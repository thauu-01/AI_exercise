import pygame
import sys
from collections import deque

# Khởi tạo Pygame
pygame.init()

# Các hằng số và cấu hình
CELL_SIZE = 50
BOARD_SIZE = 6 
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sudoku 6x6 - Generate and Test")

# Màu sắc
BACKGROUND_COLOR = (200, 220, 255)
WHITE = (255, 255, 255)
BLACK = (172, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 69, 0)
FONT = pygame.font.SysFont(None, 30)
FONT_SMALL = pygame.font.SysFont(None, 20)

# Định nghĩa các đơn vị (hàng, cột, vùng 2x3)
ROWS = [[f'{chr(65+i)}{j+1}' for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]
COLS = [[f'{chr(65+i)}{j+1}' for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)]
BOXES = [
    ['A1', 'A2', 'A3', 'B1', 'B2', 'B3'],
    ['A4', 'A5', 'A6', 'B4', 'B5', 'B6'],
    ['C1', 'C2', 'C3', 'D1', 'D2', 'D3'],
    ['C4', 'C5', 'C6', 'D4', 'D5', 'D6'],
    ['E1', 'E2', 'E3', 'F1', 'F2', 'F3'],
    ['E4', 'E5', 'E6', 'F4', 'F5', 'F6']
]
UNITS = ROWS + COLS + BOXES

def generate_and_test(csp):
    steps = []
    variables = list(csp['domains'].keys())
    assignment = csp['assignment'].copy()

    def generate(index):
        if index == len(variables):
           
            for unit in UNITS:
                unit_values = [assignment.get(var) for var in unit if assignment.get(var) is not None]
                if len(unit_values) != len(set(unit_values)):
                    return False
            return True

        var = variables[index]
        if assignment.get(var) is not None: 
            return generate(index + 1)

        
        for value in csp['domains'][var]:
            
            consistent = True
            for unit in UNITS:
                if var in unit:
                    for other in unit:
                        if other != var and assignment.get(other) == value:
                            consistent = False
                            break
                if not consistent:
                    break

            if consistent:
                assignment[var] = value
                steps.append((var, value))
                if generate(index + 1):
                    return True
                assignment[var] = None
                steps.append((var, None))  

        return False


    result = generate(0)
    csp['assignment'] = assignment
    return result, steps

# Lớp Button
class Button:
    def __init__(self, text, x, y, width, height, callback, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, self.rect, border_radius=10)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, (255, 255, 0), self.rect, 3, border_radius=10)
        
        text = FONT.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        WINDOW.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# Lớp SudokuGUI
