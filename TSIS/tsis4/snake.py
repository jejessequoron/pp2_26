import random
import sys
import pygame
from persistence import (
    connect_db,
    get_personal_best,
    get_top_scores,
    load_settings,
    save_result,
    save_settings,
)
from ui import (
    CELL,
    colorBLACK,
    colorBLUE,
    colorCYAN,
    colorDARK_RED,
    colorGRAY,
    colorGREEN,
    colorPURPLE,
    colorRED,
    colorWHITE,
    colorYELLOW,
    draw_game_over,
    draw_grid,
    draw_leaderboard,
    draw_menu,
    draw_obstacles,
    draw_settings,
)

pygame.init()
pygame.font.init()

WIDTH = 600
HEIGHT = 600
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 26)
font_tiny = pygame.font.SysFont(None, 22)
large_font = pygame.font.SysFont(None, 48)
fonts = (font, font_small, font_tiny, large_font)
settings = load_settings()
conn = connect_db()

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.grow_count = 0

    def next_head(self):
        return Point(self.body[0].x + self.dx, self.body[0].y + self.dy)

    def move(self):
        new_head = self.next_head()
        self.body.insert(0, new_head)
        if self.grow_count > 0:
            self.grow_count -= 1
        else:
            self.body.pop()

    def grow(self, amount):
        self.grow_count += amount

    def shorten(self, amount):
        for _ in range(amount):
            if len(self.body) > 1:
                self.body.pop()

    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, colorRED, (head.x * CELL, head.y * CELL, CELL, CELL))
        snake_color = tuple(settings["snake_color"])
        for segment in self.body[1:]:
            pygame.draw.rect(screen, snake_color, (segment.x * CELL, segment.y * CELL, CELL, CELL))

class Food:
    def __init__(self, poison=False):
        self.pos = Point(9, 9)
        self.poison = poison
        self.weight = random.randint(1, 3)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000

    def draw(self):
        if self.poison:
            color = colorDARK_RED
            text_value = "X"
        elif self.weight == 1:
            color = colorGREEN
            text_value = str(self.weight)
        elif self.weight == 2:
            color = colorBLUE
            text_value = str(self.weight)
        else:
            color = colorRED
            text_value = str(self.weight)
        pygame.draw.rect(screen, color, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))
        text = font.render(text_value, True, colorWHITE)
        screen.blit(text, (self.pos.x * CELL + 8, self.pos.y * CELL))

    def generate_random_pos(self, snake_body, obstacles, other_positions=None):
        if other_positions is None:
            other_positions = []
        while True:
            self.pos.x = random.randint(0, COLS - 1)
            self.pos.y = random.randint(0, ROWS - 1)
            pos = (self.pos.x, self.pos.y)
            on_snake = False
            for segment in snake_body:
                if self.pos.x == segment.x and self.pos.y == segment.y:
                    on_snake = True
                    break
            if not on_snake and pos not in obstacles and pos not in other_positions:
                break
        self.weight = random.randint(1, 3)
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

class PowerUp:
    def __init__(self):
        self.pos = Point(0, 0)
        self.kind = random.choice(["speed", "slow", "shield"])
        self.spawn_time = 0
        self.visible = False
        self.lifetime = 8000

    def generate_random_pos(self, snake_body, obstacles, other_positions):
        while True:
            self.pos.x = random.randint(0, COLS - 1)
            self.pos.y = random.randint(0, ROWS - 1)
            pos = (self.pos.x, self.pos.y)
            on_snake = False
            for segment in snake_body:
                if self.pos.x == segment.x and self.pos.y == segment.y:
                    on_snake = True
                    break
            if not on_snake and pos not in obstacles and pos not in other_positions:
                break
        self.kind = random.choice(["speed", "slow", "shield"])
        self.spawn_time = pygame.time.get_ticks()
        self.visible = True

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime

    def draw(self):
        if not self.visible:
            return
        if self.kind == "speed":
            color = colorCYAN
            letter = "B"
        elif self.kind == "slow":
            color = colorPURPLE
            letter = "S"
        else:
            color = colorYELLOW
            letter = "O"
        pygame.draw.rect(screen, color, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))
        text = font.render(letter, True, colorBLACK)
        screen.blit(text, (self.pos.x * CELL + 8, self.pos.y * CELL))

def cell_list(snake_body):
    result = []
    for segment in snake_body:
        result.append((segment.x, segment.y))
    return result

def safe_obstacle_spawn(snake, new_obstacles):
    head = snake.body[0]
    free = 0
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for dx, dy in directions:
        x = head.x + dx
        y = head.y + dy
        if 0 <= x < COLS and 0 <= y < ROWS:
            if (x, y) not in new_obstacles:
                free += 1
    return free >= 2

def generate_obstacles(level, snake):
    if level < 3:
        return set()
    count = min(22, level * 3)
    snake_cells = cell_list(snake.body)
    for _ in range(100):
        obstacles = set()
        while len(obstacles) < count:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if (x, y) not in snake_cells:
                if abs(x - snake.body[0].x) + abs(y - snake.body[0].y) > 2:
                    obstacles.add((x, y))
        if safe_obstacle_spawn(snake, obstacles):
            return obstacles
    return set()

