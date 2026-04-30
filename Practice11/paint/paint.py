import pygame

pygame.init()

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
base_layer = pygame.Surface((WIDTH, HEIGHT))

colorRED = (255, 0, 0)
colorGREEN = (0, 255, 0)
colorBLUE = (0, 0, 255)
colorWHITE = (255, 255, 255)
colorBLACK = (0, 0, 0)
colorUI_BG = (50, 50, 50)
colorHIGHLIGHT = (255, 255, 0)

base_layer.fill(colorBLACK)

current_color = colorRED
current_tool = 'pen'
clock = pygame.time.Clock()

LMBpressed = False
THICKNESS = 5
currX = 0
currY = 0
prevX = 0
prevY = 0
startX = 0
startY = 0
UI_HEIGHT = 50

def calc_rect(x1, y1, x2, y2):
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))

palette = [
    (pygame.Rect(10, 10, 30, 30), colorRED),
    (pygame.Rect(50, 10, 30, 30), colorGREEN),
    (pygame.Rect(90, 10, 30, 30), colorBLUE),
    (pygame.Rect(130, 10, 30, 30), colorWHITE)
]

font = pygame.font.SysFont(None, 22)
ui_text = font.render("R:Rect C:Circle S:Square Q:Right Triangle W:Equilateral Triangle D:Rhombus P:Pen E:Eraser", True, colorWHITE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                current_tool = 'rect'
            if event.key == pygame.K_c:
                current_tool = 'circle'
            if event.key == pygame.K_e:
                current_tool = 'eraser'
            if event.key == pygame.K_p:
                current_tool = 'pen'
            if event.key == pygame.K_s:
                current_tool = 'square'
            if event.key == pygame.K_q:
                current_tool = 'right_triangle'
            if event.key == pygame.K_w:
                current_tool = 'equil_triangle'
            if event.key == pygame.K_d:
                current_tool = 'rhombus'
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_palette = False
            for rect, color in palette:
                if rect.collidepoint(event.pos):
                    current_color = color
                    clicked_palette = True
                    break
            if not clicked_palette and event.pos[1] > UI_HEIGHT:
                LMBpressed = True
                startX = event.pos[0]
                startY = event.pos[1]
                prevX = event.pos[0]
                prevY = event.pos[1]
        if event.type == pygame.MOUSEMOTION:
            if LMBpressed:
                currX = event.pos[0]
                currY = event.pos[1]
                if current_tool == 'pen':
                    pygame.draw.line(base_layer, current_color, (prevX, prevY), (currX, currY), THICKNESS)
                    pygame.draw.circle(base_layer, current_color, (currX, currY), THICKNESS // 2)
                elif current_tool == 'eraser':
                    pygame.draw.line(base_layer, colorBLACK, (prevX, prevY), (currX, currY), THICKNESS * 2)
                prevX = currX
                prevY = currY
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if LMBpressed:
                LMBpressed = False
                currX = event.pos[0]
                currY = event.pos[1]
                rect = calc_rect(startX, startY, currX, currY)
                if current_tool == 'rect':
                    pygame.draw.rect(base_layer, current_color, rect, THICKNESS)
                elif current_tool == 'circle':
                    pygame.draw.ellipse(base_layer, current_color, rect, THICKNESS)
                elif current_tool == 'square':
                    side = min(rect.width, rect.height)
                    square_rect = pygame.Rect(rect.x, rect.y, side, side)
                    pygame.draw.rect(base_layer, current_color, square_rect, THICKNESS)
                elif current_tool == 'right_triangle':
                    points = [
                        (startX, startY),
                        (startX, currY),
                        (currX, currY)
                    ]
                    pygame.draw.polygon(base_layer, current_color, points, THICKNESS)
                elif current_tool == 'equil_triangle':
                    top = ((startX + currX) // 2, startY)
                    left = (startX, currY)
                    right = (currX, currY)
                    points = [top, left, right]
                    pygame.draw.polygon(base_layer, current_color, points, THICKNESS)
                elif current_tool == 'rhombus':
                    centerX = (startX + currX) // 2
                    centerY = (startY + currY) // 2
                    points = [
                        (centerX, startY),
                        (currX, centerY),
                        (centerX, currY),
                        (startX, centerY)
                    ]
                    pygame.draw.polygon(base_layer, current_color, points, THICKNESS)
    screen.blit(base_layer, (0, 0))
    if LMBpressed:
        rect = calc_rect(startX, startY, currX, currY)
        if current_tool == 'rect':
            pygame.draw.rect(screen, current_color, rect, THICKNESS)
        elif current_tool == 'circle':
            pygame.draw.ellipse(screen, current_color, rect, THICKNESS)
        elif current_tool == 'square':
            side = min(rect.width, rect.height)
            square_rect = pygame.Rect(rect.x, rect.y, side, side)
            pygame.draw.rect(screen, current_color, square_rect, THICKNESS)
        elif current_tool == 'right_triangle':
            points = [
                (startX, startY),
                (startX, currY),
                (currX, currY)
            ]
            pygame.draw.polygon(screen, current_color, points, THICKNESS)
        elif current_tool == 'equil_triangle':
            top = ((startX + currX) // 2, startY)
            left = (startX, currY)
            right = (currX, currY)
            points = [top, left, right]
            pygame.draw.polygon(screen, current_color, points, THICKNESS)
        elif current_tool == 'rhombus':
            centerX = (startX + currX) // 2
            centerY = (startY + currY) // 2
            points = [
                (centerX, startY),
                (currX, centerY),
                (centerX, currY),
                (startX, centerY)
            ]
            pygame.draw.polygon(screen, current_color, points, THICKNESS)
    pygame.draw.rect(screen, colorUI_BG, (0, 0, WIDTH, UI_HEIGHT))
    for rect, color in palette:
        pygame.draw.rect(screen, color, rect)
        if color == current_color:
            pygame.draw.rect(screen, colorHIGHLIGHT, rect, 3)
        else:
            pygame.draw.rect(screen, colorBLACK, rect, 1)
    screen.blit(ui_text, (180, 16))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()