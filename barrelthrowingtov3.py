# Bridges and ladders need to be updated, larger gaps
# fix that snap issue by introducing a variable similar to what u had in the old version
# integrate barrels
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
        self.rect = self.image.get_frect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.is_climbing = False
        

    def update(self):
        keys = pygame.key.get_pressed()
        on_ladder_ranged = canMarioClimb(ladders, self.rect) == True
        on_bridge = isOnBridge(bridges, self.rect)
        
        if not self.is_climbing:
            if (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and on_ladder_ranged:
                self.is_climbing = True
        else:
            if not on_ladder_ranged:
                self.is_climbing = False
        
        

        walk_cooldown = 7
        dx = 0
        dy = 0
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
        # if not on_bridge:
        #     if self.direction == 1:
        #         self.image = self.jump_image
        #     elif self.direction == -1:
        #         self.image = self.rjump_image
        

        # adding gravity
        if self.is_climbing == False and on_ladder_ranged == False:
            self.vel_y += 0.85
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
        
        # check for collisions
        #x direction
        # for ladder in ladders:
        #     if ladder.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
        #         dx = 0
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
        
        #draw mario on screen
        screen.blit(self.image, self.rect)

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
    
    def update(self):
        self.gravity = 2  # Simulate gravity for the barrel
        #self.check_collision_with_ladders()
        self.check_collision_with_bridges()

    def check_collision_with_bridges(self):
        bridge_index = self.rect.collidelist(bridges)
        if bridge_index == -1:
            self.rect.y += self.gravity  # Simulate gravity when not on a bridge
        else:
            if bridge_index%2 == 0:  # If on an even-indexed bridge, move left
                self.rect.x -= 3
            else:  # If on an odd-indexed bridge, move right
                self.rect.x += 3

    def check_collision_with_ladders(self):
        ladder_index = self.rect.collidelist(ladders)
        if ladder_index != -1 :  # Occasionally let a barrel tumble down a ladder
            self.rect.y += 1  # Adjust position to simulate falling down the ladder
            self.rect.x = ladders[ladder_index].x



# donkeykong
dk = pygame.transform.scale(pygame.image.load(sprites[11]), (60, 80))
princess = pygame.transform.scale(pygame.image.load(sprites[13]), (45, 40))

mario = Mario(50,580)

all_barrels = pygame.sprite.Group()




SPAWN_BARREL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_BARREL_EVENT, random.randint(2000, 4000)) 


running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == SPAWN_BARREL_EVENT:
            new_barrel = Barrel(100,100)  # Spawn barrel at a fixed position (100, 100)
            all_barrels.add(new_barrel)

            pygame.time.set_timer(SPAWN_BARREL_EVENT,random.randint(2000, 4000))

    

    # Draw everything
    screen.fill((20, 20, 20))
    

    for bridge_rect in bridges:
        screen.blit(bridge, bridge_rect)

    for ladder in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder)

    screen.blit(dk, (30, 100))
    screen.blit(princess, (110, 140))
        
    mario.update()
    all_barrels.update()
    all_barrels.draw(screen)

    clock.tick(60)
    pygame.display.update()

pygame.quit()
 