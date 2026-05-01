import pygame
import tools
pygame.init()

WIDTH = 1000
HEIGHT = 800
UI_HEIGHT = 70

screen = pygame.display.set_mode((WIDTH, HEIGHT))
base_layer = pygame.Surface((WIDTH, HEIGHT))

colorRED = (255, 0, 0)
colorGREEN = (0, 255, 0)
colorBLUE = (0, 0, 255)
colorWHITE = (255, 255, 255)
colorBLACK = (0, 0, 0)
colorUI_BG = (50, 50, 50)
colorHIGHLIGHT = (255, 255, 0)
colors = {
    "white": colorWHITE,
    "black": colorBLACK,
    "ui_bg": colorUI_BG,
    "highlight": colorHIGHLIGHT,
}

base_layer.fill(colorBLACK)

current_color = colorRED
current_tool = "pen"
thickness = 5
clock = pygame.time.Clock()

LMBpressed = False
currX = 0
currY = 0
prevX = 0
prevY = 0
startX = 0
startY = 0

text_active = False
text_pos = (0, 0)
text_value = ""

font = pygame.font.SysFont(None, 22)
text_font = pygame.font.SysFont(None, 32)

palette = [
    (pygame.Rect(10, 10, 30, 30), colorRED),
    (pygame.Rect(50, 10, 30, 30), colorGREEN),
    (pygame.Rect(90, 10, 30, 30), colorBLUE),
    (pygame.Rect(130, 10, 30, 30), colorWHITE),
]

tool_labels = {
    "pen": "Pen",
    "line": "Line",
    "rect": "Rect",
    "circle": "Circle",
    "eraser": "Eraser",
    "square": "Square",
    "right_tri": "Right Tri",
    "equil_tri": "Equil Tri",
    "rhombus": "Rhombus",
    "fill": "Fill",
    "text": "Text",
}

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            ctrl_pressed = event.mod & pygame.KMOD_CTRL
            if ctrl_pressed and event.key == pygame.K_s:
                tools.save_canvas(base_layer)
            elif text_active:
                text_active, text_value = tools.handle_text_input(event, base_layer, current_color, text_font, text_pos, text_value)
            else:
                current_tool, thickness = tools.choose_shortcut(event, current_tool, thickness)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_palette = False
            for rect, color in palette:
                if rect.collidepoint(event.pos):
                    current_color = color
                    clicked_palette = True
                    break
            if not clicked_palette and event.pos[1] > UI_HEIGHT:
                if current_tool == "fill":
                    tools.flood_fill(base_layer, event.pos, current_color, WIDTH, HEIGHT, UI_HEIGHT)
                elif current_tool == "text":
                    text_active = True
                    text_pos = event.pos
                    text_value = ""
                else:
                    LMBpressed = True
                    startX = event.pos[0]
                    startY = event.pos[1]
                    currX = event.pos[0]
                    currY = event.pos[1]
                    prevX = event.pos[0]
                    prevY = event.pos[1]
        if event.type == pygame.MOUSEMOTION:
            if LMBpressed:
                currX = event.pos[0]
                currY = event.pos[1]
                if current_tool == "pen":
                    pygame.draw.line(base_layer, current_color, (prevX, prevY), (currX, currY), thickness)
                    pygame.draw.circle(base_layer, current_color, (currX, currY), max(1, thickness // 2))
                elif current_tool == "eraser":
                    pygame.draw.line(base_layer, colorBLACK, (prevX, prevY), (currX, currY), thickness)
                prevX = currX
                prevY = currY
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if LMBpressed:
                LMBpressed = False
                currX = event.pos[0]
                currY = event.pos[1]
                if current_tool not in {"pen", "eraser"}:
                    tools.draw_shape(base_layer, current_tool, current_color, startX, startY, currX, currY, thickness)
    screen.blit(base_layer, (0, 0))
    if LMBpressed and current_tool not in {"pen", "eraser"}:
        tools.draw_shape(screen, current_tool, current_color, startX, startY, currX, currY, thickness)
    if text_active:
        preview = text_font.render(text_value, True, current_color)
        screen.blit(preview, text_pos)
        cursor_x = text_pos[0] + preview.get_width() + 2
        pygame.draw.line(screen, current_color, (cursor_x, text_pos[1]), (cursor_x, text_pos[1] + text_font.get_height()), 2)
    tools.draw_toolbar(screen, palette, current_color, current_tool, thickness, font, tool_labels, colors)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()