class SudokuGUI:
    def __init__(self):
        self.grid = {f'{chr(i)}{j+1}': '?' for i in range(65, 65+BOARD_SIZE) for j in range(BOARD_SIZE)}
        self.selected_cell = None
        self.domains = None
        self.steps = []
        self.step_index = 0
        self.last_step_time = pygame.time.get_ticks()
        self.step_interval = 1000
        self.is_solving = False
        self.show_solving_message = False
        self.result = None
        self.current_algorithm = "Generate and Test"

        self.buttons = [
            Button("Reset", 400, 650, 120, 50, self.reset, (192, 192, 192)),
            Button("Generate & Test", 650, 650, 140, 50, self.solve_generate_and_test, (255, 165, 0)),
        ]

    def init_csp(self):
        csp = {'domains': {}, 'neighbors': {var: set() for var in self.grid}, 'assignment': {var: None for var in self.grid}}
        for var in self.grid:
            if self.grid[var] == '?':
                csp['domains'][var] = list(range(1, BOARD_SIZE + 1))
            else:
                csp['domains'][var] = [int(self.grid[var])]
                csp['assignment'][var] = int(self.grid[var])
            for unit in UNITS:
                if var in unit:
                    for other in unit:
                        if other != var:
                            csp['neighbors'][var].add(other)
        return csp

    def draw_board(self, x_offset, y_offset, title):
        title_text = FONT.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(x_offset + CELL_SIZE * BOARD_SIZE // 2, y_offset - 40))
        WINDOW.blit(title_text, title_rect)

        board_rect = pygame.Rect(x_offset - 10, y_offset - 10, CELL_SIZE * BOARD_SIZE + 20, CELL_SIZE * BOARD_SIZE + 20)
        pygame.draw.rect(WINDOW, (230, 240, 255), board_rect, border_radius=10)
        pygame.draw.rect(WINDOW, (100, 150, 200), board_rect, 3, border_radius=10)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                var = chr(65 + i) + str(j + 1)
                val = self.grid[var]
                rect = pygame.Rect(x_offset + j * CELL_SIZE, y_offset + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell_color = WHITE
                if self.selected_cell == (i, j):
                    cell_color = (144, 238, 144)
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, (50, 50, 50), rect, 1, border_radius=5)
                
                text = FONT.render(str(val) if val != '?' else '?', True, RED)
                text_rect = text.get_rect(center=rect.center)
                WINDOW.blit(text, text_rect)

        for box in BOXES:
            top_left = box[0]
            row, col = ord(top_left[0]) - 65, int(top_left[1]) - 1
            box_width = 3 * CELL_SIZE if len(set(x[1] for x in box)) == 3 else 2 * CELL_SIZE
            box_height = 2 * CELL_SIZE
            pygame.draw.rect(WINDOW, (100, 150, 200), 
                            (x_offset + col * CELL_SIZE, y_offset + row * CELL_SIZE, box_width, box_height), 2)

        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(WINDOW, (150, 180, 210), 
                            (x_offset, y_offset + i * CELL_SIZE), 
                            (x_offset + CELL_SIZE * BOARD_SIZE, y_offset + i * CELL_SIZE), 2)
            pygame.draw.line(WINDOW, (150, 180, 210), 
                            (x_offset + i * CELL_SIZE, y_offset), 
                            (x_offset + i * CELL_SIZE, y_offset + CELL_SIZE * BOARD_SIZE), 2)

    def draw(self):
        WINDOW.fill(BACKGROUND_COLOR)
        self.draw_board(50, 100, "Sudoku 6x6")
    
        for button in self.buttons:
            button.draw()

        if self.show_solving_message:
            solving_text = f"Running {self.current_algorithm}..."
            text = FONT.render(solving_text, True, BLUE)
            WINDOW.blit(text, (50, 600))

        if self.result is not None:
            result_text = "Solution found!" if self.result else "No solution!"
            text = FONT.render(result_text, True, BLUE)
            WINDOW.blit(text, (50, 550))

        if self.steps and self.step_index < len(self.steps):
            var, value = self.steps[self.step_index]
            step_text = f"Step {self.step_index + 1}: Assign {var} = {value if value is not None else 'None'}"
            text = FONT_SMALL.render(step_text, True, BLACK)
            WINDOW.blit(text, (400, 600))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x < 50 + CELL_SIZE * BOARD_SIZE and 100 <= y < 100 + CELL_SIZE * BOARD_SIZE:
                i = (y - 100) // CELL_SIZE
                j = (x - 50) // CELL_SIZE
                self.selected_cell = (i, j)

        elif event.type == pygame.KEYDOWN and self.selected_cell:
            i, j = self.selected_cell
            var = chr(65 + i) + str(j + 1)
            if pygame.K_1 <= event.key <= pygame.K_6:
                num = event.key - pygame.K_0
                self.grid[var] = num
            elif event.key == pygame.K_BACKSPACE:
                self.grid[var] = '?'
            elif event.key == pygame.K_LEFT:
                self.selected_cell = (i, max(0, j - 1))
            elif event.key == pygame.K_RIGHT:
                self.selected_cell = (i, min(BOARD_SIZE - 1, j + 1))
            elif event.key == pygame.K_UP:
                self.selected_cell = (max(0, i - 1), j)
            elif event.key == pygame.K_DOWN:
                self.selected_cell = (min(BOARD_SIZE - 1, i + 1), j)

    def solve_generate_and_test(self):
        self.show_solving_message = True
        self.is_solving = True
        self.step_index = 0
        self.steps = []
        self.result = None

        self.draw()
        pygame.display.flip()
        pygame.event.pump()

        csp = self.init_csp()
        self.result, gen_steps = generate_and_test(csp)
        self.steps.extend(gen_steps)

        if self.result:
            for var in csp['assignment']:
                if csp['assignment'][var] is not None:
                    self.grid[var] = csp['assignment'][var]
        else:
            self.result = False

        self.show_solving_message = False

    def reset(self):
        self.grid = {var: '?' for var in self.grid}
        self.steps = []
        self.step_index = 0
        self.is_solving = False
        self.show_solving_message = False
        self.result = None
        self.selected_cell = None

    def update(self):
        if self.steps and self.step_index < len(self.steps) - 1 and self.is_solving:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_time >= self.step_interval:
                self.step_index += 1
                self.last_step_time = current_time

def main():
    gui = SudokuGUI()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            gui.handle_input(event)
            for button in gui.buttons:
                button.handle_event(event)

        gui.update()
        gui.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()