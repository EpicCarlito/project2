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

    # Green, Yellow, Purple
    colors = [(100, 180, 100), (252, 163, 3), (128, 0, 128)]

    # Map
    platforms = [
        # Outline
        [pygame.Rect(0, 0, 50, HEIGHT), colors[0]],
        [pygame.Rect(WIDTH - 50, 0, 50, HEIGHT), colors[0]],
        # Walls
        [pygame.Rect(50 * 3, 0, 25, HEIGHT / 2), colors[1]],
        [pygame.Rect(WIDTH - (25 + (50 * 3)), 0, 25, HEIGHT / 2), colors[1]],
    ]

    class Character:
        def __init__(self, x, y):
            self.position = pygame.Vector2(x, y)
            self.angle = 90
            self.velocity = pygame.Vector2(0, 0)

        def get_forward_vector(self):
            radians = math.radians(self.angle)
            forward = pygame.Vector2(math.cos(radians), -math.sin(radians))

            return forward

    class Crowd:
        def __init__(self):
            self.characters = []
            self.columns = 4
            self.spacing = SPRITE_SIZE + 4

        def update_positions(self):
            for i, character in enumerate(self.characters):
                column = i % self.columns
                row = i // self.columns

                character.position.x = self.start_x + column * self.spacing
                character.position.y = self.start_y + row * self.spacing

                character.rect.topleft = (
                    int(character.position.x),
                    int(character.position.y),
                )

        def draw(self):
            for character in self.characters:
                character.draw()

    # Crowd Class
    # Handles all the angles and velocities of the characters
    class PlayerCrowd(Crowd):
        def __init__(self, player):
            super().__init__()
            self.characters.append(player)
            self.columns = 4
            self.start_x = 50
            self.start_y = HEIGHT - HEIGHT / 4

        def add_character(self):
            self.characters.append(Player(0, 0))
            self.update_positions()

        def update(self):
            keys = pygame.key.get_pressed()
            player = self.characters[0]

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.position.x -= 5

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.position.x += 5

            max_x = WIDTH - 50 - SPRITE_SIZE - (self.columns - 1) * self.spacing

            player.position.x = max(50, min(player.position.x, max_x))

            self.start_x = player.position.x
            self.start_y = player.position.y
            self.update_positions()

        def draw(self):
            for character in self.characters:
                screen.blit(zombie_sprite, character.rect)

    # Enemy Class
    class Enemy(Character):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)

        def draw(self):
            screen.blit(zombie_sprite, self.rect)

    class EnemyCrowd(Crowd):
        def __init__(self):
            super().__init__()
            self.columns = 7
            self.rows = 3
            self.start_x = 180
            self.start_y = 40
            self.direction = 1
            self.speed = 1

            self.last_spawn_time = 0
            self.spawn_delay = 2500

            for row in range(self.rows):
                for column in range(self.columns):
                    x = self.start_x + column * self.spacing
                    y = self.start_y + row * self.spacing
                    self.characters.append(Enemy(x, y))

        def increase_speed(self):
            self.speed += 0.5

        def spawn_enemy(self):
            if self.characters:
                lowest_y = max(
                    enemy.position.y for enemy in self.characters
                )
                next_y = lowest_y + self.spacing
            else:
                next_y = self.start_y

            self.spawn_row_at_y(next_y)
            
        def spawn_row_at_y(self, y):
            for column in range(self.columns):
                x = self.start_x + column * self.spacing
                self.characters.append(Enemy(x, y))

        def update(self):
            current_time = pygame.time.get_ticks()

            if current_time - self.last_spawn_time >= self.spawn_delay:
                self.spawn_enemy()
                self.last_spawn_time = current_time

            for enemy in self.characters:
                enemy.position.y += self.speed

                enemy.rect.topleft = (
                    int(enemy.position.x),
                    int(enemy.position.y),
                )

    # Player Class
    class Player(Character):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)

        def update(self):
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.position.x -= 5

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.position.x += 5

            self.position.x = max(50, min(self.position.x, WIDTH - 50 - SPRITE_SIZE))

            self.player_rect.topleft = (
                int(self.position.x),
                int(self.position.y),
            )

        def draw(self):
            screen.blit(zombie_sprite, self.player_rect)

    class Missile:
        def __init__(self, start_position, direction):
            self.position = pygame.Vector2(start_position)
            self.previous_position = self.position.copy()
            self.speed = 3
            self.velocity = direction * self.speed
            self.radius = 2

        def update(self):
            steps = self.speed

            for _ in range(steps):
                self.position += self.velocity / steps

                missile_rect = pygame.Rect(
                    int(self.position.x - self.radius),
                    int(self.position.y - self.radius),
                    self.radius * 2,
                    self.radius * 2,
                )

            for platform in platforms:
                if missile_rect.colliderect(platform[0]):
                    return True

            return False

        def draw(self):
            pygame.draw.circle(
                screen,
                "yellow",
                (self.position.x, self.position.y),
                self.radius,
            )

    class MovingAttribute:
        def __init__(self, x, y, width, height, color, effect):
            self.position = pygame.Vector2(x, y)
            self.velocity = pygame.Vector2(0, 2)

            self.width = width
            self.height = height
            self.color = color
            self.effect = effect

            self.rect = pygame.Rect(x, y, width, height)

        def update(self):
            self.position += self.velocity

            self.rect = pygame.Rect(
                int(self.position.x),
                int(self.position.y),
                self.width,
                self.height,
            )

            if self.position.y > HEIGHT:
                self.position.y = -self.height

        def draw(self):
            pygame.draw.rect(screen, self.color, self.rect)

    # Game Loop

    # Map

    attributes = [
        MovingAttribute(50, 0, 100, 25, colors[2], "character"),
        MovingAttribute(WIDTH - 150, 0, 100, 25, colors[2], "delay"),
    ]

    missiles = []

    MISSILE_DELAY = 500
    last_shot_time = 0

    player = Player(WIDTH / 2, HEIGHT - HEIGHT / 4)
    crowd = PlayerCrowd(player)
    enemy_crowd = EnemyCrowd()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((20, 24, 40))

        ## Code Logic

        for missile in missiles[:]:
            hit_wall = missile.update()

            if hit_wall:
                missiles.remove(missile)
                continue

            missile_rect = pygame.Rect(
                int(missile.position.x - missile.radius),
                int(missile.position.y - missile.radius),
                missile.radius * 2,
                missile.radius * 2,
            )

            hit_enemy = None

            for enemy in enemy_crowd.characters:
                if missile_rect.colliderect(enemy.rect):
                    hit_enemy = enemy
                    break

            if hit_enemy is not None:
                enemy_crowd.characters.remove(hit_enemy)
                missiles.remove(missile)
                continue

            if (
                missile.position.y < 0
                or missile.position.y > HEIGHT
                or missile.position.x < 0
                or missile.position.x > WIDTH
            ):
                missiles.remove(missile)

        crowd.update()
        enemy_crowd.update()

        keys = pygame.key.get_pressed()

        current_time = pygame.time.get_ticks()

        if keys[pygame.K_SPACE]:
            if current_time - last_shot_time >= MISSILE_DELAY:
                for character in crowd.characters:
                    forward = character.get_forward_vector()

                    character_center = character.position + pygame.Vector2(
                        SPRITE_SIZE / 2,
                        SPRITE_SIZE / 2,
                    )

                    missile_start = character_center + forward * (SPRITE_SIZE / 2 + 4)

                    missiles.append(Missile(missile_start, forward))

                    last_shot_time = current_time

        for attribute in attributes:
            attribute.update()

            if player.rect.colliderect(attribute.rect):
                if attribute.effect == "character":
                    crowd.add_character()

                elif attribute.effect == "delay":
                    MISSILE_DELAY = max(100, MISSILE_DELAY - 100)

                attribute.position.y = -attribute.height
                attribute.rect.topleft = (
                    int(attribute.position.x),
                    int(attribute.position.y),
                )

        ## Render Components

        # Map
        for platform in platforms:
            pygame.draw.rect(screen, platform[1], platform[0])

        for attribute in attributes:
            attribute.draw()

        for missile in missiles:
            missile.draw()

        enemy_crowd.draw()
        crowd.draw()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
