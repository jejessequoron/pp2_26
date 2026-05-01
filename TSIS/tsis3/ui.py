import pygame

WIDTH = 400

def draw_text_center(screen, text, y, text_font, color=(255, 255, 255)):
    image = text_font.render(text, True, color)
    rect = image.get_rect(center=(WIDTH // 2, y))
    screen.blit(image, rect)

def draw_button(screen, font_small, x, y, w, h, text):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (45, 60, 85), rect, border_radius=8)
    pygame.draw.rect(screen, (230, 235, 245), rect, 2, border_radius=8)
    image = font_small.render(text, True, (255, 255, 255))
    screen.blit(image, image.get_rect(center=rect.center))
    return rect

def draw_menu(screen, fonts, username):
    font_big, font, font_small = fonts
    screen.fill((20, 24, 34))
    draw_text_center(screen, "RACER", 100, font_big)
    draw_text_center(screen, "Type name and press Play", 155, font_small, (210, 220, 235))
    pygame.draw.rect(screen, (15, 18, 25), (80, 185, 240, 38), border_radius=8)
    name_image = font.render(username or "Player", True, (255, 255, 255))
    screen.blit(name_image, (95, 191))
    buttons = {
        "play": draw_button(screen, font_small, 115, 255, 170, 42, "Play"),
        "leaderboard": draw_button(screen, font_small, 115, 310, 170, 42, "Leaderboard"),
        "settings": draw_button(screen, font_small, 115, 365, 170, 42, "Settings"),
        "quit": draw_button(screen, font_small, 115, 420, 170, 42, "Quit"),
    }
    return buttons

def draw_leaderboard(screen, fonts, leaderboard):
    font_big, font, font_small = fonts
    screen.fill((20, 24, 34))
    draw_text_center(screen, "Top 10", 90, font)
    if not leaderboard:
        draw_text_center(screen, "No scores yet", 250, font_small)
    else:
        header = font_small.render("Rank Name        Score  Dist", True, (255, 255, 255))
        screen.blit(header, (55, 130))
        y = 165
        for index, row in enumerate(leaderboard[:10], 1):
            line = f"{index:<4} {row['name'][:10]:<10} {row['score']:<6} {row['distance']}m"
            screen.blit(font_small.render(line, True, (235, 235, 235)), (55, y))
            y += 30
    return {"back": draw_button(screen, font_small, 130, 510, 140, 42, "Back")}

def draw_settings(screen, fonts, settings, car_colors, difficulty_speed):
    font_big, font, font_small = fonts
    screen.fill((20, 24, 34))
    draw_text_center(screen, "Settings", 85, font)
    draw_text_center(screen, f"Sound: {'On' if settings['sound'] else 'Off'}", 145, font_small)
    draw_text_center(screen, f"Car: {settings['car_color'].title()}", 225, font_small)
    draw_text_center(screen, f"Difficulty: {settings['difficulty'].title()}", 320, font_small)
    buttons = {
        "sound": draw_button(screen, font_small, 130, 165, 140, 34, "Toggle Sound"),
        "back": draw_button(screen, font_small, 130, 510, 140, 42, "Back"),
    }
    x = 35
    for color in car_colors:
        buttons[color] = draw_button(screen, font_small, x, 245, 75, 34, color.title())
        x += 85
    x = 55
    for difficulty in difficulty_speed:
        buttons[difficulty] = draw_button(screen, font_small, x, 340, 85, 34, difficulty.title())
        x += 95
    return buttons

def draw_game_over(screen, fonts, game, username):
    font_big, font, font_small = fonts
    screen.fill((20, 24, 34))
    title = "Finished!" if game["finished"] else "Game Over"
    draw_text_center(screen, title, 110, font_big)
    draw_text_center(screen, f"Player: {username or 'Player'}", 200, font_small)
    draw_text_center(screen, f"Score: {game['score']}", 240, font_small)
    draw_text_center(screen, f"Distance: {int(game['distance'])}m", 280, font_small)
    draw_text_center(screen, f"Coins: {game['coins']}", 320, font_small)
    return {
        "retry": draw_button(screen, font_small, 80, 430, 110, 42, "Retry"),
        "menu": draw_button(screen, font_small, 210, 430, 120, 42, "Menu"),
    }