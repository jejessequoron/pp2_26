import random
import sys
import pygame
from persistence import load_leaderboard, load_settings, save_score, save_settings
from ui import draw_game_over, draw_leaderboard, draw_menu, draw_settings

pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 60
FINISH_DISTANCE = 5000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Verdana", 40, bold=True)
font = pygame.font.SysFont("Verdana", 22)
font_small = pygame.font.SysFont("Verdana", 15)
fonts = (font_big, font, font_small)

background = pygame.image.load("AnimatedStreet.png")
image_player = pygame.image.load("invincible.jpg")
image_enemy = pygame.image.load("conquest.jpg")

pygame.mixer.music.load("background.wav")
crash_sound = pygame.mixer.Sound("crash.wav")

settings = load_settings()
leaderboard = load_leaderboard()

if settings["sound"]:
    pygame.mixer.music.play(-1)

lanes = [70, 150, 230, 310]

difficulty_speed = {
    "easy": 4,
    "normal": 5,
    "hard": 6,
}
difficulty_spawn = {
    "easy": 1200,
    "normal": 900,
    "hard": 650,
}
car_colors = {
    "red": (220, 50, 50),
    "blue": (50, 110, 230),
    "green": (40, 180, 90),
    "yellow": (240, 210, 40),
}

def make_player_image():
    image = image_player.copy()
    tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint.fill((*car_colors[settings["car_color"]], 60))
    image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return image