def start_new_game():
    new_snake = Snake()
    new_food = Food()
    new_poison = Food(poison=True)
    new_power = PowerUp()
    new_obstacles = set()
    new_food.generate_random_pos(new_snake.body, new_obstacles)
    new_poison.generate_random_pos(
        new_snake.body,
        new_obstacles,
        [(new_food.pos.x, new_food.pos.y)],
    )
    return new_snake, new_food, new_poison, new_power, new_obstacles

menu_buttons = {
    "play": pygame.Rect(210, 230, 180, 40),
    "leaderboard": pygame.Rect(210, 285, 180, 40),
    "settings": pygame.Rect(210, 340, 180, 40),
    "quit": pygame.Rect(210, 395, 180, 40),
}
game_over_buttons = {
    "retry": pygame.Rect(150, 405, 130, 40),
    "menu": pygame.Rect(320, 405, 130, 40),
}
back_button = pygame.Rect(230, 520, 140, 40)
save_back_button = pygame.Rect(205, 520, 190, 40)

FPS = 5
clock = pygame.time.Clock()
snake, food, poison_food, powerup, obstacles = start_new_game()
username = ""
personal_best = 0
score = 0
level = 1
foods_eaten = 0
foods_to_next_level = 4
game_saved = False
screen_name = "menu"
active_power = None
power_end_time = 0
shield_ready = False
next_powerup_time = pygame.time.get_ticks() + 5000
settings_color = settings["snake_color"][:]
running = True

