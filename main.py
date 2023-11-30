import math
import pygame
import random
import heapq

# PYGAME INITIALIZE
pygame.init()

# CREATE SCREEN/WINDOW
screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption("shooter game thingy idk")
clock = pygame.time.Clock()

# LOAD BACKGROUND
background = pygame.transform.scale(pygame.image.load("images/MAP.png").convert(), (800, 700))


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
        self.gun_barrel_offset = pygame.math.Vector2(-10, -40)  # ill come back to it

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
        if left_square.collidepoint(new_pos) or hallway.collidepoint(new_pos) or right_square.collidepoint(new_pos):
            return True  # Player is within the left square, hallway, or right square
        else:
            return False  # Player is outside the left square, hallway, and right square

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
        self.image = pygame.transform.rotozoom(pygame.image.load('images/bullet.png').convert_alpha(), 0, 1.5)
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


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, end):
    # Implement the A* algorithm
    heap = [(0, start)]
    visited = set()
    while heap:
        (cost, current) = heapq.heappop(heap)
        if current == end:
            path = []
            while current in grid:
                path.append(current)
                current = grid[current]
            return path[::-1]
        if current in visited:
            continue
        visited.add(current)
        for neighbor in neighbors(current):
            heapq.heappush(heap, (cost + 1 + heuristic(neighbor, end), neighbor))
            if neighbor not in grid or cost + 1 < grid[neighbor]:
                grid[neighbor] = cost + 1
                heapq.heappush(heap, (cost + 1, neighbor))
    return None


def neighbors(node):
    # Get neighboring nodes
    x, y = node
    return [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/yellow_ball.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.05)
        self.rect = self.image.get_rect()
        self.rect.center = self.get_random_position()
        self.grid_size = 15
        self.playable_area = self.create_playable_area()
        self.speed = 0.01

    def create_playable_area(self):
        # Create a 2D grid representation of the playable area
        grid = []
        for y in range(0, 700, self.grid_size):
            row = []
            for x in range(0, 800, self.grid_size):
                pos = pygame.math.Vector2(x, y)
                is_obstacle = not self.is_within_playable_area(pos)
                row.append(is_obstacle)
            grid.append(row)
        return grid

    def is_within_playable_area(self, position):
        # check if a position is within the playable area
        left_square = pygame.Rect(50, 110, 260, 430)
        hallway = pygame.Rect(310, 220, 180, 70)
        right_square = pygame.Rect(490, 110, 260, 430)
        return left_square.collidepoint(position) or hallway.collidepoint(position) or right_square.collidepoint(position)

    def draw_playable_area(self):
        # Draw the playable area for visualization purposes
        for y, row in enumerate(self.playable_area):
            for x, is_obstacle in enumerate(row):
                color = (255, 0, 0) if is_obstacle else (0, 255, 0)
                pygame.draw.rect(screen, color, (x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size), 1)

    def get_random_position(self, min_distance=200):
        while True:
            # Return a random position within the playable area grid
            x = random.randint(50, 740)
            y = random.randint(110, 590)

            # Calculate distance between player and enemy
            distance = math.hypot(x - player.pos.x, y - player.pos.y)

            # Check if the distance is greater than the minimum required
            if distance >= min_distance:
                return x, y

    def move_towards_player(self):
        # Implement A* pathfinding to find the path towards the player
        start = (self.rect.x // self.grid_size, self.rect.y // self.grid_size)
        end = (player.pos.x // self.grid_size, player.pos.y // self.grid_size)
        grid = {}
        path = astar(grid, start, end)

        if path:
            # Move towards the next node in the path
            next_node = path[0]
            new_x = next_node[0] * self.grid_size
            new_y = next_node[1] * self.grid_size

            # Check if the new position is within the playable area
            if self.is_within_playable_area((new_x, new_y)):
                self.rect.x += int((new_x - self.rect.x) * self.speed)
                self.rect.y += int((new_y - self.rect.y) * self.speed)


    def update(self):
        self.draw_playable_area()
        self.move_towards_player()


all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# CREATE INSTANCE OF PLAYER
player = Player()

all_sprites_group.add(player)

enemy = Enemy()
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

pygame.quit()
