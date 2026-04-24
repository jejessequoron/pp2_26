import pygame
import random
import time
import sys

pygame.init()

WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Dodge & Coin Collector")

image_background = pygame.image.load('AnimatedStreet.png')
image_player = pygame.image.load('invincible.jpg')
image_enemy = pygame.image.load('conquest.jpg')

pygame.mixer.music.load('background.wav')
pygame.mixer.music.play(-1)
sound_crash = pygame.mixer.Sound('crash.wav')

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
image_game_over = font.render("Game Over", True, "black")
image_game_over_rect = image_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2))

SPEED = 5
SCORE = 0
COINS_COLLECTED = 0

INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_player
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 5

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_enemy
        self.rect = self.image.get_rect()
        self.generate_random_rect()

    def generate_random_rect(self):
        self.rect.left = random.randint(0, WIDTH - self.rect.width)
        self.rect.bottom = 0

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > HEIGHT:
            SCORE += 1
            self.generate_random_rect()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)
        self.rect = self.image.get_rect()
        self.generate_random_rect()

    def generate_random_rect(self):
        self.rect.left = random.randint(0, WIDTH - self.rect.width)
        self.rect.bottom = random.randint(-100, -20)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > HEIGHT:
            self.generate_random_rect()

player = Player()
enemy = Enemy()
coin = Coin()

all_sprites = pygame.sprite.Group()
all_sprites.add(player, enemy, coin)

enemy_sprites = pygame.sprite.Group()
enemy_sprites.add(enemy)

coin_sprites = pygame.sprite.Group()
coin_sprites.add(coin)

clock = pygame.time.Clock()
FPS = 60
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == INC_SPEED:
            SPEED += 0.5

    player.move()
    for entity in all_sprites:
        if entity != player:
            entity.move()

    if pygame.sprite.spritecollideany(player, enemy_sprites):
        pygame.mixer.music.stop()
        sound_crash.play()
        time.sleep(0.5)
        
        screen.fill("red")
        screen.blit(image_game_over, image_game_over_rect)
        pygame.display.update()
        time.sleep(2)
        running = False
    
    coins_collected_list = pygame.sprite.spritecollide(player, coin_sprites, False)
    for collected_coin in coins_collected_list:
        COINS_COLLECTED += 1
        collected_coin.generate_random_rect()

    screen.blit(image_background, (0, 0))
    for entity in all_sprites:
        screen.blit(entity.image, entity.rect)

    score_text = font_small.render(f"Score: {SCORE}", True, "black")
    screen.blit(score_text, (10, 10))

    coins_text = font_small.render(f"Coins: {COINS_COLLECTED}", True, "black")
    screen.blit(coins_text, (WIDTH - coins_text.get_width() - 10, 10))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()