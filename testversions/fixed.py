import pygame
import random

class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/mario.png").convert_alpha()
        self.image.set_colorkey((0, 0, 0))  # Set white as the transparent color
        self.rect = self.image.get_rect(bottomleft=(50, 580))
        self.gravity = 0

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and self.rect.collidelist(bridges):
            self.gravity = -5
    
    def apply_gravity(self):
        on_ladder = self.rect.collidelist(ladders) != -1
        
        if on_ladder:
            self.gravity = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.rect.y -= 2
            if keys[pygame.K_DOWN]:
                self.rect.y += 2
        else:
            self.gravity += 1
            self.rect.y += self.gravity

        bridge = self.rect.collidelist(bridges) != -1
        if bridge and self.gravity >= 0: 
            self.rect.bottom = bridges[self.rect.collidelist(bridges)].top
            self.gravity = 0
    
    def update(self):
        self.player_input()
        self.apply_gravity()
        #self.animation_state()

class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20)) #replace with actual barrel image
        self.image.fill((139, 69, 19))  # Brown color for the barrel
        self.rect = self.image.get_rect(topleft=(x, y))

    #def animation_state(self):
    
    def update(self):
        self.gravity = 1  # Simulate gravity for the barrel
        self.check_collision_with_ladders()
        self.check_collision_with_bridges()
        #self.destroy_if_off_screen()
    
    def check_collision_with_bridges(self):
        bridge_index = self.rect.collidelist(bridges)
        if bridge_index == -1:
            self.rect.y += self.gravity  # Simulate gravity when not on a bridge
        else:
            if bridge_index%2 == 0:  # If on an even-indexed bridge, move left
                self.rect.x -= 5
            else:  # If on an odd-indexed bridge, move right
                self.rect.x += 5
       
    def check_collision_with_ladders(self):
        ladder_index = self.rect.collidelist(ladders)
        if ladder_index != -1:
            self.rect.y += 1  # Adjust position to simulate falling down the ladder
            self.rect.x = ladders[ladder_index].x  # Keep the barrel aligned with the ladder

def collision_sprite(mario, all_barrels):
    if pygame.sprite.spritecollide(mario.sprite, all_barrels, False):
        return True
    else:
        return False
   

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Barrel-ly Learning")
clock = pygame.time.Clock()

# Bridges
bridges = [
    pygame.Rect(50,580,750,20),
    pygame.Rect(0,500,750,20),
    pygame.Rect(50,420,750,20),
    pygame.Rect(0,340,750,20),
    pygame.Rect(50,260,750,20),
    pygame.Rect(0,340,750,20)
]

"""
bridge = pygame.Surface((750, 20))
bridge.fill((255, 0, 0))

bridge_rect1 = bridge.get_rect(bottomright=(800, 600))
bridge_rect2 = bridge.get_rect(topleft=(0, 500))
bridge_rect3 = bridge.get_rect(topright=(800, 420))
bridge_rect4 = bridge.get_rect(topleft=(0, 340))
bridge_rect5 = bridge.get_rect(topright=(800, 260))
bridge_rect6 = bridge.get_rect(topleft=(0, 180))

bridges = [bridge_rect1, bridge_rect2, bridge_rect3, bridge_rect4, bridge_rect5, bridge_rect6]
"""

# Ladders
ladders = [
    pygame.Rect(100, 500, 20, 100),
    pygame.Rect(300, 420, 20, 100),
    pygame.Rect(500, 340, 20, 100),
    pygame.Rect(700, 260, 20, 100)
]

#Groups
mario = pygame.sprite.GroupSingle()
mario.add(Mario())
all_barrels = pygame.sprite.Group()


# Timer for spawning barrels
SPAWN_BARREL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_BARREL_EVENT, random.randint(1000,3000))  # Spawn a barrel every 2 seconds

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == SPAWN_BARREL_EVENT:
            new_barrel = Barrel(100, 100)
            all_barrels.add(new_barrel)
        if collision_sprite(mario, all_barrels):
            print("Game Over")
            pygame.quit()
            exit()
        
    screen.fill((20, 20, 20))

    for bridge_rect in bridges:
        #screen.blit(bridge, bridge_rect)
        pygame.draw.rect(screen, (250, 0, 0), bridge_rect)  # Draw Bridges
    for ladder_rect in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder_rect)  # Draw ladders

    mario.update()
    all_barrels.update()

    mario.draw(screen)
    all_barrels.draw(screen)

    pygame.display.update()
    clock.tick(60)

