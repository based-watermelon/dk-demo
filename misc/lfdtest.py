# need to add more ladders according to original DK
import random
import pygame
from sys import exit
from feature_extraction import get_state
import csv
import torch
import torch.nn as nn
pygame.init()

# ---------------------------------------------------------------------------
# Autoplay config
# ---------------------------------------------------------------------------
AUTOPLAY = True                 # False = normal keyboard play / data collection
MODEL_PATH = "bc_policy.pt"     # path to the trained checkpoint from train_bc.py
LOG_AUTOPLAY_DATA = False       # True if you still want to write a CSV while autoplaying

# Re-query the model every N frames instead of every frame, and hold that
# action in between. This MUST match the FRAME_SKIP used when the training
# data was collected -- the model has only ever seen states this sparse, so
# querying it every single frame (60Hz) asks it to be temporally smoother
# than it was trained to be, which shows up as flickery/erratic behavior
# whenever the scene changes fast (e.g. a barrel nearby).
ACTION_HOLD_FRAMES = 4

STATE_DIM = 500
N_ACTIONS = 7


class BCPolicy(nn.Module):
    """Must match the architecture in train_bc.py exactly, or load_state_dict will fail."""
    def __init__(self, input_dim=STATE_DIM, hidden=(256, 128), n_actions=N_ACTIONS, dropout=0.2):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, n_actions))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def action_to_keys(action):
    """
    Turns a predicted action int (0-6) into the same key-state dict shape
    that pygame.key.get_pressed() returns, so Mario.update() doesn't need
    to know or care whether it's being driven by a human or the model.
    """
    keys = {
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_SPACE: False,
    }
    if action == 0:      # left
        keys[pygame.K_LEFT] = True
    elif action == 1:    # right
        keys[pygame.K_RIGHT] = True
    elif action == 2:    # jump-left
        keys[pygame.K_LEFT] = True
        keys[pygame.K_SPACE] = True
    elif action == 3:    # jump-right
        keys[pygame.K_RIGHT] = True
        keys[pygame.K_SPACE] = True
    elif action == 4:    # up
        keys[pygame.K_UP] = True
    elif action == 5:    # down
        keys[pygame.K_DOWN] = True
    # action == 6 (idle) -> all False, nothing to set
    return keys


def mask_invalid_actions(logits, on_ladder_ranged, on_bridge):
    """
    Zero out actions the game engine would ignore anyway (Up/Down only do
    anything near a ladder; jump only does anything while grounded on a
    bridge), so the model can't 'waste' a prediction on a no-op. This is a
    hard rule enforced on top of the learned policy, not a training fix --
    it guarantees the agent never freezes into an invalid action even if
    the network itself hasn't fully learned the game's gating logic yet.
    """
    masked = logits.clone()
    if not on_ladder_ranged:
        masked[0, 4] = -1e9   # up
        masked[0, 5] = -1e9   # down
    if not on_bridge:
        masked[0, 2] = -1e9   # jump-left
        masked[0, 3] = -1e9   # jump-right
    return masked


# init variables
W_WIDTH = 800
W_HEIGHT = 800
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
pygame.display.set_caption("Barrel-ly Learning" + (" [AUTOPLAY]" if AUTOPLAY else ""))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None,30)

GRID_SIZE = 7
CELL_SIZE = 40
ENV_GRID = 20

sprites = [
    "assets/marion.png",
    "assets/mario.png",
    "assets/marioj.png",
    "assets/mariorev.png",
    "assets/marionrev.png",
    "assets/mariojrev.png",
    "assets/mariob.png",
    "assets/mariost.png",
    "assets/mariostrev.png",
    "assets/mariostend.png",
    "assets/mariostendrev.png",
    "assets/dk.png",
    "assets/dkb.png",
    "assets/phelp.png",
    "assets/plove.png",
    "assets/marioll.png",
    "assets/marioh.png",
    "assets/lotsofbarrels.png",
]

# constants
MOVE_SPEED = 200
CLIMB_SPEED = 150
GROUND_TOLERANCE = 4    # tolerance for standing on a bridge
LADDER_TOP_TOLERANCE = 100
LIVES = 3
MARIO_INITIAL = (50, 780)
GAME_OVER = 0
SCORE = 0
# Bridge

bridges = [
    pygame.Rect(50,780,750,20),
    pygame.Rect(0,680,750,20),
    pygame.Rect(50,580,750,20),
    pygame.Rect(0,480,750,20),
    pygame.Rect(50,380,750,20),
    pygame.Rect(0,280,750,20),
    pygame.Rect(120,180,100,20)
    
]

