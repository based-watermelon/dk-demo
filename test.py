import random

import pygame
from sys import exit

class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.states =["assets/mario.png","assets/marioj.png"]
        self.index = 0
        self.image = pygame.transform.scale(pygame.image.load(self.states[self.index]).convert_alpha(),(20,30))
        self.rect = self.image.get_frect(bottomleft=(50, 580))

        self.velocity = pygame.math.Vector2()

        self.gravity = 0
        self.move_speed = 200
        self.climb_speed = 150

        self.jumping = False

        self.crossed = set()
        self.points = 0


    def player_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = self.move_speed * (int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]))

        if keys[pygame.K_SPACE] and not self.jumping:
            if self.rect.collidelist(bridges) != -1:
                self.gravity = -5
                self.jumping = True
    
    def apply_gravity(self,dt):
        keys = pygame.key.get_pressed()
        on_ladder = self.rect.collidelist(ladders) != -1
        if on_ladder:
            self.velocity.y = self.climb_speed * (
                int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            ) * dt
        else:
            self.gravity += 0.4
            self.velocity.y = self.gravity

        bridge = self.rect.collidelist(bridges) != -1
        if bridge and self.gravity >= 0: 
            self.rect.bottom = bridges[self.rect.collidelist(bridges)].top
            self.gravity = 0
            self.velocity.y = 0
            self.jumping = False
    
    def collision_sprite(self,all_barrels):
        if pygame.sprite.spritecollideany(self, all_barrels):
            print("Game Over")
            pygame.quit()
            exit()

    def score(self,all_barrels):
        for barrel in all_barrels:
                if self.jumping:
                    # Check if over the obstacle
                    if self.rect.right > barrel.rect.left and self.rect.left < barrel.rect.right:
                        
                        # player over obstacle
                        #if self.rect.bottom <= barrel.rect.top:
                            
                            # fully passed the obstacle's right edge
                            if self.rect.left > barrel.rect.left and barrel not in self.crossed:
                                self.crossed.add(barrel)
                                self.points += 100
                                print("Successfully jumped over an obstacle!, points= " ,self.points)

        
                        
        
    def update(self,dt,all_barrels):
        self.player_input()
        self.apply_gravity(dt)
        self.rect.centerx += self.velocity.x * dt
        self.rect.centery += self.velocity.y
        self.collision_sprite(all_barrels)
        self.score(all_barrels)

        #self.animation_state()
    

class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((17, 17)) #replace with actual barrel image
        self.image.fill((139, 69, 19))  # Brown color for the barrel
        self.rect = self.image.get_rect(topleft=(x, y))

        self.velocity = pygame.math.Vector2()

        self.gravity = 0
        self.move_speed = 200
        self.climb_speed = 150

    #def animation_state(self):
    """
    def spawn_barrel():
        x = 800
        y = random.randint(100, 500)
        new_barrel = Barrel(x, y)
        all_barrels.add(new_barrel)
    """
    def update(self):
        self.gravity = 1  # Simulate gravity for the barrel
        #self.check_collision_with_ladders()
        self.check_collision_with_bridges()
        
        #self.destroy_if_off_screen()
    
    def check_collision_with_bridges(self):
        bridge_index = self.rect.collidelist(bridges)
        if bridge_index == -1:
            self.rect.y += self.gravity  # Simulate gravity when not on a bridge
        else:
            if bridge_index%2 == 0:  # If on an even-indexed bridge, move left
                self.rect.x -= 3.5
            else:  # If on an odd-indexed bridge, move right
                self.rect.x += 3.5
       
    def check_collision_with_ladders(self):
        ladder_index = self.rect.collidelist(ladders)
        if ladder_index != -1 :  # Occasionally let a barrel tumble down a ladder
            self.rect.y += 1  # Adjust position to simulate falling down the ladder
            self.rect.x = ladders[ladder_index].x  # Keep the barrel aligned with the ladder


    


pygame.init()

#init variables
W_WIDTH=800
W_HEIGHT=600
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
pygame.display.set_caption("Barrel-ly Learning")
clock = pygame.time.Clock()
"""
sprites=[
    "assets/mario.png","assets/marion.png","assets/marioj.png",
    "assets/mariorev.png","assets/marionrev.png","assets/mariojrev.png",
    "assets/mariob.png","assets/mariost.png","assets/mariostrev.png",
    "assets/mariostend.png","assets/mariostendrev.png","assets/dk.png",
    "assets/dkb.png","assets/phelp.png","assets/plove.png",
    "assets/marioll.png","assets/marioh.png","assets/lotsofbarrels.png"]
"""
#Groups
mario = pygame.sprite.GroupSingle()
mario.add(Mario())
all_barrels = pygame.sprite.Group()

# Timer for spawning barrels
SPAWN_BARREL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_BARREL_EVENT, random.randint(1000, 3000))  # Spawn a barrel every 1-3 seconds


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
"""
    #donkeykong
dk = pygame.transform.scale(pygame.image.load(sprites[11]),(60,80))
princess = pygame.transform.scale(pygame.image.load(sprites[13]),(30,40))
"""

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

        if event.type == SPAWN_BARREL_EVENT:
            new_barrel = Barrel(100,100)  # Spawn barrel at a fixed position (100, 100)
            all_barrels.add(new_barrel)
        

    # Draw everything
    screen.fill((20, 20, 20))

    for bridge_rect in bridges:	
        screen.blit(bridge, bridge_rect)

    for ladder in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder)
    

    mario.update(dt,all_barrels)
    all_barrels.update()

    mario.draw(screen)
    all_barrels.draw(screen)

    pygame.display.update()

pygame.quit()

