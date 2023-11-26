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


# CREATE INSTANCE OF PLAYER
player = Player()

# GAME LOOP
running = True
while running:

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((0, 0, 0))

    # HANDLE EVENTS/ pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # RENDER PLAYER
    screen.blit(player.image, player.rect)
    # CALL FUNCTION TO UPDATE PLAYER STATE
    player.update()
    pygame.draw.rect(screen, "red", player.hitbox_rect, width=2)
    pygame.draw.rect(screen, "yellow", player.rect, width=2)


    pygame.display.update()
    clock.tick(60)  # limits FPS to 60

pygame.quit()