# Ladders
ladders = [
    pygame.Rect(700, 680, 20, 100),
    pygame.Rect(300, 580, 20, 100),
    pygame.Rect(500, 480, 20, 100),
    pygame.Rect(700, 380, 20, 100),
    pygame.Rect(200, 280, 20, 100),
    pygame.Rect(150,180,20, 100)
    
]

def canMarioClimb(ladders, rect):
    for ladder in ladders:
        ladder_center_x = ladder.centerx
        if abs(rect.centerx - ladder_center_x) <= 6:
            if ladder.top <= rect.bottom <= ladder.bottom :
                return True
    return False
def isOnBridge(bridges, mrect):
    probe = pygame.Rect(mrect.x, mrect.y, mrect.width, mrect.height + GROUND_TOLERANCE)
    return probe.collidelist(bridges) != -1

#comment out if not needed during training
def show_end_screen(text, color):
    overlay = pygame.Surface((W_WIDTH, W_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont(None, 80)
    end_text = big_font.render(text, True, color)
    text_rect = end_text.get_rect(center=(W_WIDTH // 2, W_HEIGHT // 2))
    screen.blit(end_text, text_rect)

    score_surf = font.render(f"Final Score: {SCORE}", True, "white")
    score_rect = score_surf.get_rect(center=(W_WIDTH // 2, W_HEIGHT // 2 + 60))
    screen.blit(score_surf, score_rect)

class Mario:
    def __init__(self,x,y):
        self.right_walk = []
        self.left_walk = []
        self.index = 0
        self.counter = 0
        for num in range(0,2):
            img_right = pygame.transform.scale(pygame.image.load(sprites[num]).convert_alpha(), (20, 30))
            img_left = pygame.transform.flip(img_right,True, False )
            self.right_walk.append(img_right)
            self.left_walk.append(img_left)
        self.image = self.right_walk[self.index]
        self.jump_image = pygame.transform.scale(pygame.image.load(sprites[2]).convert_alpha(), (20, 30))
        self.rjump_image = pygame.transform.scale(pygame.image.load(sprites[5]).convert_alpha(), (20, 30))
        self.death_image = pygame.transform.scale(pygame.image.load(sprites[16]).convert_alpha(), (20, 30))
        self.rect = self.image.get_frect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.is_climbing = False
        
    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.is_climbing = False
        self.index = 0
        self.counter = 0
        self.image = self.right_walk[self.index]

    def update(self, GAME_OVER, SCORE, all_barrels, action_override=None):
        walk_cooldown = 7
        dx = 0
        dy = 0
        if GAME_OVER == 0 :
            # AUTOPLAY: use the model's predicted action instead of the keyboard.
            # action_to_keys() returns a dict shaped like pygame's key-state
            # object, so every keys[pygame.K_...] lookup below works unchanged.
            if action_override is not None:
                keys = action_to_keys(action_override)
            else:
                keys = pygame.key.get_pressed()
            on_ladder_ranged = canMarioClimb(ladders, self.rect) == True
            on_bridge = isOnBridge(bridges, self.rect)
            
            if not self.is_climbing:
                if (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and on_ladder_ranged:
                    self.is_climbing = True
            else:
                if not on_ladder_ranged:
                    self.is_climbing = False

            if keys[pygame.K_SPACE] and self.jumped == False and self.is_climbing == False:
                if on_bridge == True:
                    self.vel_y = -10
                    self.jumped = True
                
            if keys[pygame.K_SPACE] == False:
                self.jumped = False

            if keys[pygame.K_LEFT] and self.is_climbing == False:
                dx -= 3 
                self.counter += 1
                self.direction = -1
            if keys[pygame.K_RIGHT] and self.is_climbing == False:
                dx += 3
                self.counter += 1
                self.direction = 1
            if keys[pygame.K_UP] and on_ladder_ranged == True:
                dy -= 1
                self.counter += 1
                self.direction = -1
            if keys[pygame.K_DOWN] and on_ladder_ranged == True:
                dy += 1
            if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.right_walk[self.index]
                if self.direction == -1:
                    self.image = self.left_walk[self.index]

            #animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.right_walk):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.right_walk[self.index]
                if self.direction == -1:
                    self.image = self.left_walk[self.index]
            if self.jumped:
                if self.direction == 1:
                    self.image = self.jump_image
                elif self.direction == -1:
                    self.image = self.rjump_image
            

            # adding gravity
            if self.is_climbing == False and on_ladder_ranged == False:
                self.vel_y += 0.75
                if self.vel_y > 10:
                    self.vel_y = 10
                dy += self.vel_y
            
            # check for collisions
            if on_bridge == True and self.is_climbing == False :
                for bridge in bridges:
                    #y direction
                    if bridge.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                        #check if below block (jumping)
                        if self.vel_y < 0:
                            dy = bridge.bottom - self.rect.top
                        # check if collision on the block (falling)
                        elif self.vel_y >= 0:
                            dy = bridge.top - self.rect.bottom
                            self.vel_y = 0

            # check for collision with barrels
            if pygame.sprite.spritecollide(self, all_barrels, False):
                GAME_OVER = -1


            # update player coords  
            self.rect.x += dx
            self.rect.y += dy
            # border boundaries
            if self.rect.bottom > W_HEIGHT:
                self.rect.bottom = W_HEIGHT
                dy = 0
            if self.rect.left < 0:
                self.rect.left = 0
                dx = 0
            if self.rect.right > W_WIDTH:
                self.rect.right = W_WIDTH
                dx = 0

            #Scoring system
            for barrel in all_barrels:
                if (
                    self.jumped
                    and not barrel.scored
                    and abs(self.rect.centerx - barrel.rect.centerx) < 35
                    and self.rect.bottom < barrel.rect.top + 10
                ):
                    SCORE += 100
                    barrel.scored = True
            



        else:
            self.image = self.death_image
        #draw mario on screen
        screen.blit(self.image, self.rect)
        return GAME_OVER, SCORE

class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("assets/barrel.jpg"), (20,20))
        self.image.set_colorkey("black")
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_frect()
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0
        self.move_speed = 200
        self.climb_speed = 150
        self.ladder_decision = None
        self.on_ladder = False

        self.scored = False
    
    def update(self):
        self.gravity = 2  # Simulate gravity for the barrel
        self.check_collision_with_ladders()
        if not self.on_ladder:
            self.check_collision_with_bridges()

    def check_collision_with_bridges(self):
        probe = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height + GROUND_TOLERANCE)
        bridge_index = probe.collidelist(bridges)        
        if bridge_index == -1:
            self.rect.y += self.gravity  # Simulate gravity when not on a bridge
        else:
            self.rect.bottom = bridges[bridge_index].top
            if bridge_index%2 == 0:  # If on an even-indexed bridge, move left
                self.rect.x -= 2.5
            else:  # If on an odd-indexed bridge, move right
                self.rect.x += 2.5
            

    def check_collision_with_ladders(self):
        ladder_index = -1
        for i, ladder in enumerate(ladders):
            if canMarioClimb([ladder], self.rect):
                ladder_index = i
                break

        if ladder_index == -1:
            self.ladder_decision = None
            self.on_ladder = False
            return

        if self.ladder_decision is None:
            self.ladder_decision = ladder_index if random.random() < 0.5 else -1

        if self.ladder_decision == ladder_index:
            self.on_ladder = True
            self.rect.y += 1
            self.rect.x = ladders[ladder_index].x
            if self.rect.bottom >= ladders[ladder_index].bottom:
                self.on_ladder = False
                self.ladder_decision = None
        else:
            self.on_ladder = False
         
def get_action():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and keys[pygame.K_SPACE]:
        return 2      

    elif keys[pygame.K_RIGHT] and keys[pygame.K_SPACE]:
        return 3      

    elif keys[pygame.K_LEFT]:
        return 0      

    elif keys[pygame.K_RIGHT]:
        return 1      

    elif keys[pygame.K_UP]:
        return 4      

    elif keys[pygame.K_DOWN]:
        return 5      

    return 6          # stand still

def get_reward(previous_score, current_score, previous_lives, current_lives, game_over):
    reward = 0

    if current_score > previous_score:
        reward += current_score - previous_score

    if current_lives < previous_lives:
        reward -= 100

    if game_over == 1:
        reward += 1000

    return reward

# donkeykong
dk = pygame.transform.scale(pygame.image.load(sprites[11]), (60, 80))
dkb = pygame.transform.scale(pygame.image.load(sprites[12]), (60, 80))
dkbr = pygame.transform.flip(dkb,True, False )
lots_of_barrels = pygame.transform.scale(pygame.image.load(sprites[17]), (50, 80))
princess_help = pygame.transform.scale(pygame.image.load(sprites[13]), (45, 40))
princess_help.set_colorkey("black")
princess_love = pygame.transform.scale(pygame.image.load(sprites[14]), (45, 40))
princess_love.set_colorkey("black")
princess_rect = princess_help.get_frect(topleft = (130,140))
princess_image = princess_help
game_won = False
dk_throwing = False


mario = Mario(*MARIO_INITIAL)

all_barrels = pygame.sprite.Group()

SPAWN_BARREL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_BARREL_EVENT, random.randint(2000, 5000)) 

# --- load the trained policy for autoplay ---------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
policy = None
if AUTOPLAY:
    policy = BCPolicy().to(device)
    policy.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    policy.eval()
    print(f"Autoplay ON. Loaded {MODEL_PATH} on {device}.")
# ---------------------------------------------------------------------------

if LOG_AUTOPLAY_DATA:
    csv_file = open("autoplay_log.csv", "w", newline="")
    writer = csv.writer(csv_file)
    header = [f"s{i}" for i in range(500)] + ["action", "reward"] + [f"next_s{i}" for i in range(500)]
    writer.writerow(header)

previous_score = SCORE
previous_lives = LIVES
autoplay_frame_count = 0
held_action = 6  # start idle


running = True
while running:
    lives_text=font.render(f"Lives: {LIVES}", True, "white")
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if LOG_AUTOPLAY_DATA:
                csv_file.close()
            pygame.quit()
            exit()
        
        if event.type == SPAWN_BARREL_EVENT:
            new_barrel = Barrel(100,280)  # Spawn barrel at a fixed position (100, 100)
            all_barrels.add(new_barrel)

            pygame.time.set_timer(SPAWN_BARREL_EVENT,random.randint(2000, 5000))
            dk_throwing = True
        if event.type != SPAWN_BARREL_EVENT:
            dk_throwing = False
    

    # Draw everything
    screen.fill((20, 20, 20))
    

    for bridge_rect in bridges:
        pygame.draw.rect(screen, (255,0,0), bridge_rect)

    for ladder in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder)

    
    screen.blit(princess_image, princess_rect)

    if dk_throwing:
        screen.blit(dkb, (50, 200))
    else:
        screen.blit(dk, (50, 200))
    screen.blit(lots_of_barrels, (5, 200))

    state = get_state(mario, all_barrels, ladders,screen, CELL_SIZE, GRID_SIZE, ENV_GRID)
    state.extend([int(mario.is_climbing),int(canMarioClimb(ladders,mario.rect))])

    # decide the action: model prediction if autoplaying, keyboard otherwise.
    # Only re-predict every ACTION_HOLD_FRAMES frames (matching training's
    # FRAME_SKIP) -- holding the action in between avoids flickery decisions
    # in fast-changing moments like a barrel entering the vision grid.
    if AUTOPLAY:
        on_ladder_ranged = canMarioClimb(ladders, mario.rect)
        on_bridge = isOnBridge(bridges, mario.rect)

        if autoplay_frame_count % ACTION_HOLD_FRAMES == 0:
            with torch.no_grad():
                state_t = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
                logits = policy(state_t)
                logits = mask_invalid_actions(logits, on_ladder_ranged, on_bridge)
                held_action = logits.argmax(dim=1).item()
        autoplay_frame_count += 1
        action = held_action
    else:
        action = get_action()


    if GAME_OVER in (0, -1):
            GAME_OVER, SCORE = mario.update(
                GAME_OVER, SCORE, all_barrels,
                action_override=action if AUTOPLAY else None,
            )
            if GAME_OVER == 0:
                all_barrels.update()
            all_barrels.draw(screen)

               

            if not game_won and GAME_OVER == 0 and mario.rect.colliderect(princess_rect):
                princess_image = princess_love
                game_won = True
                SCORE += 1000
                GAME_OVER = 1

            if GAME_OVER == -1:
                LIVES -= 1
                if LIVES <= 0:
                    GAME_OVER = -2       # terminal game-over state
                else:
                    mario.reset(*MARIO_INITIAL)
                    all_barrels.empty()
                    pygame.time.set_timer(SPAWN_BARREL_EVENT, random.randint(2000, 5000))
                    GAME_OVER = 0

            if LOG_AUTOPLAY_DATA:
                next_state = get_state(
                                    mario,
                                    all_barrels,
                                    ladders,
                                    screen,
                                    CELL_SIZE,
                                    GRID_SIZE,
                                    ENV_GRID,
                                )
                next_state.extend([
                    int(mario.is_climbing),
                    int(canMarioClimb(ladders, mario.rect))
                ])
                reward = get_reward(
                                        previous_score,
                                        SCORE,
                                        previous_lives,
                                        LIVES,
                                        GAME_OVER,
                                    )
                writer.writerow(state + [action, reward] + next_state)

            previous_score = SCORE
            previous_lives = LIVES

    if GAME_OVER == -2:
            show_end_screen("GAME OVER", "red")
    elif GAME_OVER == 1:
            show_end_screen("YOU WIN!", "gold")
    else:
            screen.blit(lives_text, (700, 10))
            score_text = font.render(f"Score: {SCORE}", True, "white")
            screen.blit(score_text, (10, 10))

    clock.tick(60)
    pygame.display.update()