while running:
    now = pygame.time.get_ticks()
    current_fps = FPS
    if active_power == "speed":
        current_fps += 5
        if now > power_end_time:
            active_power = None
    elif active_power == "slow":
        current_fps = max(3, current_fps - 3)
        if now > power_end_time:
            active_power = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if screen_name == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN:
                    if username.strip() == "":
                        username = "Player"
                    personal_best = get_personal_best(conn, username)
                    snake, food, poison_food, powerup, obstacles = start_new_game()
                    score = 0
                    level = 1
                    FPS = 5
                    foods_eaten = 0
                    active_power = None
                    shield_ready = False
                    game_saved = False
                    screen_name = "game"
                elif event.unicode and event.unicode.isprintable() and len(username) < 14:
                    username += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_buttons["play"].collidepoint(event.pos):
                    if username.strip() == "":
                        username = "Player"
                    personal_best = get_personal_best(conn, username)
                    snake, food, poison_food, powerup, obstacles = start_new_game()
                    score = 0
                    level = 1
                    FPS = 5
                    foods_eaten = 0
                    active_power = None
                    shield_ready = False
                    game_saved = False
                    screen_name = "game"
                elif menu_buttons["leaderboard"].collidepoint(event.pos):
                    screen_name = "leaderboard"
                elif menu_buttons["settings"].collidepoint(event.pos):
                    settings_color = settings["snake_color"][:]
                    screen_name = "settings"
                elif menu_buttons["quit"].collidepoint(event.pos):
                    running = False
        elif screen_name == "game":
            if event.type == pygame.KEYDOWN:
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
        elif screen_name == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over_buttons["retry"].collidepoint(event.pos):
                    personal_best = get_personal_best(conn, username)
                    snake, food, poison_food, powerup, obstacles = start_new_game()
                    score = 0
                    level = 1
                    FPS = 5
                    foods_eaten = 0
                    active_power = None
                    shield_ready = False
                    game_saved = False
                    screen_name = "game"
                elif game_over_buttons["menu"].collidepoint(event.pos):
                    screen_name = "menu"
        elif screen_name == "leaderboard":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    screen_name = "menu"
        elif screen_name == "settings":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                grid_button = pygame.Rect(210, 160, 180, 35)
                sound_button = pygame.Rect(210, 210, 180, 35)
                if grid_button.collidepoint(event.pos):
                    settings["grid"] = not settings["grid"]
                elif sound_button.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                for i in range(3):
                    y = 295 + i * 45
                    minus_button = pygame.Rect(220, y, 35, 35)
                    plus_button = pygame.Rect(345, y, 35, 35)
                    if minus_button.collidepoint(event.pos):
                        settings_color[i] = max(0, settings_color[i] - 15)
                    if plus_button.collidepoint(event.pos):
                        settings_color[i] = min(255, settings_color[i] + 15)
                if save_back_button.collidepoint(event.pos):
                    settings["snake_color"] = settings_color[:]
                    save_settings(settings)
                    screen_name = "menu"
    screen.fill(colorBLACK)
    if screen_name == "menu":
        draw_menu(screen, fonts, username, menu_buttons)
    elif screen_name == "game":
        next_head = snake.next_head()
        hit_wall = (
            next_head.x >= COLS
            or next_head.x < 0
            or next_head.y >= ROWS
            or next_head.y < 0
        )
        hit_self = False
        for segment in snake.body[1:]:
            if next_head.x == segment.x and next_head.y == segment.y:
                hit_self = True
                break
        hit_obstacle = (next_head.x, next_head.y) in obstacles
        if hit_wall or hit_self or hit_obstacle:
            if active_power == "shield" and shield_ready:
                shield_ready = False
                active_power = None
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for dx, dy in directions:
                    test_x = snake.body[0].x + dx
                    test_y = snake.body[0].y + dy
                    safe = True
                    if test_x < 0 or test_x >= COLS or test_y < 0 or test_y >= ROWS:
                        safe = False

                    for segment in snake.body[1:]:
                        if test_x == segment.x and test_y == segment.y:
                            safe = False

                    if (test_x, test_y) in obstacles:
                        safe = False

                    if safe:
                        snake.dx = dx
                        snake.dy = dy
                        break
            else:
                if not game_saved:
                    save_result(conn, username, score, level)
                    personal_best = max(personal_best, score)
                    game_saved = True
                screen_name = "game_over"
        else:
            snake.move()
            if snake.body[0].x == food.pos.x and snake.body[0].y == food.pos.y:
                score += food.weight
                foods_eaten += 1
                snake.grow(food.weight)
                food.generate_random_pos(
                    snake.body,
                    obstacles,
                    [(poison_food.pos.x, poison_food.pos.y)],
                )
                if foods_eaten % foods_to_next_level == 0:
                    level += 1
                    FPS += 2
                    obstacles = generate_obstacles(level, snake)
                    food.generate_random_pos(
                        snake.body,
                        obstacles,
                        [(poison_food.pos.x, poison_food.pos.y)],
                    )
                    poison_food.generate_random_pos(
                        snake.body,
                        obstacles,
                        [(food.pos.x, food.pos.y)],
                    )
            if snake.body[0].x == poison_food.pos.x and snake.body[0].y == poison_food.pos.y:
                snake.shorten(2)
                poison_food.generate_random_pos(
                    snake.body,
                    obstacles,
                    [(food.pos.x, food.pos.y)],
                )
                if len(snake.body) <= 1:
                    if not game_saved:
                        save_result(conn, username, score, level)
                        personal_best = max(personal_best, score)
                        game_saved = True
                    screen_name = "game_over"
            if powerup.visible:
                if snake.body[0].x == powerup.pos.x and snake.body[0].y == powerup.pos.y:
                    if powerup.kind == "speed":
                        active_power = "speed"
                        power_end_time = pygame.time.get_ticks() + 5000
                    elif powerup.kind == "slow":
                        active_power = "slow"
                        power_end_time = pygame.time.get_ticks() + 5000
                    else:
                        active_power = "shield"
                        shield_ready = True
                    powerup.visible = False
                    next_powerup_time = pygame.time.get_ticks() + 8000
            if food.is_expired():
                food.generate_random_pos(
                    snake.body,
                    obstacles,
                    [(poison_food.pos.x, poison_food.pos.y)],
                )
            if powerup.visible and powerup.is_expired():
                powerup.visible = False
                next_powerup_time = pygame.time.get_ticks() + 5000
            if not powerup.visible and active_power is None and pygame.time.get_ticks() >= next_powerup_time:
                powerup.generate_random_pos(
                    snake.body,
                    obstacles,
                    [(food.pos.x, food.pos.y), (poison_food.pos.x, poison_food.pos.y)],
                )
        if screen_name == "game":
            draw_grid(screen, settings)
            draw_obstacles(screen, obstacles)
            snake.draw()
            food.draw()
            poison_food.draw()
            powerup.draw()
            score_text = font.render(
                f"Score: {score}   Level: {level}   Best: {personal_best}",
                True,
                colorWHITE,
            )
            screen.blit(score_text, (10, 10))
            if active_power == "speed":
                remain = max(0, power_end_time - pygame.time.get_ticks()) // 1000
                power_text = font_tiny.render(f"Speed boost: {remain}s", True, colorCYAN)
                screen.blit(power_text, (10, 45))
            elif active_power == "slow":
                remain = max(0, power_end_time - pygame.time.get_ticks()) // 1000
                power_text = font_tiny.render(f"Slow motion: {remain}s", True, colorPURPLE)
                screen.blit(power_text, (10, 45))
            elif active_power == "shield":
                power_text = font_tiny.render("Shield: ready", True, colorYELLOW)
                screen.blit(power_text, (10, 45))
    elif screen_name == "game_over":
        draw_game_over(screen, fonts, score, level, personal_best, game_over_buttons)
    elif screen_name == "leaderboard":
        rows = get_top_scores(conn)
        draw_leaderboard(screen, fonts, rows, back_button)
    elif screen_name == "settings":
        draw_settings(screen, fonts, settings, settings_color, save_back_button)
    pygame.display.flip()
    clock.tick(current_fps)
save_settings(settings)
conn.close()
pygame.quit()
sys.exit()