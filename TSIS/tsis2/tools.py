from datetime import datetime
import pygame

def calc_rect(x1, y1, x2, y2):
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))

def save_canvas(base_layer):
    filename = f"paint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(base_layer, filename)
    print(f"Saved {filename}")

def draw_shape(surface, tool, color, x1, y1, x2, y2, line_width):
    rect = calc_rect(x1, y1, x2, y2)
    if tool == "line":
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), line_width)
    elif tool == "rect":
        pygame.draw.rect(surface, color, rect, line_width)
    elif tool == "circle":
        pygame.draw.ellipse(surface, color, rect, line_width)
    elif tool == "square":
        side = min(rect.width, rect.height)
        square_rect = pygame.Rect(rect.x, rect.y, side, side)
        pygame.draw.rect(surface, color, square_rect, line_width)
    elif tool == "right_tri":
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, line_width)
    elif tool == "equil_tri":
        top = ((x1 + x2) // 2, y1)
        left = (x1, y2)
        right = (x2, y2)
        pygame.draw.polygon(surface, color, [top, left, right], line_width)
    elif tool == "rhombus":
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        points = [
            (center_x, y1),
            (x2, center_y),
            (center_x, y2),
            (x1, center_y),
        ]
        pygame.draw.polygon(surface, color, points, line_width)

def flood_fill(surface, start_pos, fill_color, width, height, ui_height):
    x, y = start_pos
    if y < ui_height or not (0 <= x < width and 0 <= y < height):
        return
    target_color = surface.get_at((x, y))
    replacement_color = pygame.Color(*fill_color)
    if target_color == replacement_color:
        return
    stack = [(x, y)]
    while stack:
        px, py = stack.pop()
        if not (0 <= px < width and ui_height <= py < height):
            continue
        if surface.get_at((px, py)) != target_color:
            continue
        surface.set_at((px, py), replacement_color)
        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))

def choose_shortcut(event, current_tool, thickness):
    if event.key == pygame.K_1:
        thickness = 5
    elif event.key == pygame.K_2:
        thickness = 10
    elif event.key == pygame.K_3:
        thickness = 15
    elif event.key == pygame.K_p:
        current_tool = "pen"
    elif event.key == pygame.K_l:
        current_tool = "line"
    elif event.key == pygame.K_r:
        current_tool = "rect"
    elif event.key == pygame.K_c:
        current_tool = "circle"
    elif event.key == pygame.K_e:
        current_tool = "eraser"
    elif event.key == pygame.K_s:
        current_tool = "square"
    elif event.key == pygame.K_q:
        current_tool = "right_tri"
    elif event.key == pygame.K_w:
        current_tool = "equil_tri"
    elif event.key == pygame.K_d:
        current_tool = "rhombus"
    elif event.key == pygame.K_f:
        current_tool = "fill"
    elif event.key == pygame.K_t:
        current_tool = "text"
    return current_tool, thickness

def handle_text_input(event, base_layer, current_color, text_font, text_pos, text_value):
    text_active = True
    if event.key == pygame.K_RETURN:
        if text_value:
            rendered = text_font.render(text_value, True, current_color)
            base_layer.blit(rendered, text_pos)
        text_active = False
        text_value = ""
    elif event.key == pygame.K_ESCAPE:
        text_active = False
        text_value = ""
    elif event.key == pygame.K_BACKSPACE:
        text_value = text_value[:-1]
    elif event.unicode and event.unicode.isprintable():
        text_value += event.unicode
    return text_active, text_value

def draw_toolbar(screen, palette, current_color, current_tool, thickness, font, tool_labels, colors):
    color_ui_bg = colors["ui_bg"]
    color_highlight = colors["highlight"]
    color_black = colors["black"]
    color_white = colors["white"]
    pygame.draw.rect(screen, color_ui_bg, (0, 0, screen.get_width(), 70))
    for rect, color in palette:
        pygame.draw.rect(screen, color, rect)
        border = color_highlight if color == current_color else color_black
        width = 3 if color == current_color else 1
        pygame.draw.rect(screen, border, rect, width)
    line1 = ("Tools: P Pencil | L Line | R Rect | C Circle | E Eraser | S Square | Q RightTri | W EquilTri | D Rhombus | F Fill | T Text")
    line2 = (f"Size: 1 small, 2 medium, 3 large | Current: {tool_labels[current_tool]}, {thickness}px | Ctrl+S Save")
    screen.blit(font.render(line1, True, color_white), (180, 10))
    screen.blit(font.render(line2, True, color_white), (180, 38))