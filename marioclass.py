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
    "assets/mario.png",
    "assets/marion.png",
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


class Mario:
    def __init__(self):
        self.image = pygame.transform.scale(
            pygame.image.load(sprites[1]).convert_alpha(), (20, 30)
        )
        self.jump_image = pygame.transform.scale(
            pygame.image.load(sprites[2]).convert_alpha(), (20, 30)
        )
        self.rect = self.image.get_frect(bottomleft=(50, 580))
        self.velocity = pygame.math.Vector2()

        self.fall_speed = 0
        self.jump_gravity = 0.5
        self.jump_height = 7
        self.jump_velocity = self.jump_height
        self.jumping = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        on_ladder = self.rect.collidelist(ladders) != -1
        on_bridge = self.rect.collidelist(bridges) != -1

        # horizontal movement
        self.velocity.x = MOVE_SPEED * (
            int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        )

        # vertical movement
        if on_ladder and not self.jumping:
            self.velocity.y = CLIMB_SPEED * (
                int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            )
            self.fall_speed = 0
        elif on_bridge:
            self.velocity.y = 0
            self.fall_speed = 0
        else:
            self.fall_speed += 15
            self.velocity.y = self.fall_speed

        # jump
        if keys[pygame.K_SPACE]:
            self.jumping = True

        if self.jumping:
            self.rect.y -= self.jump_velocity
            self.jump_velocity -= self.jump_gravity
            if self.jump_velocity < -self.jump_height:
                self.jumping = False
                self.jump_velocity = self.jump_height

        # keep mario on the bridge
        if not on_ladder and on_bridge and not self.jumping:
            self.rect.bottom = bridges[self.rect.collidelist(bridges)].top

        # updating mario using velocity
        self.rect.center += self.velocity * dt

    def draw(self, screen):
        if self.jumping:
            screen.blit(self.jump_image, self.rect)
        else:
            screen.blit(self.image, self.rect)


# donkeykong
dk = pygame.transform.scale(pygame.image.load(sprites[11]), (60, 80))
princess = pygame.transform.scale(pygame.image.load(sprites[13]), (30, 40))

mario = Mario()

running = True
while running:
    dt = (
        clock.tick(60) / 1000
    )  # this is used to make sure speed remains same despite changing framerate

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    mario.update(dt)

    # Draw everything
    screen.fill((20, 20, 20))

    for bridge_rect in bridges:
        screen.blit(bridge, bridge_rect)

    for ladder in ladders:
        pygame.draw.rect(screen, (139, 69, 19), ladder)

    mario.draw(screen)

    pygame.display.update()

pygame.quit()
 