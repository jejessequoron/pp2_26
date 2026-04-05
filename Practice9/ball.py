import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

RADIUS = 25
DIAMETER = 50
STEP = 20

ball_x = WIDTH // 2
ball_y = HEIGHT // 2

clock = pygame.time.Clock()

def can_move(new_x, new_y):
    return (
        RADIUS <= new_x <= WIDTH - RADIUS and
        RADIUS <= new_y <= HEIGHT - RADIUS
    )

def main():
    global ball_x, ball_y

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                new_x, new_y = ball_x, ball_y

                if event.key == pygame.K_LEFT:
                    new_x -= STEP
                elif event.key == pygame.K_RIGHT:
                    new_x += STEP
                elif event.key == pygame.K_UP:
                    new_y -= STEP
                elif event.key == pygame.K_DOWN:
                    new_y += STEP

                if can_move(new_x, new_y):
                    ball_x, ball_y = new_x, new_y

        screen.fill(WHITE)

        pygame.draw.circle(screen, RED, (ball_x, ball_y), RADIUS)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()