import sys
import pygame
import math
import heapq
import random

pygame.init()

screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption("shooter game thingy idk")
clock = pygame.time.Clock()

background = pygame.transform.scale(pygame.image.load("images/MAP.png").convert(), (800, 700))
# Load the shooting sound
shooting_sound = pygame.mixer.Sound("308 Single.mp3")
shooting_sound.set_volume(0.2)

# Load the sound for start menu and retry menu on channel 1
background_music = pygame.mixer.Sound("Action 1.mp3")
pygame.mixer.Channel(1).set_volume(0.5)
pygame.mixer.Channel(1).play(background_music, -1)
pygame.mixer.Channel(1).stop()

# Load the sound for start menu and retry menu on channel 1
start_menu_sound = pygame.mixer.Sound("Ambient 2.mp3")
pygame.mixer.Channel(1).set_volume(0.5)
pygame.mixer.Channel(0).play(start_menu_sound, -1)
pygame.mixer.Channel(1).stop()


def start_menu():
    menu_font = pygame.font.Font(None, 48)
    menu_text = menu_font.render("Press 'Space' to Start", True, (255, 255, 255))
    text_rect = menu_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    pygame.mixer.Channel(0).play(start_menu_sound, loops=-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Stop the start menu sound when the space key is pressed
                pygame.mixer.Channel(0).stop()
                pygame.mixer.Channel(1).play(background_music, loops=-1)
                return  # Exit the start menu if the space key is pressed

        screen.blit(background, (0, 0))
        screen.blit(menu_text, text_rect)
        pygame.display.update()


def is_within_playable_area(position):
    left_square = pygame.Rect(45, 110, 260, 440)
    hallway = pygame.Rect(300, 200, 180, 80)
    right_square = pygame.Rect(480, 110, 260, 440)
    return left_square.collidepoint(position) or hallway.collidepoint(position) or right_square.collidepoint(position)

def create_playable_area_grid(grid_size):
    grid = []
    for y in range(0, 700, grid_size):
        row = []
        for x in range(0, 800, grid_size):
            pos = pygame.math.Vector2(x, y)
            is_obstacle = not is_within_playable_area(pos)
            row.append(is_obstacle)
        grid.append(row)
    return grid

# PLAYER
class Player(pygame.sprite.Sprite):
    # INITIAL CONSTRUCTOR
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(200, 500)
        self.image = pygame.transform.rotozoom(pygame.image.load('images/playerCharacter.png').convert_alpha(), 0, 0.18)
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
        self.gun_barrel_offset = pygame.math.Vector2(2, -40)
        self.grid_size = 15
        self.playable_area_grid = create_playable_area_grid(self.grid_size)

    # ROTATION
    def player_rotation(self):
        # GET MOUSE COORDINATES
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.y_change_mouse_player = (self.mouse_coords[1] - self.hitbox_rect.centery)
        # ADDED 90 TO FIX CALCULATION FOR THE TIME BEING
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player)) + 90
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
            if not self.shoot:
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
            # Play the shooting sound
            shooting_sound.play()

    # CHANGE POSITION
    def move(self):
        new_pos = self.pos + pygame.math.Vector2(self.velocity_x, self.velocity_y)
        grid_x = int(new_pos.x / self.grid_size)
        grid_y = int(new_pos.y / self.grid_size)

        # Check if the new position is within the playable area grid
        if 0 <= grid_x < len(self.playable_area_grid[0]) and 0 <= grid_y < len(self.playable_area_grid):
            # Check if the new position is not an obstacle in the grid
            if not self.playable_area_grid[grid_y][grid_x]:
                self.pos = new_pos

        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    # DRAW HEALTH TEXT
    def draw_health_text(self):
        font = pygame.font.Font(None, 30)
        health_text = font.render('Health:', True, (255, 255, 255))
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
        pygame.draw.rect(health_bar_surface, (255, 255, 255), (0, 0, bar_width, bar_height))
        # Draw the colored portion representing the health
        pygame.draw.rect(health_bar_surface, (255, 0, 0), (0, 0, health_bar_width, bar_height))
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
        self.image = pygame.transform.rotozoom(pygame.image.load('images/bullet.png').convert_alpha(), 0, 1.2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.speed = 30
        self.bullet_angle = bullet_angle - 90
        self.x_vel = math.cos(self.bullet_angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.bullet_angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = 750
        self.spawn_time = pygame.time.get_ticks()

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            # if timer - the timer for the bullet creation is grater than bullet lifetime -  KILL IT
            self.kill()

    def update_movement(self):
        self.bullet_movement()

        # Check for collisions with the enemy
        enemy_hit = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in enemy_hit:
            # Decrease enemy health and kill the bullet
            enemy.health -= 30
            self.kill()

        # Check if the bullet is out of the screen or hits the non-playable area
        if (
                self.rect.x < 0
                or self.rect.y < 0
                or self.rect.x > screen.get_width()
                or self.rect.y > screen.get_height()
                or not is_within_playable_area((self.rect.x, self.rect.y))
        ):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load("images/zombiebasic.png").convert_alpha()
        self.image = pygame.transform.rotozoom(original_image, 0, 0.6)
        self.base_image = self.image.copy()  # Store the original rotated image
        self.rect = self.image.get_rect()
        self.hitbox_rect = self.base_image.get_rect(center=self.rect.center)
        self.grid_size = 15
        self.speed = 3
        self.path = []  # Store the path calculated by A*
        self.path_update_timer = 100  # Timer to control path updates
        self.spawned = False  # Flag to check if the enemy has been spawned
        self.rotation_angle = 0  # Initial rotation angle
        self.health = 100

    def update_rotation(self, target_x, target_y):
        angle = math.degrees(math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx))
        self.rotation_angle = -angle - 90
        self.image = pygame.transform.rotate(self.base_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox_rect.center = self.rect.center  # Recalculate hitbox_rect position

    def spawn_randomly(self, playable_area_grid, player_position, min_distance):
        if not self.spawned:
            x, y = self.get_random_position(playable_area_grid, self.grid_size)
            distance_to_player = pygame.math.Vector2(x - player_position.x, y - player_position.y).length()

            if distance_to_player >= min_distance:
                self.rect.topleft = (x, y)
                self.spawned = True  # Set the spawned flag to True

    def get_random_position(self, playable_area_grid, grid_size):
        valid_positions = []

        for y in range(0, len(playable_area_grid) * grid_size, grid_size):
            for x in range(0, len(playable_area_grid[0]) * grid_size, grid_size):
                grid_x = int(x / grid_size)
                grid_y = int(y / grid_size)

                if 0 <= grid_x < len(playable_area_grid[0]) and 0 <= grid_y < len(playable_area_grid):
                    if not playable_area_grid[grid_y][grid_x]:
                        valid_positions.append((x, y))

        if valid_positions:
            return random.choice(valid_positions)
        else:
            # If no valid position is found, return a default position
            return 0, 0

    def get_grid_position(self):
        return int(self.rect.x / self.grid_size), int(self.rect.y / self.grid_size)

    # A star algorithm
    def update_path_to_player(self, player_pos, playable_area_grid):
        start = self.get_grid_position()
        goal = (int(player_pos.x / self.grid_size), int(player_pos.y / self.grid_size))
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        open_set = []
        heapq.heappush(open_set, (0, start))
        cost_to_point = {start: 0}
        came_from = {start: None}

        while open_set:
            current_cost, current_point = heapq.heappop(open_set)

            if current_point == goal:
                # Reconstruct the path
                path = []
                while current_point:
                    path.append(current_point)
                    current_point = came_from[current_point]
                self.path = path[::-1]
                return

            for move in moves:
                new_point = (current_point[0] + move[0], current_point[1] + move[1])

                if (
                        0 <= new_point[0] < len(playable_area_grid[0])
                        and 0 <= new_point[1] < len(playable_area_grid)
                        and not playable_area_grid[new_point[1]][new_point[0]]
                ):
                    new_cost = cost_to_point[current_point] + 1
                    if (
                            new_point not in cost_to_point
                            or new_cost < cost_to_point[new_point]
                    ):
                        cost_to_point[new_point] = new_cost
                        priority = (new_cost + self.heuristic(new_point, goal), new_point)
                        heapq.heappush(open_set, priority)
                        came_from[new_point] = current_point

        self.path = []  # If no path is found, clear the existing path

    def heuristic(self, a, b):
        # heuristic using Euclidean distance
        return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

    def draw_hitbox(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def move_towards_player_astar(self, playable_area_grid):
        if self.path:
            for next_point in reversed(self.path):
                target_x = next_point[0] * self.grid_size + self.grid_size / 2
                target_y = next_point[1] * self.grid_size + self.grid_size / 2

                direction = pygame.math.Vector2(target_x - self.rect.x, target_y - self.rect.y).normalize()
                new_rect = self.rect.move(direction.x * self.speed, direction.y * self.speed)

                grid_x = int(new_rect.x / self.grid_size)
                grid_y = int(new_rect.y / self.grid_size)

                if (
                        0 <= grid_x < len(playable_area_grid[0])
                        and 0 <= grid_y < len(playable_area_grid)
                        and not playable_area_grid[grid_y][grid_x]
                ):
                    self.rect = new_rect
                    break  # Exit the loop if a valid position is found

    def draw_health_bar(self):
        # Calculate health ratio
        health_ratio = self.health / 100
        # Set the dimensions of the health bar
        bar_width = 40
        bar_height = 5
        # Calculate the width of the colored portion of the health bar
        health_bar_width = int(bar_width * health_ratio)
        # Create a surface for the health bar
        health_bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        # Draw the background of the health bar
        pygame.draw.rect(health_bar_surface, (255, 255, 255), (0, 0, bar_width, bar_height))
        # Choose the color based on health status
        if health_ratio > 0.6:
            color = (0, 255, 0)  # Green
        elif health_ratio > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
        # Draw the colored portion representing the health
        pygame.draw.rect(health_bar_surface, color, (0, 0, health_bar_width, bar_height))
        # Set the position to display the health bar above the enemy
        health_bar_pos = (self.rect.centerx - bar_width // 2, self.rect.y - 10)
        # Blit the health bar onto the screen
        screen.blit(health_bar_surface, health_bar_pos)

    def update(self):
        if not self.spawned:
            self.spawn_randomly(player.playable_area_grid, player.pos, 150)
        else:
            if self.path_update_timer <= 0:
                self.update_path_to_player(player.pos, player.playable_area_grid)
                self.path_update_timer = 10
            else:
                self.path_update_timer -= 1

            # Pass playable_area_grid to move_towards_player_astar
            self.move_towards_player_astar(player.playable_area_grid)

            # Update the enemy's rotation
            self.update_rotation(player.pos.x, player.pos.y)
            # Draw the enemy health bar
            self.draw_health_bar()
            # Check if the enemy has reached the player's hitbox
            if self.rect.colliderect(player.hitbox_rect):
                player.health -= 30
                self.kill()  # Remove the enemy if there's a collision
            else:
                # Check if the enemy's health is 0 or less, and kill it
                if self.health <= 0:
                    self.kill()

# Function to spawn enemies
def spawn_enemies(wave_number):
    enemies = pygame.sprite.Group()

    for i in range(wave_number):
        enemy = Enemy()
        enemy_group.add(enemy)
        all_sprites_group.add(enemy)
        enemies.add(enemy)

    return enemies

def game_over_screen(wave_number):
    screen.blit(background, (0, 0))  # Display the background map

    # Display you died mssg
    font = pygame.font.Font(None, 48)
    game_over_text = font.render('You Died', True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(game_over_text, text_rect)

    # Display wave number
    wave_font = pygame.font.Font(None, 36)
    wave_text = wave_font.render(f'Wave: {wave_number}', True, (255, 255, 255))
    wave_rect = wave_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(wave_text, wave_rect)

    # Display retry message
    retry_font = pygame.font.Font(None, 30)
    retry_text = retry_font.render('Press Space to Retry', True, (255, 255, 255))
    retry_rect = retry_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    screen.blit(retry_text, retry_rect)

    pygame.display.update()
    pygame.mixer.Channel(1).stop()
    pygame.mixer.Channel(0).play(start_menu_sound, loops=-1)

    # Wait for the player to press space to retry
    space_pressed = False
    while not space_pressed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                space_pressed = True

    # Kill all enemies before retrying
    for enemy in enemy_group.sprites():
        enemy.kill()

    pygame.mixer.Channel(0).stop()
    pygame.mixer.Channel(1).play(background_music, loops=-1)
    return True  # Retry the game




all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# CREATE INSTANCE OF PLAYER
player = Player()
all_sprites_group.add(player)

current_wave = 1
enemies = spawn_enemies(current_wave)

# GAME LOOP
running = True
show_menu = True
while running:
    if show_menu:
        start_menu()
        show_menu = False
        # fill the screen with a color to wipe away anything from last frame
    screen.blit(background, (0, 0))

    # HANDLE EVENTS/ pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.draw_health_text()
    player.draw_health_bar()

    # Render the wave number on the top left of the screen
    font = pygame.font.Font(None, 36)
    wave_text = font.render(f'Wave: {current_wave}', True, (255, 255, 255))
    screen.blit(wave_text, (10, 10))

    for bullet in bullet_group.sprites():
        bullet.update_movement()

    # Check if all enemies are killed
    if len(enemies) == 0:
        current_wave += 1
        enemies = spawn_enemies(current_wave)

    # RENDER PLAYER AND BULLET // CALL FUNCTION TO UPDATE THEIR STATES
    all_sprites_group.draw(screen)
    all_sprites_group.update()

    # Check if player's health is zero or less
    if player.health <= 0:
        # Display game over screen
        if game_over_screen(current_wave):
            # Reset game state
            player.health = 100
            current_wave = 1
            enemies = spawn_enemies(current_wave)
        else:
            running = False  # Exit the game

    pygame.display.update()
    clock.tick(60)  # limits FPS to 60

pygame.quit()
