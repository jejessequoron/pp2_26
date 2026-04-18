import pygame
import sys
import math
import datetime

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpongeBob Clock")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MINUTE_COLOR = (60, 60, 60)
SECOND_COLOR = (200, 40, 40)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

CENTER = (WIDTH // 2, HEIGHT // 2)

sim = pygame.image.load("spongy.png").convert_alpha()
sim = pygame.transform.smoothscale(sim, (850, 700))

def draw_hand(surface, center, length, angle_deg, color, thickness):
    angle_rad = math.radians(angle_deg - 90)
    end_x = center[0] + math.cos(angle_rad) * length
    end_y = center[1] + math.sin(angle_rad) * length
    pygame.draw.line(surface, color, center, (end_x, end_y), thickness)

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        bg_rect = sim.get_rect(center=CENTER)
        screen.blit(sim, bg_rect)

        now = datetime.datetime.now()
        minute = now.minute
        second = now.second

        minute_angle = (minute / 60) * 360
        second_angle = (second / 60) * 360

        minute_length = 180
        second_length = 230

        draw_hand(screen, CENTER, minute_length, minute_angle, MINUTE_COLOR, 8)
        draw_hand(screen, CENTER, second_length, second_angle, SECOND_COLOR, 4)

        pygame.draw.circle(screen, BLACK, CENTER, 10)

        time_text = font.render(f"{minute:02}:{second:02}", True, BLACK)
        text_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(time_text, text_rect)

        pygame.display.flip()
        clock.tick(1)

if __name__ == "__main__":
    main()