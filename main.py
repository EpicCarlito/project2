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
    SPRITE_SIZE = 32

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Import Images

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    running = True
    game_state = "PLAYING"
    font = pygame.font.SysFont(None, 50)

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

    class SpriteSheet:
        def __init__(self, image_path):
            self.sheet = pygame.image.load(
                os.path.join(SCRIPT_DIR, image_path)
            ).convert_alpha()

        def get_image(self, x, y, width, height):
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            image.blit(self.sheet, (0, 0), (x, y, width, height))

            return image

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

            playerCount = 4 if len(self.characters) > 4 else len(self.characters)
            max_x = WIDTH - SPRITE_SIZE - (playerCount * self.spacing)

            player.position.x = max(50, min(player.position.x, max_x))

            self.start_x = player.position.x
            self.start_y = player.position.y

            self.update_positions()

            for character in self.characters:
                character.update()

        def draw(self):
            for character in self.characters:
                character.draw()

    # Enemy Class
    class Enemy(Character):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)

            self.position = pygame.Vector2(x, y)

            self.sheet = SpriteSheet("assets/virus.png")
            self.ANIMATION_FRAMES = [
                self.sheet.get_image(i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE)
                for i in range(4)
            ]

            self.DEATH_FRAMES = [
                self.sheet.get_image(
                    i * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE
                )
                for i in range(4, 8)
            ]
            
            self.current_frame = 0
            self.death_frame = 0

            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            self.animation_cooldown = 100

            self.dying = False
            self.dead = False

        def start_death(self):
            if self.dying:
                return

            self.dying = True
            self.death_frame = 0
            self.last_update = pygame.time.get_ticks()


        def update(self, speed):
            current_time = pygame.time.get_ticks()

            # Death animation
            if self.dying:
                if current_time - self.last_update >= self.animation_cooldown:
                    self.last_update = current_time
                    self.death_frame += 1

                    if self.death_frame >= len(self.DEATH_FRAMES):
                        self.dead = True

                return

            # Normal enemy movement
            distance_vector = player.position - self.position
            distance = distance_vector.length()

            if distance < 200 and distance > 0:
                direction = distance_vector.normalize()
                self.position += direction * speed * 2
            else:
                self.position.y += speed

            self.rect.topleft = (
                int(self.position.x),
                int(self.position.y),
            )

            # Normal animation — update only once
            if current_time - self.last_update >= self.animation_cooldown:
                self.last_update = current_time
                self.current_frame = (
                    self.current_frame + 1
                ) % len(self.ANIMATION_FRAMES)


        def draw(self):
            if self.dying:
                if self.death_frame < len(self.DEATH_FRAMES):
                    active_image = self.DEATH_FRAMES[self.death_frame]
                else:
                    return
            else:
                active_image = self.ANIMATION_FRAMES[self.current_frame]

            screen.blit(
                active_image,
                (int(self.position.x), int(self.position.y)),
            )

    class EnemyCrowd(Crowd):
        def __init__(self, start_x, columns):
            super().__init__()
            self.columns = columns
            self.rows = 3
            self.start_x = start_x
            self.start_y = 40
            self.direction = 1
            self.speed = 0.25

            for row in range(self.rows):
                for column in range(self.columns):
                    x = self.start_x + column * self.spacing
                    y = self.start_y + row * self.spacing
                    self.characters.append(Enemy(x, y))

        def spawn_enemy(self):
            if self.characters:
                highest_y = min(enemy.position.y for enemy in self.characters)
                next_y = highest_y - self.spacing
            else:
                next_y = self.start_y

            self.spawn_row_at_y(next_y)

        def spawn_row_at_y(self, y):
            for column in range(self.columns):
                x = self.start_x + column * self.spacing
                self.characters.append(Enemy(x, y))

        def update(self, player):
            collision_detected = False

            for enemy in self.characters[:]:
                enemy.update(self.speed)

                if enemy.dead:
                    self.characters.remove(enemy)
                    continue

                if not enemy.dying and enemy.rect.colliderect(player.rect):
                    collision_detected = True

            if self.characters:
                highest_y = min(enemy.position.y for enemy in self.characters)

                if highest_y >= self.start_y:
                    self.spawn_enemy()
            else:
                self.spawn_enemy()

            return collision_detected

        def draw(self):
            for character in self.characters:
                character.draw()

    # Player Class
    class Player(Character):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)
            self.sheet = SpriteSheet("assets/launcher.png")
            self.image = self.sheet.get_image(0, 0, SPRITE_SIZE, SPRITE_SIZE)

        def update(self):
            keys = pygame.key.get_pressed()

            self.rect.topleft = (int(self.position.x), int(self.position.y))

        def draw(self):
            screen.blit(self.image, self.rect)

    class Missile:
        def __init__(self, start_position, direction):
            self.position = pygame.Vector2(start_position)
            self.previous_position = self.position.copy()
            self.speed = 3
            self.velocity = direction * self.speed
            self.radius = 2

            self.sheet = SpriteSheet("assets/bubble.png")

            self.ANIMATION_FRAMES = [
                self.sheet.get_image(i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE)
                for i in range(4)
            ]

            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            self.animation_cooldown = 100

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

            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= self.animation_cooldown:
                self.current_frame += 1
                self.last_update = current_time

                if self.current_frame >= len(self.ANIMATION_FRAMES):
                    self.current_frame = 0

            return False

        def draw(self):
            active_image = self.ANIMATION_FRAMES[self.current_frame]

            draw_x = self.position.x - (SPRITE_SIZE // 2)
            draw_y = self.position.y - (SPRITE_SIZE // 2)

            screen.blit(active_image, (draw_x, draw_y))

    class MovingAttribute:
        def __init__(self, x, y, width, height, color, effect):
            self.position = pygame.Vector2(x, y)
            self.velocity = pygame.Vector2(0, 2)

            self.width = width
            self.height = height
            self.color = color
            self.effect = effect

            self.rect = pygame.Rect(x, y, width, height)

            self.font = pygame.font.SysFont(None, 20)

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

            text_surface = self.font.render(self.effect, True, "white")
            text_rect = text_surface.get_rect(center=self.rect.center)

            screen.blit(text_surface, text_rect)

    # Game Loop

    # Map

    attributes = [
        MovingAttribute(50, 0, 100, 25, colors[2], "+1 player"),
        MovingAttribute(WIDTH - 150, 0, 100, 25, colors[2], "shoot faster"),
    ]

    missiles = []

    missile_delay = 800

    last_shot_time = 0

    player = Player(WIDTH / 2, HEIGHT - HEIGHT / 4)
    crowd = PlayerCrowd(player)

    enemies = [EnemyCrowd(64, 2), EnemyCrowd(180, 4), EnemyCrowd(WIDTH - 134, 2)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_state == "PLAYING":
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
                hit_crowd = None

                for enemy_crowd in enemies:
                    for enemy in enemy_crowd.characters:
                        if not enemy.dying and missile_rect.colliderect(enemy.rect):
                            hit_enemy = enemy
                            hit_crowd = enemy_crowd
                            break

                    if hit_enemy is not None:
                        break

                if hit_enemy is not None:
                    hit_enemy.start_death()
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

            collision_detected = False

            for enemy_crowd in enemies:
                if enemy_crowd.update(player):
                    collision_detected = True

            if collision_detected:
                game_state = "GAME_OVER"

            keys = pygame.key.get_pressed()

            current_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                if current_time - last_shot_time >= missile_delay:
                    for character in crowd.characters:
                        forward = character.get_forward_vector()

                        character_center = character.position + pygame.Vector2(
                            SPRITE_SIZE / 2,
                            SPRITE_SIZE / 2,
                        )

                        missile_start = character_center + forward * (
                            SPRITE_SIZE / 2 + 4
                        )

                        missiles.append(Missile(missile_start, forward))

                        last_shot_time = current_time

            for attribute in attributes:
                attribute.update()
                for character in crowd.characters:
                    if character.rect.colliderect(attribute.rect):
                        if attribute.effect == "+1 player":
                            crowd.add_character()

                        elif attribute.effect == "shoot faster":
                            missile_delay = max(300, missile_delay - 50)

                        for enemy_crowd in enemies:
                            enemy_crowd.speed += 0.01

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

            for enemy_crowd in enemies:
                enemy_crowd.draw()

            crowd.draw()
        elif game_state == "GAME_OVER":
            screen.fill((0, 0, 0))

            text_surf = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
