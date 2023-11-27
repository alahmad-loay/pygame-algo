import math
import pygame

# PYGAME INITIALIZE
pygame.init()

# CREATE SCREEN/WINDOW
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("shooter game thingy idk")
clock = pygame.time.Clock()


# LOAD IMAGES

# PLAYER
class Player(pygame.sprite.Sprite):
    # INITIAL CONSTRUCTOR
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(400, 500)
        self.image = pygame.transform.rotozoom(pygame.image.load('images/playerCharacter.png').convert_alpha(), 0, 0.3)
        # WHAT WE ROTATE FOR HIGHER QUALITY AND LESS BUGS
        self.base_player_image = self.image
        # TO CHECK HITBOX
        self.hitbox_rect = self.base_player_image.get_rect(center=self.pos)
        # TO DRAW PLAYER ON SCREEN
        self.rect = self.hitbox_rect.copy()
        # for bullet
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(3, 2) # ill come back to it

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
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    # UPDATE PLAYER STATE
    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_angle): # change x,y name
        super().__init__()
        self.image = pygame.transform.rotozoom(pygame.image.load('images/bullet.png').convert_alpha(), 0, 2)
        self.rect = self.image.get_rect() #fix name later
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.speed = 30
        self.bullet_angle = bullet_angle - 90
        self.x_vel = math.cos(self.bullet_angle * (2*math.pi/360)) * self.speed # change name later
        self.y_vel = math.sin(self.bullet_angle * (2*math.pi/360)) * self.speed #here too
        self.bullet_lifetime = 750
        self.spawn_time = pygame.time.get_ticks() # time bullet was created
    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()  # if timer - the timer for the bullet creation is grater than bullet lifetime -  KILL IT

    def update_movement(self):
        self.bullet_movement()



# CREATE INSTANCE OF PLAYER
player = Player()

all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

all_sprites_group.add(player)

# GAME LOOP
running = True
while running:

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((245, 245, 220))

    # HANDLE EVENTS/ pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # # RENDER PLAYER
    # screen.blit(player.image, player.rect)
    # # CALL FUNCTION TO UPDATE PLAYER STATE
    # player.update()
    pygame.draw.rect(screen, "red", player.hitbox_rect, width=2)
    pygame.draw.rect(screen, "yellow", player.rect, width=2)

    for bullet in bullet_group.sprites():
        bullet.update_movement()

    all_sprites_group.draw(screen)
    all_sprites_group.update()

    pygame.display.update()
    clock.tick(60)  # limits FPS to 60

pygame.quit()