def make_coin():
    weight = random.choice([1, 1, 2, 2, 3])
    size = 18 + weight * 5
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    colors = {
        1: (255, 215, 0),
        2: (255, 128, 0),
        3: (236, 45, 24),
    }
    pygame.draw.circle(image, colors[weight], (size // 2, size // 2), size // 2)
    label = font_small.render(str(weight), True, (40, 25, 5))
    image.blit(label, label.get_rect(center=(size // 2, size // 2)))
    return image, weight

def make_obstacle(kind):
    image = pygame.Surface((60, 32), pygame.SRCALPHA)
    if kind == "oil":
        pygame.draw.ellipse(image, (15, 15, 25), (4, 4, 52, 24))
    else:
        pygame.draw.rect(image, (210, 60, 45), (0, 3, 60, 26), border_radius=4)
        pygame.draw.line(image, (255, 230, 80), (5, 28), (22, 4), 5)
        pygame.draw.line(image, (255, 230, 80), (35, 28), (52, 4), 5)
    return image

def make_powerup(kind):
    image = pygame.Surface((34, 34), pygame.SRCALPHA)
    colors = {
        "nitro": (40, 190, 255),
        "shield": (120, 120, 255),
        "repair": (0, 255, 67),
    }
    labels = {
        "nitro": "N",
        "shield": "S",
        "repair": "R",
    }
    pygame.draw.circle(image, colors[kind], (17, 17), 16)
    pygame.draw.circle(image, (255, 255, 255), (17, 17), 16, 2)
    label = font_small.render(labels[kind], True, (10, 20, 35))
    image.blit(label, label.get_rect(center=(17, 17)))
    return image

def new_game():
    player = make_player_image()
    player_rect = player.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 20)
    return {
        "player": player,
        "player_rect": player_rect,
        "items": [],
        "speed": difficulty_speed[settings["difficulty"]],
        "spawn_delay": difficulty_spawn[settings["difficulty"]],
        "last_spawn": pygame.time.get_ticks(),
        "road_y": 0,
        "score": 0,
        "coins": 0,
        "distance": 0,
        "active_power": None,
        "power_end": 0,
        "shield": False,
        "slow_end": 0,
        "finished": False,
    }

def add_item(game):
    lane = random.choice(lanes)
    y = random.randint(-150, -40)
    roll = random.random()
    if roll < 0.45:
        image = image_enemy
        kind = "traffic"
        value = None
    elif roll < 0.7:
        image, value = make_coin()
        kind = "coin"
    elif roll < 0.9:
        value = random.choice(["barrier", "oil"])
        image = make_obstacle(value)
        kind = "obstacle"
    else:
        if game["active_power"] is None:
            value = random.choice(["nitro", "shield", "repair"])
            image = make_powerup(value)
            kind = "powerup"
        else:
            image, value = make_coin()
            kind = "coin"
    rect = image.get_rect(centerx=lane, bottom=y)
    game["items"].append(
        {
            "kind": kind,
            "image": image,
            "rect": rect,
            "value": value,
            "created": pygame.time.get_ticks(),
        }
    )

def use_powerup(game, power):
    now = pygame.time.get_ticks()
    if power == "repair":
        for item in game["items"]:
            if item["kind"] == "obstacle":
                game["items"].remove(item)
                break
        game["score"] += 75
        return
    if game["active_power"] is not None:
        return
    game["active_power"] = power
    if power == "nitro":
        game["power_end"] = now + 4000
        game["score"] += 100
    elif power == "shield":
        game["shield"] = True
        game["power_end"] = 0
        game["score"] += 60

def shield_blocks_crash(game):
    if game["active_power"] == "shield" and game["shield"]:
        game["active_power"] = None
        game["shield"] = False
        game["score"] += 50
        return True
    return False

def update_game(game, dt, username):
    now = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        game["player_rect"].x -= 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        game["player_rect"].x += 5
    game["player_rect"].left = max(40, game["player_rect"].left)
    game["player_rect"].right = min(360, game["player_rect"].right)
    speed = game["speed"] + game["distance"] / 1500
    if game["active_power"] == "nitro":
        speed *= 1.6
        if now >= game["power_end"]:
            game["active_power"] = None
    if now < game["slow_end"]:
        speed *= 0.55
    game["distance"] += speed * dt * 8
    game["score"] = int(game["distance"] // 20) + game["coins"] * 25
    spawn_delay = max(350, game["spawn_delay"] - int(game["distance"] / 20))
    if now - game["last_spawn"] > spawn_delay:
        add_item(game)
        game["last_spawn"] = now
    for item in game["items"][:]:
        item["rect"].y += speed
        if item["kind"] == "powerup" and now - item["created"] > 8000:
            game["items"].remove(item)
            continue
        if item["rect"].top > HEIGHT:
            game["items"].remove(item)
            continue
        if not item["rect"].colliderect(game["player_rect"]):
            continue
        if item["kind"] == "coin":
            game["coins"] += item["value"]
            if game["coins"] % 5 == 0:
                game["speed"] += 0.3
            game["items"].remove(item)
        elif item["kind"] == "powerup":
            use_powerup(game, item["value"])
            game["items"].remove(item)
        elif item["kind"] == "traffic":
            if shield_blocks_crash(game):
                game["items"].remove(item)
            else:
                if settings["sound"]:
                    crash_sound.play()
                save_score(leaderboard, username or "Player", game["score"], game["distance"], game["coins"])
                return "game_over"
        elif item["kind"] == "obstacle":
            if item["value"] == "oil":
                game["slow_end"] = now + 1800
                game["items"].remove(item)
            elif shield_blocks_crash(game):
                game["items"].remove(item)
            else:
                if settings["sound"]:
                    crash_sound.play()
                save_score(leaderboard, username or "Player", game["score"], game["distance"], game["coins"])
                return "game_over"
    if game["distance"] >= FINISH_DISTANCE:
        game["finished"] = True
        save_score(leaderboard, username or "Player", game["score"], game["distance"], game["coins"])
        return "game_over"
    return "play"

def draw_game(game):
    now = pygame.time.get_ticks()
    speed = game["speed"] + game["distance"] / 1500
    game["road_y"] = (game["road_y"] + speed) % HEIGHT
    screen.blit(background, (0, game["road_y"] - HEIGHT))
    screen.blit(background, (0, game["road_y"]))
    for item in game["items"]:
        screen.blit(item["image"], item["rect"])
    screen.blit(game["player"], game["player_rect"])
    left = max(0, FINISH_DISTANCE - int(game["distance"]))
    hud = [
        f"Score: {game['score']}",
        f"Coins: {game['coins']}",
        f"Dist: {int(game['distance'])}m",
        f"Left: {left}m",
    ]
    for i, line in enumerate(hud):
        screen.blit(font_small.render(line, True, (10, 10, 10)), (8, 8 + i * 18))
    power = "Power: none"
    if game["active_power"] == "nitro":
        seconds = max(0, game["power_end"] - now) / 1000
        power = f"Power: nitro {seconds:.1f}s"
    elif game["active_power"] == "shield":
        power = "Power: shield"
    text = font_small.render(power, True, (10, 10, 10))
    screen.blit(text, (WIDTH - text.get_width() - 8, 8))
screen_name = "menu"
username = ""
game = None
buttons = {}
running = True

while running:
    dt = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if screen_name == "menu" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            elif event.key == pygame.K_RETURN:
                game = new_game()
                screen_name = "play"
            elif event.unicode and event.unicode.isprintable() and len(username) < 14:
                username += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if screen_name == "menu":
                if buttons["play"].collidepoint(event.pos):
                    game = new_game()
                    screen_name = "play"
                elif buttons["leaderboard"].collidepoint(event.pos):
                    screen_name = "leaderboard"
                elif buttons["settings"].collidepoint(event.pos):
                    screen_name = "settings"
                elif buttons["quit"].collidepoint(event.pos):
                    running = False
            elif screen_name == "leaderboard":
                if buttons["back"].collidepoint(event.pos):
                    screen_name = "menu"
            elif screen_name == "settings":
                if buttons["sound"].collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                    if settings["sound"]:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
                    save_settings(settings)
                elif buttons["back"].collidepoint(event.pos):
                    screen_name = "menu"
                else:
                    for color in car_colors:
                        if buttons[color].collidepoint(event.pos):
                            settings["car_color"] = color
                            save_settings(settings)
                    for difficulty in difficulty_speed:
                        if buttons[difficulty].collidepoint(event.pos):
                            settings["difficulty"] = difficulty
                            save_settings(settings)
            elif screen_name == "game_over":
                if buttons["retry"].collidepoint(event.pos):
                    game = new_game()
                    screen_name = "play"
                elif buttons["menu"].collidepoint(event.pos):
                    screen_name = "menu"
    if screen_name == "play":
        screen_name = update_game(game, dt, username)
        if screen_name == "play":
            draw_game(game)
    elif screen_name == "menu":
        buttons = draw_menu(screen, fonts, username)
    elif screen_name == "leaderboard":
        buttons = draw_leaderboard(screen, fonts, leaderboard)
    elif screen_name == "settings":
        buttons = draw_settings(screen, fonts, settings, car_colors, difficulty_speed)
    elif screen_name == "game_over":
        buttons = draw_game_over(screen, fonts, game, username)
    pygame.display.flip()
save_settings(settings)
pygame.quit()
sys.exit()