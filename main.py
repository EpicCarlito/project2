# AI For Game Programming
# Ms. Qiu - Period 7

import asyncio
import math
import os

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
    # The position and player_rect are not synced
    class Player(Character):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.player_rect = pygame.Rect(
                self.position.x, self.position.y, SPRITE_SIZE, SPRITE_SIZE
            )

        def update(self):
            leftX, rightX = 50, WIDTH - 50
            keys = pygame.key.get_pressed()

            forward = self.get_forward_vector()
            self.position += self.velocity

            # Move individual player left to right
            if self.player_rect.left > leftX:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.position.x -= 5

            if self.player_rect.right < rightX:
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.position.x += 5

            print(self.position)

            self.player_rect = pygame.Rect(
                self.position.x, self.position.y, SPRITE_SIZE, SPRITE_SIZE
            )

            # Block the following code

        def draw(self):
            screen.blit(zombie_sprite, self.player_rect)

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

    # Green, Yellow
    colors = [(100, 180, 100), (252, 163, 3)]

    # Map
    platforms = [
        # Outline
        [pygame.Rect(0, 0, 50, HEIGHT), colors[0]],
        [pygame.Rect(WIDTH - 50, 0, 50, HEIGHT), colors[0]],
        # Walls
        [pygame.Rect(50 * 3, 0, 20, HEIGHT / 2), colors[1]],
        [pygame.Rect(WIDTH - (25 + (50 * 3)), 0, 20, HEIGHT / 2), colors[1]],
    ]

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

        player.update()

        # Render Components

        # Map
        for platform in platforms:
            pygame.draw.rect(screen, platform[1], platform[0])

        # Character

        player.draw()

        for missile in missiles:
            missile.draw()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
