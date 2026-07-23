# need to add more ladders according to original DK
import random
import pygame
from sys import exit


pygame.init()

# init variables
W_WIDTH = 800
W_HEIGHT = 600
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
pygame.display.set_caption("Barrel-ly Learning")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None,30)

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
MARIO_INITIAL = (50, 580)
GAME_OVER = 0
# Bridge
bridge = pygame.Surface((750, 20))
bridge.fill((255, 0, 0))


bridge_rect1 = bridge.get_frect(bottomright=(W_WIDTH, W_HEIGHT))
bridge_rect2 = bridge.get_frect(topleft=(0, 500))
bridge_rect3 = bridge.get_frect(topright=(800, 420))
bridge_rect4 = bridge.get_frect(topleft=(0, 340))
bridge_rect5 = bridge.get_frect(topright=(800, 260))
bridge_rect6 = bridge.get_frect(topleft=(0, 180))

bridges = [
    bridge_rect1,
    bridge_rect2,
    bridge_rect3,
    bridge_rect4,
    bridge_rect5,
    bridge_rect6,
]

# Ladders
ladders = [
    pygame.Rect(700, 500, 20, 80),
    pygame.Rect(300, 420, 20, 80),
    pygame.Rect(500, 340, 20, 80),
    pygame.Rect(700, 260, 20, 80),
    pygame.Rect(200, 180, 20, 80),
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

    def update(self, GAME_OVER):
        walk_cooldown = 7
        dx = 0
        dy = 0
        if GAME_OVER == 0 :
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
            
        else:
            self.image = self.death_image
        #draw mario on screen
        screen.blit(self.image, self.rect)
        return GAME_OVER

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
    
    def update(self):
        self.gravity = 2  # Simulate gravity for the barrel
        #self.check_collision_with_ladders()
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
                self.rect.x -= 3
            else:  # If on an odd-indexed bridge, move right
                self.rect.x += 3
            

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
         



# donkeykong
dk = pygame.transform.scale(pygame.image.load(sprites[11]), (60, 80))
dkb = pygame.transform.scale(pygame.image.load(sprites[12]), (60, 80))
dkbr = pygame.transform.flip(dkb,True, False )
lots_of_barrels = pygame.transform.scale(pygame.image.load(sprites[17]), (50, 80))
princess = pygame.transform.scale(pygame.image.load(sprites[13]), (45, 40))
dk_throwing = False


mario = Mario(*MARIO_INITIAL)

all_barrels = pygame.sprite.Group()

SPAWN_BARREL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_BARREL_EVENT, random.randint(2000, 5000)) 

running = True
while running:
    lives_text=font.render(f"Lives: {LIVES}", True, "white")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == SPAWN_BARREL_EVENT:
            new_barrel = Barrel(100,100)  # Spawn barrel at a fixed position (100, 100)
            all_barrels.add(new_barrel)

            pygame.time.set_timer(SPAWN_BARREL_EVENT,random.randint(2000, 5000))
            dk_throwing = True
        if event.type != SPAWN_BARREL_EVENT:
            dk_throwing = False
    

    # Draw everything
    screen.fill((20, 20, 20))
    

    for bridge_rect in bridges:
        screen.blit(bridge, bridge_rect)

    for ladder in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder)

    
    screen.blit(princess, (150, 140))

    if dk_throwing:
        screen.blit(dkb, (50, 100))
    else:
        screen.blit(dk, (50, 100))
    screen.blit(lots_of_barrels, (5, 100))
        
    GAME_OVER = mario.update(GAME_OVER)
    if GAME_OVER == 0:
        all_barrels.update()
    all_barrels.draw(screen)
    


    if GAME_OVER == -1 :
        LIVES -= 1
        if LIVES <= 0:
            pygame.quit()
            exit()
        else:
            mario.reset(*MARIO_INITIAL)
            all_barrels.empty()
            pygame.time.set_timer(SPAWN_BARREL_EVENT, random.randint(2000, 5000))
            GAME_OVER = 0
    screen.blit(lives_text, (700,10))

    clock.tick(60)
    pygame.display.update()

pygame.quit()
 