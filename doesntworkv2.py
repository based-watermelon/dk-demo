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

def canMarioClimb(ladders, mrect):
    for ladder in ladders:
        # ladder_center_x = ladder.centerx
        # if abs(center - ladder_center_x) <= 5:
        if ladder.left <= mrect.centerx <= ladder.right:
            if (abs(mrect.bottom - ladder.bottom) < 10) or (abs(mrect.bottom - ladder.top)) < 10:
                return ladder
    return None 


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
        self.is_climbing = False
        self.current_ladder = None
        self.direction = 0
        
        
    def update(self):
        keys = pygame.key.get_pressed()
        # on_ladder_ranged = self.rect.collidelist(ladders) != -1 and canMarioClimb(ladders, self.rect)
        on_bridge = self.rect.collidelist(bridges) != -1

        #checking if climbing
        if not self.is_climbing:
            ladderc = canMarioClimb(ladders, self.rect)

            if ladderc and keys[pygame.K_UP]:
                self.is_climbing = True
                self.current_ladder = ladderc
                if self.rect.bottom <= ladderc.top + 5:
                    self.is_climbing = False

            elif ladderc and keys[pygame.K_DOWN]:
                self.is_climbing = True
                self.current_ladder = ladderc
                if self.rect.bottom >= ladderc.bottom - 5:
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
            dx -= 5 
            self.counter += 1
            self.direction = -1
        if keys[pygame.K_RIGHT] and self.is_climbing == False:
            dx += 5
            self.counter += 1
            self.direction = 1
        if keys[pygame.K_UP] and self.is_climbing == True:
            dy -= 3
            self.counter += 1
            self.direction = -1
        if keys[pygame.K_DOWN] and self.is_climbing == True:
            dy += 3
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
        if self.is_climbing == False:
            self.vel_y += 0.85
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
        
        # check for collisions
        #x direction
        # for ladder in ladders:
        #     if ladder.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
        #         dx = 0
        if on_bridge == True and self.is_climbing == False:
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

        if self.rect.bottom > W_HEIGHT:
            self.rect.bottom = W_HEIGHT
            dy = 0
        
        #draw mario on screen
        screen.blit(self.image, self.rect)

        



        




# donkeykong
dk = pygame.transform.scale(pygame.image.load(sprites[11]), (60, 80))
princess = pygame.transform.scale(pygame.image.load(sprites[13]), (30, 40))

mario = Mario(50,580)

running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    

    # Draw everything
    screen.fill((20, 20, 20))
    

    for bridge_rect in bridges:
        screen.blit(bridge, bridge_rect)

    for ladder in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder)

    screen.blit(dk, (30, 100))
    screen.blit(princess, (110, 140))
        
    mario.update()

    clock.tick(60)
    pygame.display.update()

pygame.quit()
 