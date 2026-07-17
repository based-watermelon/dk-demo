

import pygame
from sys import exit


pygame.init()

#init variables
W_WIDTH=800
W_HEIGHT=600
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
pygame.display.set_caption("Barrel-ly Learning")
clock = pygame.time.Clock()

sprites=[
    "assets/mario.png","assets/marion.png","assets/marioj.png",
    "assets/mariorev.png","assets/marionrev.png","assets/mariojrev.png",
    "assets/mariob.png","assets/mariost.png","assets/mariostrev.png",
    "assets/mariostend.png","assets/mariostendrev.png","assets/dk.png",
    "assets/dkb.png","assets/phelp.png","assets/plove.png",
    "assets/marioll.png","assets/marioh.png","assets/lotsofbarrels.png"]

#constants
MOVE_SPEED=200
CLIMB_SPEED=150

# Bridge
bridge = pygame.Surface((750, 20))
bridge.fill((255, 0, 0))


bridge_rect1 = bridge.get_frect(bottomright=(W_WIDTH, W_HEIGHT))
bridge_rect2 = bridge.get_frect(topleft=(0, 500))
bridge_rect3 = bridge.get_frect(topright=(800, 420))
bridge_rect4 = bridge.get_frect(topleft=(0, 340))
bridge_rect5 = bridge.get_frect(topright=(800, 260))
bridge_rect6 = bridge.get_frect(topleft=(0, 180))


bridges = [bridge_rect1, bridge_rect2, bridge_rect3, bridge_rect4, bridge_rect5, bridge_rect6]

#Characters
    # Mario
    #mario = pygame.Surface((30, 40))
mario = pygame.transform.scale(pygame.image.load(sprites[1]).convert_alpha(),(30,40))
mario_jump = pygame.transform.scale(pygame.image.load(sprites[2]).convert_alpha(),(30,40))
mario_rect = mario.get_frect(bottomleft=(50, 580))
mario_velocity = pygame.math.Vector2()

fall_speed = 0
jump_gravity = 0.5
jump_height = 7
jump_velocity = jump_height
jumping = False


    #donkeykong
dk = pygame.transform.scale(pygame.image.load(sprites[11]),(60,80))
princess = pygame.transform.scale(pygame.image.load(sprites[13]),(30,40))


#functions


# Ladders
ladders = [
   pygame.Rect(700, 500, 20, 80),
   pygame.Rect(300, 420, 20, 80),
   pygame.Rect(500, 340, 20, 80),
   pygame.Rect(700, 260, 20, 80),
   pygame.Rect(200, 180, 20, 80)
]


running = True
while running:
    dt=clock.tick(60)/1000      # this is used to make sure speed remains same despite changing framerate
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

   # input

    keys = pygame.key.get_pressed()

    on_ladder = mario_rect.collidelist(ladders) != -1
    on_bridge = mario_rect.collidelist(bridges) != -1

    #horizontal movement
    
    mario_velocity.x= MOVE_SPEED*(int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) 


   #vertical movement


        # On ladder

    if on_ladder and not jumping:
        mario_velocity.y = CLIMB_SPEED*(int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]))
        fall_speed=0

    elif on_bridge:
        mario_velocity.y=0
        fall_speed=0
    else:
        fall_speed+=15
        mario_velocity.y = fall_speed

   # Keep mario on the bridge
    if not on_ladder and on_bridge and not jumping:
        mario_rect.bottom = bridges[mario_rect.collidelist(bridges)].top

    #jump
    if keys[pygame.K_SPACE]:
        jumping = True

    if jumping:
        mario_rect.y -= jump_velocity
        jump_velocity -= jump_gravity
        if jump_velocity <= -jump_height:
            jumping=False
            jump_velocity=jump_height
          
        
        
    #updating mario using velocity
    mario_rect.center += mario_velocity*dt

   # Draw everything
    screen.fill((20, 20, 20))


    for bridge_rect in bridges:	
        screen.blit(bridge, bridge_rect)


    for ladder in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder)

    
    if jumping: screen.blit(mario_jump,mario_rect) 
    else:   screen.blit(mario, mario_rect)


    pygame.display.update()
    


pygame.quit()

