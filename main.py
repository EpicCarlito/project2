# AI For Game Programming
# Ms. Qiu - Period 7

import asyncio
import math
import os
import random

import pygame


async def main():
    pygame.init()
    WIDTH, HEIGHT = 500, 800
    SPRITE_SIZE = 16

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Import Images

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    zombie_sprite = pygame.image.load(
        os.path.join(SCRIPT_DIR, "assets/test.jpeg")
    ).convert_alpha()
    zombie_sprite = pygame.transform.scale(zombie_sprite, (SPRITE_SIZE, SPRITE_SIZE))

    running = True

    # Crowd Class
    # Handles all the angles and velocities of the characters
    class Crowd:
        def __init__(self, characters):
            self.characters = characters
            self.angle = 0
            self.velocity = pygame.Vector2(0, 0)

    class Character:
        def __init__(self, x, y):
            self.position = pygame.Vector2(x, y)
            self.angle = 90
            self.velocity = pygame.Vector2(0, 0)

        def get_forward_vector(self):
            radians = math.radians(self.angle)
            forward = pygame.Vector2(math.cos(radians), -math.sin(radians))

            return forward

    # Enemy Class
    class Enemy(Character):
        def __init__(self, x, y):
            super().__init__(x)
            super().__init__(y)
            self.radius = 20
            self.state = "PATROL"

            self.distance = 0
            self.dot = 0

            self.fire_timer = 0

        def update(self):
            keys = pygame.key.get_pressed()

    # Player Class
    class Player(Character):
        def __init__(self, x, y):
            super().__init__(x, y)

        def update(self):
            leftX, rightX = 50, WIDTH - 50
            keys = pygame.key.get_pressed()

            forward = self.get_forward_vector()
            self.position += self.velocity
            # if (self.position.x < leftX or self.position.x > rightX) return
            # Block the following code

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle += 5

        def draw(self):
            player_rect = pygame.Rect(
                self.position.x, self.position.y, SPRITE_SIZE, SPRITE_SIZE
            )
            screen.blit(zombie_sprite, player_rect)

    class Missile:
        def __init__(self, start_position, direction):
            self.position = pygame.Vector2(start_position)
            self.velocity = direction * 3

        def update(self):
            self.position += self.velocity

        def draw(self):
            pygame.draw.circle(
                screen,
                "yellow",
                (int(self.position.x + 8), int(self.position.y + 24)),
                2,
            )

    # Game Loop

    missiles = []

    player = Player(WIDTH / 2, HEIGHT - HEIGHT / 4)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    forward = player.get_forward_vector()
                    missile_start = player.position + forward * 24
                    new_missile = Missile(missile_start, forward)
                    missiles.append(new_missile)

        screen.fill((20, 24, 40))

        # Code Logic

        for missile in missiles:
            missile.update()

        # Render Components

        player.draw()
        
        for missile in missiles:
            missile.draw()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
