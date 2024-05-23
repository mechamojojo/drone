import pygame
import random

# Initialize the game
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE_SKY = (135, 206, 235)  # Define a blue sky color

# Load images
# Update the path to include the 'images' folder
BIRD_IMAGE = pygame.image.load('images/drone.png')
BIRD_IMAGE = pygame.transform.scale(BIRD_IMAGE, (90, 70))
PIPE_IMAGE = pygame.image.load('images/pipe.png')
PIPE_IMAGE = pygame.transform.scale(PIPE_IMAGE, (100, 500))
FLOOR_IMAGE = pygame.image.load('images/floor.png')  # Load the floor image
FLOOR_HEIGHT = FLOOR_IMAGE.get_height()
CLOUD_IMAGE = pygame.image.load('images/cloud.png')  # Load the cloud image
# Scale the cloud image to be smaller
CLOUD_IMAGE = pygame.transform.scale(CLOUD_IMAGE, (180, 90))
BILLBOARD_IMAGE = pygame.image.load(
    'images/billboard.png')  # Load the billboard image
# Scale the billboard image to a reasonable size
BILLBOARD_IMAGE = pygame.transform.scale(BILLBOARD_IMAGE, (700, 350))


# Game variables
bird_x = 50
bird_y = 300
bird_velocity = 0
gravity = 0.5
jump_height = -7
pipe_gap = 190
pipe_velocity = -5
pipe_frequency = 1500  # in milliseconds
score = 0
rotation_angle = 0  # Initial rotation angle of the drone
clouds = []  # List to hold cloud objects
billboard = None  # To hold the billboard object
billboard_timer = 0  # Timer to control billboard appearance

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Drone")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Pipe class


class Pipe:
    def __init__(self, x, height, passed=False):
        self.x = x
        self.height = height
        self.top = self.height - PIPE_IMAGE.get_height()
        self.bottom = self.height + pipe_gap
        self.passed = passed

    def move(self):
        self.x += pipe_velocity

    def draw(self, screen):
        screen.blit(PIPE_IMAGE, (self.x, self.top))
        screen.blit(pygame.transform.flip(
            PIPE_IMAGE, False, True), (self.x, self.bottom))

    def collide(self, bird_rect):
        top_pipe_rect = pygame.Rect(
            self.x, self.top, PIPE_IMAGE.get_width(), PIPE_IMAGE.get_height())
        bottom_pipe_rect = pygame.Rect(
            self.x, self.bottom, PIPE_IMAGE.get_width(), PIPE_IMAGE.get_height())
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)

    # Cloud class


class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = random.uniform(-1, -0.5)  # Cloud velocity

    def move(self):
        self.x += self.velocity

    def draw(self, screen):
        screen.blit(CLOUD_IMAGE, (self.x, self.y))

    # Billboard class


class Billboard:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - FLOOR_HEIGHT - \
            BILLBOARD_IMAGE.get_height() - 0  # Lower position
        self.velocity = pipe_velocity / 2  # Billboard moves slower than pipes

    def move(self):
        self.x += self.velocity

    def draw(self, screen):
        screen.blit(BILLBOARD_IMAGE, (self.x, self.y))


# Function to reset the game


def reset_game():
    global bird_y, bird_velocity, pipes, score, pipe_velocity, rotation_angle, clouds, billboard, billboard_timer
    bird_y = 300
    bird_velocity = 0
    pipes = [Pipe(SCREEN_WIDTH + 100, random.randint(100, 400))]
    score = 0
    pipe_velocity = -3  # Reset pipe velocity
    rotation_angle = 0  # Reset rotation angle
    clouds = [Cloud(random.randint(0, SCREEN_WIDTH), random.randint(
        0, SCREEN_HEIGHT - FLOOR_HEIGHT - 100)) for _ in range(5)]  # Reset clouds
    billboard = None  # Reset billboard
    # Randomize the initial time for the first billboard appearance
    billboard_timer = random.randint(100, 200)


# Function to display the score


def display_score(score):
    font = pygame.font.Font(None, 36)
    text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(text, (10, 10))

# Function to rotate the drone


def get_rotated_image(image, angle):
    return pygame.transform.rotate(image, angle)


# Game loop
running = True
pipes = [Pipe(SCREEN_WIDTH + 100, random.randint(100, 400))]
reset_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_velocity = jump_height

    # Update bird position
    bird_velocity += gravity
    bird_y += bird_velocity

    # Update rotation angle based on velocity
    if bird_velocity < 0:
        rotation_angle = min(bird_velocity * -2, 5)  # Rotate up to 45 degrees
    else:
        # Rotate up to -45 degrees
        rotation_angle = max(bird_velocity * 0, -5)

    # Update pipes
    for pipe in pipes:
        pipe.move()
        if pipe.x + PIPE_IMAGE.get_width() < 0:
            pipes.remove(pipe)
        if not pipe.passed and pipe.x < bird_x:
            pipe.passed = True
            score += 1

    if pipes[-1].x < SCREEN_WIDTH - 300:
        pipes.append(Pipe(SCREEN_WIDTH, random.randint(100, 400)))

        # Update clouds
    for cloud in clouds:
        cloud.move()
        if cloud.x + CLOUD_IMAGE.get_width() < 0:
            cloud.x = SCREEN_WIDTH
            cloud.y = random.randint(0, SCREEN_HEIGHT - FLOOR_HEIGHT - 0)

    # Update billboard
    if billboard_timer > 0:
        billboard_timer -= 1
    else:
        if billboard is None:
            billboard = Billboard()  # Create a new billboard

    if billboard:
        billboard.move()
        if billboard.x + BILLBOARD_IMAGE.get_width() < 0:
            billboard = None
            # Set timer for next billboard appearance
            billboard_timer = random.randint(500, 1000)

    # Check for collisions
    bird_rect = pygame.Rect(
        bird_x, bird_y, BIRD_IMAGE.get_width(), BIRD_IMAGE.get_height())
    collision = any(pipe.collide(bird_rect) for pipe in pipes)

    # Check for game over conditions
    if bird_y > SCREEN_HEIGHT - FLOOR_HEIGHT or bird_y < 0 or collision:
        reset_game()

    # Increase pipe speed based on score
    pipe_velocity = -5 - (score // 5)  # Increase speed every 5 points

    # Draw clouds
    for cloud in clouds:
        cloud.draw(screen)  # Draw the clouds behind the pipes

    # Draw everything
    screen.fill(BLUE_SKY)  # Fill the background with blue sky color
    for cloud in clouds:
        cloud.draw(screen)  # Draw the clouds behind the pipe
        # Draw billboard if it exists
    if billboard:
        billboard.draw(screen)  # Draw the billboard behind the pipes
    for pipe in pipes:
        pipe.draw(screen)  # Draw the pipes
    rotated_bird_image = get_rotated_image(
        BIRD_IMAGE, rotation_angle)  # Rotate the bird (drone) image
    # Draw the rotated bird (drone) on top of the background and pipes
    screen.blit(rotated_bird_image, (bird_x, bird_y))

    # Draw the floor image
    screen.blit(FLOOR_IMAGE, (0, SCREEN_HEIGHT - FLOOR_HEIGHT))

    display_score(score)  # Draw the score on top of everything

    pygame.display.update()
    clock.tick(30)

pygame.quit()
