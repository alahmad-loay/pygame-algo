import math
import pygame
import random

random_number = random.randint(1, 10)  # Generates a random number between 1 and 10
print(random_number)

# PYGAME INITIALIZE
pygame.init()

# CREATE SCREEN/WINDOW
screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption("shooter game thingy idk")
clock = pygame.time.Clock()

# LOAD BACKGROUND
background = pygame.transform.scale(
    pygame.image.load("images/MAP.png").convert(), (800, 700)
)


# PLAYER
class Player(pygame.sprite.Sprite):
    # INITIAL CONSTRUCTOR
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(200, 500)
        self.image = pygame.transform.rotozoom(
            pygame.image.load("images/playerCharacter.png").convert_alpha(), 0, 0.18
        )
        # WHAT WE ROTATE FOR HIGHER QUALITY AND FEWER BUGS
        self.base_player_image = self.image
        # TO CHECK HITBOX
        self.hitbox_rect = self.base_player_image.get_rect(center=self.pos)
        self.hitbox_rect.height = 30
        # TO DRAW PLAYER ON SCREEN
        self.rect = self.hitbox_rect.copy()
        # for bullet
        self.shoot = False
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = 100
        self.gun_barrel_offset = pygame.math.Vector2(-10, -40)  # ill come back to it

    def update(self):
        # Check for natural health regeneration
        if self.health < 100:
            self.health += self.health_regen

    # ROTATION
    def player_rotation(self):
        # GET MOUSE COORDINATES
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = self.mouse_coords[0] - self.hitbox_rect.centerx
        self.y_change_mouse_player = self.mouse_coords[1] - self.hitbox_rect.centery
        # ADDED 90 TO FIX CALCULATION FOR THE TIME BEING
        self.angle = (
            math.degrees(
                math.atan2(self.y_change_mouse_player, self.x_change_mouse_player)
            )
            + 90
        )
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.hitbox_rect.center)

    # HANDLE USER INPUTS
    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocity_y = -6
        if keys[pygame.K_s]:
            self.velocity_y = 6
        if keys[pygame.K_d]:
            self.velocity_x = 6
        if keys[pygame.K_a]:
            self.velocity_x = -6
        # MOVE DIAGONALLY / PYTHAGOREAN THEORY
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_y /= math.sqrt(2)
            self.velocity_x /= math.sqrt(2)
        # for bullet
        if pygame.mouse.get_pressed() == (1, 0, 0):
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    # CHANGE POSITION
    def move(self):
        new_pos = self.pos + pygame.math.Vector2(self.velocity_x, self.velocity_y)
        if self.is_within_playable_area(new_pos):
            self.pos = new_pos
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def is_within_playable_area(self, new_pos):
        # Define boundaries for the left square region
        left_square = pygame.Rect(50, 110, 260, 430)  # Adjust these values as needed

        # Define boundaries for the hallway region
        hallway = pygame.Rect(310, 220, 180, 70)  # Adjust these values as needed

        # Define boundaries for the right square region
        right_square = pygame.Rect(490, 110, 260, 430)  # Adjust these values as needed

        # Check if the new position is within the left square, hallway, or right square
        if (
            left_square.collidepoint(new_pos)
            or hallway.collidepoint(new_pos)
            or right_square.collidepoint(new_pos)
        ):
            return True  # Player is within the left square, hallway, or right square
        else:
            return False  # Player is outside the left square, hallway, and right square

    # DRAW HEALTH TEXT
    def draw_health_text(self):
        font = pygame.font.Font(None, 30)
        health_text = font.render("Health:", True, (255, 255, 255))
        text_rect = health_text.get_rect(center=((screen.get_width() // 2) - 100, 15))
        screen.blit(health_text, text_rect)

    # DRAW HEALTH BAR
    def draw_health_bar(self):
        # Calculate health ratio
        health_ratio = self.health / self.max_health
        # Set the dimensions of the health bar
        bar_width = 100
        bar_height = 10
        # Calculate the width of the colored portion of the health bar
        health_bar_width = int(bar_width * health_ratio)
        # Create a surface for the health bar
        health_bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        # Draw the background of the health bar
        pygame.draw.rect(
            health_bar_surface, (255, 255, 255), (0, 0, bar_width, bar_height)
        )
        # Draw the colored portion representing the health
        pygame.draw.rect(
            health_bar_surface, (255, 0, 0), (0, 0, health_bar_width, bar_height)
        )
        # Set the position to display the health bar at the top of the screen
        health_bar_pos = (screen.get_width() // 2 - bar_width // 2, 10)
        # Blit the health bar onto the screen
        screen.blit(health_bar_surface, health_bar_pos)

    # UPDATE PLAYER STATE
    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_angle):
        super().__init__()
        self.image = pygame.transform.rotozoom(
            pygame.image.load("images/bullet.png").convert_alpha(), 0, 1.5
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.speed = 30
        self.bullet_angle = bullet_angle - 90
        self.x_vel = math.cos(self.bullet_angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.bullet_angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = 750  # Maximum lifespan of the bullet in milliseconds
        self.spawn_time = pygame.time.get_ticks()

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Check if the bullet has gone off the screen
        if (
            self.rect.left < 0
            or self.rect.right > screen.get_width()
            or self.rect.top < 0
            or self.rect.bottom > screen.get_height()
        ):
            self.kill()  # Remove the bullet if it's off-screen

        # Check for collisions with enemies
        for enemy in enemy_group.sprites():
            if self.rect.colliderect(enemy.rect):
                self.kill()  # Remove the bullet if it hits an enemy
                enemy.kill()  # Remove the enemy if it's hit by the bullet

    def update_movement(self):
        self.bullet_movement()

        # Check if the bullet has exceeded its maximum lifespan
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()  # Remove the bullet if it's too old


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.image.load("images/yellow_ball.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.05)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.chase_speed = 2  # Enemy's movement speed when chasing

    def update(self):
        # Check for player's presence within a certain distance
        if pygame.sprite.collide_rect(self, player):
            # Chase behavior: Move towards the player
            if self.rect.x < player.rect.x:
                self.rect.x += self.chase_speed
            elif self.rect.x > player.rect.x:
                self.rect.x -= self.chase_speed

            if self.rect.y < player.rect.y:
                self.rect.y += self.chase_speed
            elif self.rect.y > player.rect.y:
                self.rect.y -= self.chase_speed
            else:
                # Wander behavior: Move randomly
                self.rect.x += random.randint(-3, 3)
                self.rect.y += random.randint(-3, 3)

    def check_collision(self):
        if player.hitbox_rect.colliderect(self.rect):
            player.health -= 30
            self.kill()  # Remove the enemy if there's a collision


all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()

        self.image = pygame.image.load("images/bullet.png").convert_alpha()
        self.rect = self.image.get_rect(center=start_pos)

        # Calculate projectile direction and speed
        vector = target_pos - start_pos
        vector = vector.normalize() * 30  # Set initial projectile speed

        self.x_vel = vector[0]
        self.y_vel = vector[1]

        # Set maximum lifespan for the projectile
        self.lifespan = 5000  # Lifespan in milliseconds

    def update(self):
        # Update projectile position based on velocity
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

        # Check for collisions with enemies or outside the screen
        for enemy in enemy_group.sprites():
            if self.rect.colliderect(enemy.rect):
                enemy.hit()
                self.kill()

        if self.rect.left < 0 or self.rect.right > screen.get_width() or \
            self.rect.top < 0 or self.rect.bottom > screen.get_height():
            self.kill()  # Destroy the projectile if it goes off-screen

        # Decrement projectile lifespan
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()  # Destroy the projectile if its lifespan is over

class RangedEnemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.image.load("images/ranged_enemy.png").convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.attack_range = 300
        self.attack_cooldown = 1000  # Time between attacks in milliseconds

    def update(self):
        # Handle enemy movement and attack behavior
        if pygame.sprite.collide_rect(self, player):
            # Attack the player if in range
            if self.attack_cooldown <= 0:
                # Create a projectile or bullet
                projectile = Projectile(self.rect.center, player.rect.center)
                all_sprites_group.add(projectile)
                enemy_bullet_group.add(projectile)
                self.attack_cooldown = 1000
            else:
                self.attack_cooldown -= 1
        else:
            # Move towards the player if not in range
            if self.rect.x < player.rect.x:
                self.rect.x += 1
            else:
                self.rect.x -= 1

            if self.rect.y < player.rect.y:
                self.rect.y += 1
            else:
                self.rect.y -= 1

    def check_collision(self):
        # Handle collisions with player or player's bullets
            pass

# CREATE INSTANCE OF PLAYER
player = Player()

all_sprites_group.add(player)

enemy = Enemy((600, 400))
enemy_group.add(enemy)
all_sprites_group.add(enemy)

# GAME LOOP
running = True
while running:
    # fill the screen with a color to wipe away anything from last frame
    screen.blit(background, (0, 0))

    # HANDLE EVENTS/ pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.draw_health_text()
    player.draw_health_bar()

    pygame.draw.rect(screen, "red", player.hitbox_rect, width=2)
    pygame.draw.rect(screen, "yellow", player.rect, width=2)

    for bullet in bullet_group.sprites():
        bullet.update_movement()

    # Check for collisions between the player's hitbox and the enemy's sprite
    # CHANGE POSITION AND MAKE A FUNCTION DO NOT LEAVE IT IN GAME LOOP
    for enemy in enemy_group.sprites():
        if player.hitbox_rect.colliderect(enemy.rect):
            player.health -= 30
            enemy.kill()  # Remove the enemy if there's a collision

    # RENDER PLAYER AND BULLET // CALL FUNCTION TO UPDATE THEIR STATES
    all_sprites_group.draw(screen)
    all_sprites_group.update()

    pygame.display.update()
    clock.tick(60)  # limits FPS to 60
# ...

# SCORE VARIABLES
score = 0
highest_score = 0


def display_score():
    font = pygame.font.Font(None, 30)
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    text_rect = score_text.get_rect(center=(screen.get_width() // 2, 35))
    screen.blit(score_text, text_rect)


def update_score():
    global score, highest_score

    # Increase score for killing enemies
    for enemy in enemy_group.sprites():
        if enemy.rect.bottom < 0:
            score += 100
            enemy.kill()

    # Update highest score
    if score > highest_score:
        highest_score = score


# GAME LOOP
running = True
while running:
    # ...

    # Update score
    update_score()

    # Display score and highest score
    display_score()

    # ...

pygame.quit()
