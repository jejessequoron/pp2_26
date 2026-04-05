import pygame
import sys
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 220)
GRAY = (200, 200, 200)
GREEN = (50, 180, 90)
RED = (220, 60, 60)

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

MUSIC_FOLDER = "music"

def load_playlist(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    supported_extensions = (".wav")
    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(supported_extensions)
    ]
    files.sort()
    return files

playlist = load_playlist(MUSIC_FOLDER)
current_index = 0
is_playing = False
track_start_ticks = 0
paused_position_ms = 0

def get_track_name(path):
    return os.path.basename(path)

def load_and_play(index):
    global is_playing, track_start_ticks, paused_position_ms

    if not playlist:
        return

    pygame.mixer.music.load(playlist[index])
    pygame.mixer.music.play()
    is_playing = True
    paused_position_ms = 0
    track_start_ticks = pygame.time.get_ticks()

def stop_music():
    global is_playing, paused_position_ms
    pygame.mixer.music.stop()
    is_playing = False
    paused_position_ms = 0

def next_track():
    global current_index
    if not playlist:
        return
    current_index = (current_index + 1) % len(playlist)
    load_and_play(current_index)

def previous_track():
    global current_index
    if not playlist:
        return
    current_index = (current_index - 1) % len(playlist)
    load_and_play(current_index)

def format_time(ms):
    seconds = max(0, ms // 1000)
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02}:{secs:02}"

def draw_text(text, font_obj, color, x, y):
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))

def get_track_length_ms(path):
    try:
        sound = pygame.mixer.Sound(path)
        return int(sound.get_length() * 1000)
    except:
        return 0

def main():
    global is_playing

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if playlist:
                        load_and_play(current_index)

                elif event.key == pygame.K_s:
                    stop_music()

                elif event.key == pygame.K_n:
                    next_track()

                elif event.key == pygame.K_b:
                    previous_track()

                elif event.key == pygame.K_q:
                    running = False

        if playlist and is_playing and not pygame.mixer.music.get_busy():
            next_track()

        screen.fill(WHITE)

        title = font.render("Music Player", True, BLACK)
        screen.blit(title, (20, 20))

        controls = "P = Play   S = Stop   N = Next   B = Previous   Q = Quit"
        draw_text(controls, small_font, BLUE, 20, 70)

        if not playlist:
            draw_text(f"No audio files found in '{MUSIC_FOLDER}' folder.", font, RED, 20, 140)
            draw_text("Add .mp3, .wav, or .ogg files and restart.", small_font, BLACK, 20, 180)
        else:
            current_track = get_track_name(playlist[current_index])
            draw_text(f"Track: {current_track}", font, BLACK, 20, 140)

            status = "Playing" if is_playing and pygame.mixer.music.get_busy() else "Stopped"
            status_color = GREEN if status == "Playing" else RED
            draw_text(f"Status: {status}", font, status_color, 20, 190)

            total_ms = get_track_length_ms(playlist[current_index])

            if is_playing:
                current_ms = pygame.mixer.music.get_pos()
                if current_ms < 0:
                    current_ms = 0
            else:
                current_ms = 0

            draw_text(f"Position: {format_time(current_ms)} / {format_time(total_ms)}", font, BLACK, 20, 240)

            bar_x, bar_y, bar_w, bar_h = 20, 300, 700, 25
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_w, bar_h))

            if total_ms > 0:
                progress_w = int((current_ms / total_ms) * bar_w)
                progress_w = max(0, min(progress_w, bar_w))
                pygame.draw.rect(screen, BLUE, (bar_x, bar_y, progress_w, bar_h))

            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_w, bar_h), 2)

            draw_text("Playlist:", small_font, BLACK, 500, 70)
            for i, track in enumerate(playlist[:8]):
                prefix = "-> " if i == current_index else "   "
                color = BLUE if i == current_index else BLACK
                draw_text(prefix + get_track_name(track), small_font, color, 500, 100 + i * 28)

        pygame.display.flip()
        clock.tick(30)

    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()