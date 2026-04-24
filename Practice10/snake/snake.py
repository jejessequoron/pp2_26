import pygame
import random
import sys

pygame.init()
pygame.font.init()

WIDTH = 600
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

colorWHITE = (255, 255, 255)
colorGRAY = (200, 200, 200)
colorBLACK = (0, 0, 0)
colorRED = (255, 0, 0)
colorGREEN = (0, 255, 0)
colorYELLOW = (255, 255, 0)

CELL = 30
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 48)

def draw_grid():
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, colorGRAY, (i * CELL, j * CELL, CELL, CELL), 1)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        head = self.body[0]
        if head.x >= WIDTH // CELL or head.x < 0 or head.y >= HEIGHT // CELL or head.y < 0:
            return False 

        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                return False 
        return True

    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, colorRED, (head.x * CELL, head.y * CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, colorYELLOW, (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def check_collision(self, food):
        head = self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            self.body.append(Point(self.body[-1].x, self.body[-1].y))
            return True
        return False

class Food:
    def __init__(self):
        self.pos = Point(9, 9)

    def draw(self):
        pygame.draw.rect(screen, colorGREEN, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

    def generate_random_pos(self, snake_body):
        while True:
            self.pos.x = random.randint(0, (WIDTH // CELL) - 1)
            self.pos.y = random.randint(0, (HEIGHT // CELL) - 1)
            
            on_snake = False
            for segment in snake_body:
                if self.pos.x == segment.x and self.pos.y == segment.y:
                    on_snake = True
                    break
            
            if not on_snake:
                break 

FPS = 5
clock = pygame.time.Clock()

food = Food()
snake = Snake()

score = 0
level = 1
foods_to_next_level = 4 

food.generate_random_pos(snake.body)

running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_RIGHT and snake.dx != -1:
                    snake.dx = 1
                    snake.dy = 0
                elif event.key == pygame.K_LEFT and snake.dx != 1:
                    snake.dx = -1
                    snake.dy = 0
                elif event.key == pygame.K_DOWN and snake.dy != -1:
                    snake.dx = 0
                    snake.dy = 1
                elif event.key == pygame.K_UP and snake.dy != 1:
                    snake.dx = 0
                    snake.dy = -1
            else:
                if event.key == pygame.K_SPACE:
                    snake = Snake()
                    score = 0
                    level = 1
                    FPS = 5
                    game_over = False
                    food.generate_random_pos(snake.body)

    screen.fill(colorBLACK)

    if not game_over:
        if not snake.move():
            game_over = True
            
        if snake.check_collision(food):
            score += 1
            food.generate_random_pos(snake.body)
            if score % foods_to_next_level == 0:
                level += 1
                FPS += 2 
        draw_grid()
        snake.draw()
        food.draw()
        score_text = font.render(f"Score: {score}   Level: {level}", True, colorWHITE)
        screen.blit(score_text, (10, 10))

    else:
        game_over_text = large_font.render("GAME OVER!", True, colorRED)
        score_text = font.render(f"Final Score: {score}", True, colorWHITE)
        play_again_text = font.render("Press SPACE to Play Again", True, colorYELLOW)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()