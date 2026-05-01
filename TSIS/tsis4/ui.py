import pygame

WIDTH = 600
HEIGHT = 600
CELL = 30

colorWHITE = (255, 255, 255)
colorGRAY = (200, 200, 200)
colorBLACK = (0, 0, 0)
colorRED = (255, 0, 0)
colorGREEN = (0, 255, 0)
colorYELLOW = (255, 255, 0)
colorBLUE = (0, 100, 255)
colorDARK_RED = (120, 0, 0)
colorPURPLE = (160, 60, 255)
colorCYAN = (0, 220, 255)

def draw_grid(screen, settings):
    if not settings["grid"]:
        return
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, colorGRAY, (i * CELL, j * CELL, CELL, CELL), 1)

def draw_button(screen, font_small, rect, text):
    pygame.draw.rect(screen, colorBLACK, rect)
    pygame.draw.rect(screen, colorWHITE, rect, 2)
    image = font_small.render(text, True, colorWHITE)
    screen.blit(image, image.get_rect(center=rect.center))

def draw_center(screen, text, y, text_font, color=colorWHITE):
    image = text_font.render(text, True, color)
    screen.blit(image, image.get_rect(center=(WIDTH // 2, y)))

def draw_obstacles(screen, obstacles):
    for x, y in obstacles:
        pygame.draw.rect(screen, colorGRAY, (x * CELL, y * CELL, CELL, CELL))
        pygame.draw.rect(screen, colorBLACK, (x * CELL, y * CELL, CELL, CELL), 2)

def draw_menu(screen, fonts, username, menu_buttons):
    font, font_small, font_tiny, large_font = fonts
    draw_center(screen, "SNAKE GAME", 95, large_font, colorGREEN)
    draw_center(screen, "Username:", 160, font, colorWHITE)
    pygame.draw.rect(screen, colorBLACK, (180, 180, 240, 35))
    pygame.draw.rect(screen, colorWHITE, (180, 180, 240, 35), 2)
    name_text = font_small.render(username or "Player", True, colorWHITE)
    screen.blit(name_text, (190, 188))
    draw_button(screen, font_small, menu_buttons["play"], "Play")
    draw_button(screen, font_small, menu_buttons["leaderboard"], "Leaderboard")
    draw_button(screen, font_small, menu_buttons["settings"], "Settings")
    draw_button(screen, font_small, menu_buttons["quit"], "Quit")

def draw_game_over(screen, fonts, score, level, personal_best, game_over_buttons):
    font, font_small, font_tiny, large_font = fonts
    game_over_text = large_font.render("GAME OVER!", True, colorRED)
    score_text = font.render(f"Final Score: {score}", True, colorWHITE)
    level_text = font.render(f"Level Reached: {level}", True, colorWHITE)
    best_text = font.render(f"Personal Best: {personal_best}", True, colorYELLOW)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 120))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 55))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 15))
    screen.blit(best_text, (WIDTH // 2 - best_text.get_width() // 2, HEIGHT // 2 + 25))
    draw_button(screen, font_small, game_over_buttons["retry"], "Retry")
    draw_button(screen, font_small, game_over_buttons["menu"], "Main Menu")

def draw_leaderboard(screen, fonts, rows, back_button):
    font, font_small, font_tiny, large_font = fonts
    draw_center(screen, "LEADERBOARD", 60, large_font, colorGREEN)
    if not rows:
        draw_center(screen, "No scores yet", 280, font, colorWHITE)
    else:
        header = font_tiny.render("Rank  Username      Score  Level  Date", True, colorYELLOW)
        screen.blit(header, (55, 105))
        y = 140
        for i, row in enumerate(rows, start=1):
            username_db, score_db, level_db, date_db = row
            line = f"{i:<5} {username_db[:11]:<11} {score_db:<6} {level_db:<6} {date_db}"
            text = font_tiny.render(line, True, colorWHITE)
            screen.blit(text, (55, y))
            y += 34
    draw_button(screen, font_small, back_button, "Back")

def draw_settings(screen, fonts, settings, settings_color, save_back_button):
    font, font_small, font_tiny, large_font = fonts
    draw_center(screen, "SETTINGS", 60, large_font, colorGREEN)
    grid_button = pygame.Rect(210, 160, 180, 35)
    sound_button = pygame.Rect(210, 210, 180, 35)
    draw_button(screen, font_small, grid_button, f"Grid: {'On' if settings['grid'] else 'Off'}")
    draw_button(screen, font_small, sound_button, f"Sound: {'On' if settings['sound'] else 'Off'}")
    draw_center(screen, f"Snake color RGB: {settings_color}", 270, font_small, colorWHITE)
    labels = ["R", "G", "B"]
    for i, label in enumerate(labels):
        y = 295 + i * 45
        minus_button = pygame.Rect(220, y, 35, 35)
        plus_button = pygame.Rect(345, y, 35, 35)
        value_rect = pygame.Rect(265, y, 70, 35)
        draw_button(screen, font_small, minus_button, "-")
        draw_button(screen, font_small, plus_button, "+")
        pygame.draw.rect(screen, colorBLACK, value_rect)
        pygame.draw.rect(screen, colorWHITE, value_rect, 2)
        label_text = font_small.render(label, True, colorWHITE)
        value_text = font_small.render(str(settings_color[i]), True, colorWHITE)
        screen.blit(label_text, (180, y + 6))
        screen.blit(value_text, value_text.get_rect(center=value_rect.center))
    preview_rect = pygame.Rect(420, 330, 40, 40)
    pygame.draw.rect(screen, tuple(settings_color), preview_rect)
    pygame.draw.rect(screen, colorWHITE, preview_rect, 2)
    draw_button(screen, font_small, save_back_button, "Save & Back")