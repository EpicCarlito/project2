# AI For Game Programming
# Ms. Qiu - Period 7

import asyncio
import math
import os
import random

import pygame


async def main():
    pygame.init()
    pygame.mixer.init()
    WIDTH, HEIGHT = 500, 800
    SPRITE_SIZE = 32

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    DIRECTORY = os.path.dirname(os.path.abspath(__file__))

    pygame.mixer.music.load(os.path.join(DIRECTORY, "assets/background_music.ogg"))
    pygame.mixer.music.play(-1)

    running = True
    gameState = "PLAYING"
    font = pygame.font.SysFont(None, 50)

    animationCooldown = 100
    
    score = 0

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

    # Sprites
    class SpriteSheet:
        def __init__(self, image_path):
            self.sheet = pygame.image.load(
                os.path.join(DIRECTORY, image_path)
            ).convert_alpha()

        def get_image(self, x, y, width, height):
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            image.blit(self.sheet, (0, 0), (x, y, width, height))

            return image

    # For Player and Enemy
    class Character:
        def __init__(self, x, y):
            self.position = pygame.Vector2(x, y)
            self.rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)
            self.angle = 90
            self.velocity = pygame.Vector2(0, 0)

        def get_forward_vector(self):
            radians = math.radians(self.angle)
            forward = pygame.Vector2(math.cos(radians), -math.sin(radians))

            return forward

    # Crowd Class
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

    # Player Crowd Class
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
            maxX = WIDTH - SPRITE_SIZE - (playerCount * self.spacing)

            player.position.x = max(50, min(player.position.x, maxX))

            self.start_x = player.position.x
            self.start_y = player.position.y

            self.update_positions()

            for character in self.characters:
                character.update()

        def draw(self):
            for character in self.characters:
                character.draw()

    # Player Class
    class Player(Character):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.sheet = SpriteSheet("assets/launcher.png")
            self.image = self.sheet.get_image(0, 0, SPRITE_SIZE, SPRITE_SIZE)

        def update(self):
            self.rect.topleft = (self.position.x, self.position.y)

        def draw(self):
            screen.blit(self.image, self.rect)

    class EnemyCrowd(Crowd):
        def __init__(self, startX, columns):
            super().__init__()
            self.columns = columns
            self.rows = 3
            self.startX = startX
            self.startY = 40
            self.direction = 1
            self.speed = 0.25

            for row in range(self.rows):
                for column in range(self.columns):
                    x = self.startX + column * self.spacing
                    y = self.startY + row * self.spacing
                    self.characters.append(Enemy(x, y))

        def spawn_enemy(self):
            if self.characters:
                highestY = min(enemy.position.y for enemy in self.characters)
                nextY = highestY - self.spacing
            else:
                nextY = self.startY

            self.spawn_row_at_y(nextY)

        def spawn_row_at_y(self, y):
            for column in range(self.columns):
                x = self.startX + column * self.spacing
                self.characters.append(Enemy(x, y))

        def update(self, player):
            collision_detected = False

            for enemy in self.characters[:]:
                enemy.update(self.speed)

                if enemy.rect.colliderect(player.rect):
                    collision_detected = True

            if self.characters:
                highestY = min(enemy.position.y for enemy in self.characters)

                if highestY >= self.startY:
                    self.spawn_enemy()
            else:
                self.spawn_enemy()

            return collision_detected

        def draw(self):
            for character in self.characters:
                character.draw()

    # Enemy Class
    class Enemy(Character):
        def __init__(self, x, y):
            super().__init__(x, y)

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
                for i in range(4, 18)
            ]

            self.currentFrame = 0
            self.lastUpdate = pygame.time.get_ticks()

            self.exploding = False

        def explode(self):
            if not self.exploding:
                self.exploding = True
                self.currentFrame = 0
                self.velocity = pygame.Vector2(0, 0)

        def update(self, speed):
            currentTime = pygame.time.get_ticks()

            if self.exploding:
                if currentTime - self.lastUpdate >= animationCooldown:
                    self.lastUpdate = currentTime
                    self.currentFrame += 1

                    if self.currentFrame >= len(self.DEATH_FRAMES):
                        return True
                return False

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

            if currentTime - self.lastUpdate >= animationCooldown:
                self.lastUpdate = currentTime
                self.currentFrame = (self.currentFrame + 1) % len(self.ANIMATION_FRAMES)

            return False

        def draw(self):
            if self.exploding:
                if self.currentFrame < len(self.DEATH_FRAMES):
                    activeImage = self.DEATH_FRAMES[self.currentFrame]
                else:
                    return
            else:
                activeImage = self.ANIMATION_FRAMES[self.currentFrame]

            screen.blit(
                activeImage,
                (int(self.position.x), int(self.position.y)),
            )

    class Missile(Character):
        def __init__(self, x, y, startPosition, direction):
            super().__init__(x, y)
            self.position = pygame.Vector2(startPosition)
            self.speed = 3
            self.velocity = direction * self.speed
            self.radius = 2

            self.sheet = SpriteSheet("assets/bubble.png")

            self.ANIMATION_FRAMES = [
                self.sheet.get_image(i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE)
                for i in range(3)
            ]

            self.currentFrame = 0
            self.lastUpdate = pygame.time.get_ticks()

        def update(self):
            self.position += self.velocity
            self.rect.center = (self.position.x, self.position.y)

            for platform in platforms:
                if self.rect.colliderect(platform[0]):
                    return True

            currentTime = pygame.time.get_ticks()
            if currentTime - self.lastUpdate >= animationCooldown:
                self.currentFrame += 1
                self.lastUpdate = currentTime

                if self.currentFrame >= len(self.ANIMATION_FRAMES):
                    self.currentFrame = 0

            return False

        def draw(self):
            active_image = self.ANIMATION_FRAMES[self.currentFrame]

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

            textSurface = self.font.render(self.effect, True, "white")
            textRect = textSurface.get_rect(center=self.rect.center)

            screen.blit(textSurface, textRect)

    # Game Loop

    attributes = [
        MovingAttribute(50, 0, 100, 25, colors[2], "+1 player"),
        MovingAttribute(WIDTH - 150, 0, 100, 25, colors[2], "shoot faster"),
    ]

    missiles = []

    missile_delay = 800
    last_shot_time = 0

    player = Player(WIDTH / 2, HEIGHT - HEIGHT / 4)
    crowd = PlayerCrowd(player)
    # I'm too lazy to find the precise coordinates
    enemies = [EnemyCrowd(64, 2), EnemyCrowd(180, 4), EnemyCrowd(WIDTH - 134, 2)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if gameState == "PLAYING":
            screen.fill((20, 24, 40))

            keys = pygame.key.get_pressed()
            currentTime = pygame.time.get_ticks()

            # Spawn Missiles
            if keys[pygame.K_SPACE]:
                if currentTime - last_shot_time >= missile_delay:
                    for character in crowd.characters:
                        forward = character.get_forward_vector()

                        character_center = character.position + pygame.Vector2(
                            SPRITE_SIZE / 2,
                            SPRITE_SIZE / 2,
                        )

                        missileStart = character_center + forward * (
                            SPRITE_SIZE / 2 + 4
                        )

                        missiles.append(
                            Missile(
                                missileStart.x, missileStart.y, missileStart, forward
                            )
                        )

                        last_shot_time = currentTime

            # Give Attributes
            for attribute in attributes:
                attribute.update()
                for character in crowd.characters:
                    if character.rect.colliderect(attribute.rect):
                        if attribute.effect == "+1 player":
                            crowd.add_character()

                        elif attribute.effect == "shoot faster":
                            missile_delay = max(300, missile_delay - 10)

                        for enemy_crowd in enemies:
                            enemy_crowd.speed += 0.25

                        attribute.position.y = -attribute.height
                        attribute.rect.topleft = (
                            int(attribute.position.x),
                            int(attribute.position.y),
                        )

            # Detect Missile Collisions
            for missile in missiles[:]:
                hasHitWall = missile.update()

                if hasHitWall:
                    missiles.remove(missile)
                    continue

                if (
                    missile.position.y < 0
                    or missile.position.y > HEIGHT
                    or missile.position.x < 0
                    or missile.position.x > WIDTH
                ):
                    missiles.remove(missile)
                    continue

                hitEnemy = None
                for enemyCrowd in enemies:
                    for enemy in enemyCrowd.characters:
                        if not enemy.exploding:
                            if missile.rect.colliderect(enemy.rect):
                                hitEnemy = enemy
                                break
                    if hitEnemy is not None:
                        break

                if hitEnemy is not None:
                    hitEnemy.explode()
                    score += 1
                    missiles.remove(missile)

            crowd.update()

            # Detect Enemy Collisions / Game Over Trigger
            collisionDetected = False

            for enemyCrowd in enemies:
                if enemyCrowd.update(player):
                    collisionDetected = True

            if collisionDetected:
                gameState = "GAME_OVER"

            # Render Components

            for platform in platforms:
                pygame.draw.rect(screen, platform[1], platform[0])

            for attribute in attributes:
                attribute.draw()

            for missile in missiles:
                missile.draw()

            for enemy_crowd in enemies:
                enemy_crowd.draw()
                
            scoreText = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(scoreText, (15, 15))

            crowd.draw()
        elif gameState == "GAME_OVER":
            screen.fill((0, 0, 0))

            textSurf = font.render("GAME OVER", True, (255, 0, 0))
            textRect = textSurf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            subSurf = font.render(f"FINAL SCORE: {score}", True, (255, 255, 255))
            subRect = subSurf.get_rect(center=(WIDTH // 2, (HEIGHT // 2) + 40))
            screen.blit(textSurf, textRect)
            screen.blit(subSurf, subRect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
