import pygame
from sys import exit


pygame.init()


screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Barrel-ly Learning")
clock = pygame.time.Clock()


# Bridge
bridge = pygame.Surface((750, 20))
bridge.fill((255, 0, 0))


bridge_rect1 = bridge.get_rect(bottomright=(800, 600))
bridge_rect2 = bridge.get_rect(topleft=(0, 500))
bridge_rect3 = bridge.get_rect(topright=(800, 420))
bridge_rect4 = bridge.get_rect(topleft=(0, 340))
bridge_rect5 = bridge.get_rect(topright=(800, 260))
bridge_rect6 = bridge.get_rect(topleft=(0, 180))


bridges = [bridge_rect1, bridge_rect2, bridge_rect3, bridge_rect4, bridge_rect5, bridge_rect6]


# Mario
mario = pygame.Surface((30, 40))
mario.fill((0, 0, 255))
mario_rect = mario.get_rect(bottomleft=(50, 580))
mario_gravity = 0


# Ladders
ladders = [
   pygame.Rect(100, 500, 20, 100),
   pygame.Rect(300, 420, 20, 100),
   pygame.Rect(500, 340, 20, 100),
   pygame.Rect(700, 260, 20, 100)
]


running = True
while running:
   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           pygame.quit()
           exit()


       # Jump
       if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_SPACE and mario_rect.collidelist(bridges) != -1:
               mario_gravity = -15


   # Continuous movement
   keys = pygame.key.get_pressed()


   if keys[pygame.K_LEFT]:
       mario_rect.x -= 5


   if keys[pygame.K_RIGHT]:
       mario_rect.x += 5


   # On ladder
   on_ladder = mario_rect.collidelist(ladders) != -1


   if on_ladder:
       mario_gravity = 0


       if keys[pygame.K_UP]:
           mario_rect.y -= 5


       if keys[pygame.K_DOWN]:
           mario_rect.y += 5
   else:
       mario_gravity += 1
       mario_rect.y += mario_gravity


   # Keep mario on the bridge
   if mario_rect.collidelist(bridges) != -1:
       mario_rect.bottom = bridges[mario_rect.collidelist(bridges)].top
       mario_gravity = 0


   # Draw everything
   screen.fill((20, 20, 20))


   for bridge_rect in bridges:	
       screen.blit(bridge, bridge_rect)


   for ladder in ladders:
       pygame.draw.rect(screen, (139, 69, 19), ladder)


   screen.blit(mario, mario_rect)


   pygame.display.update()
   clock.tick(60)


pygame.quit()

