import pygame
import sys
import random

# Khởi tạo Pygame
pygame.init()

# Các hằng số và cấu hình
CELL_SIZE = 50
BOARD_SIZE = 6
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Min-Conflicts on Sudoku 6x6 with Two Boards")

# Màu sắc
BACKGROUND_COLOR = (200, 220, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (180, 200, 220)
BLUE = (0, 0, 255)


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
        
        text = pygame.font.SysFont(None, 30).render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        WINDOW.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# Lớp SudokuGUI
class SudokuGUI:
    def __init__(self):
        self.input_grid = {f'{chr(i)}{j+1}': '?' for i in range(65, 65+BOARD_SIZE) for j in range(BOARD_SIZE)}
        self.solving_grid = {f'{chr(i)}{j+1}': '?' for i in range(65, 65+BOARD_SIZE) for j in range(BOARD_SIZE)}
        self.selected_cell = None
        self.is_solving = False
        self.steps = 0
        self.max_steps = 1000
        self.result = None
        self.step_list = []  
        self.step_display_offset = 0  

        self.buttons = [
            Button("Reset", 400, 650, 120, 50, self.reset, GRAY),
            Button("Run", 550, 650, 120, 50, self.solve, GREEN),
        ]

    def count_conflicts(self, var, value, grid):
        conflicts = 0
        for unit in UNITS:
            if var in unit:
                for other in unit:
                    if other != var and grid.get(other) == str(value):
                        conflicts += 1
        return conflicts

    def min_conflicts_step(self):
        conflicted_vars = [var for var in self.solving_grid if self.solving_grid[var] != '?' and self.count_conflicts(var, int(self.solving_grid[var]), self.solving_grid) > 0]
        if not conflicted_vars:
            return True
        var = random.choice(conflicted_vars)
        old_value = self.solving_grid[var]
        min_conflicts = float('inf')
        best_value = old_value
        for value in range(1, BOARD_SIZE + 1):
            if str(value) != self.solving_grid[var]:
                conflicts = self.count_conflicts(var, value, self.solving_grid)
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_value = str(value)
        if best_value != old_value:
            self.step_list.append(f"Step {self.steps + 1}: Change {var} from {old_value} to {best_value}")
            self.solving_grid[var] = best_value
        self.steps += 1
        return False if self.steps >= self.max_steps else None

    def draw_board(self, grid, x_offset, y_offset, title):
        title_text = pygame.font.SysFont(None, 30).render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(x_offset + CELL_SIZE * BOARD_SIZE // 2, y_offset - 40))
        WINDOW.blit(title_text, title_rect)

        board_rect = pygame.Rect(x_offset - 10, y_offset - 10, CELL_SIZE * BOARD_SIZE + 20, CELL_SIZE * BOARD_SIZE + 20)
        pygame.draw.rect(WINDOW, (230, 240, 255), board_rect, border_radius=10)
        pygame.draw.rect(WINDOW, BLUE, board_rect, 3, border_radius=10)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                var = chr(65 + i) + str(j + 1)
                val = grid[var]
                rect = pygame.Rect(x_offset + j * CELL_SIZE, y_offset + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell_color = WHITE
                if self.selected_cell == (i, j) and x_offset == 50:  
                    cell_color = (144, 238, 144)
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, BLACK, rect, 1, border_radius=5)
                
                text = pygame.font.SysFont(None, 30).render(str(val) if val != '?' else '?', True, RED)
                text_rect = text.get_rect(center=rect.center)
                WINDOW.blit(text, text_rect)

        for box in BOXES:
            top_left = box[0]
            row, col = ord(top_left[0]) - 65, int(top_left[1]) - 1
            box_width = 3 * CELL_SIZE if len(set(x[1] for x in box)) == 3 else 2 * CELL_SIZE
            box_height = 2 * CELL_SIZE
            pygame.draw.rect(WINDOW, BLUE, (x_offset + col * CELL_SIZE, y_offset + row * CELL_SIZE, box_width, box_height), 2)

        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(WINDOW, (150, 180, 210), (x_offset, y_offset + i * CELL_SIZE), (x_offset + CELL_SIZE * BOARD_SIZE, y_offset + i * CELL_SIZE), 2)
            pygame.draw.line(WINDOW, (150, 180, 210), (x_offset + i * CELL_SIZE, y_offset), (x_offset + i * CELL_SIZE, y_offset + CELL_SIZE * BOARD_SIZE), 2)

    def draw_steps(self, x_offset, y_offset):
        title_text = pygame.font.SysFont(None, 30).render("Solving Steps", True, BLACK)
        WINDOW.blit(title_text, (x_offset, y_offset - 40))

        max_display_steps = 10  
        start_idx = max(0, len(self.step_list) - max_display_steps - self.step_display_offset)
        end_idx = min(len(self.step_list), start_idx + max_display_steps)

        for i, step in enumerate(self.step_list[start_idx:end_idx]):
            text = pygame.font.SysFont(None, 25).render(step, True, BLACK)
            WINDOW.blit(text, (x_offset, y_offset + i * 30))

    def draw(self):
        WINDOW.fill(BACKGROUND_COLOR)
        self.draw_board(self.input_grid, 50, 100, "Input Sudoku 6x6")
        self.draw_board(self.solving_grid, 450, 100, "Solving Sudoku 6x6")  
        self.draw_steps(800, 100) 
        
        for button in self.buttons:
            button.draw()

        if self.is_solving:
            solving_text = "Running Min-Conflicts..."
            text = pygame.font.SysFont(None, 30).render(solving_text, True, BLUE)
            WINDOW.blit(text, (50, 600))

        if self.result is not None:
            result_text = "Solution found!" if self.result else "No solution!"
            text = pygame.font.SysFont(None, 30).render(result_text, True, BLUE)
            WINDOW.blit(text, (50, 550))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x < 50 + CELL_SIZE * BOARD_SIZE and 100 <= y < 100 + CELL_SIZE * BOARD_SIZE:
                i = (y - 100) // CELL_SIZE
                j = (x - 50) // CELL_SIZE
                self.selected_cell = (i, j)
            else:
                self.selected_cell = None

        elif event.type == pygame.KEYDOWN and self.selected_cell:
            i, j = self.selected_cell
            var = chr(65 + i) + str(j + 1)
            if pygame.K_1 <= event.key <= pygame.K_6:
                num = event.key - pygame.K_0
                self.input_grid[var] = num
            elif event.key == pygame.K_BACKSPACE:
                self.input_grid[var] = '?'
            elif event.key == pygame.K_LEFT:
                self.selected_cell = (i, max(0, j - 1))
            elif event.key == pygame.K_RIGHT:
                self.selected_cell = (i, min(BOARD_SIZE - 1, j + 1))
            elif event.key == pygame.K_UP:
                self.selected_cell = (max(0, i - 1), j)
            elif event.key == pygame.K_DOWN:
                self.selected_cell = (min(BOARD_SIZE - 1, i + 1), j)

    def solve(self):
        self.is_solving = True
        self.steps = 0
        self.result = None
        self.step_list = []
        self.step_display_offset = 0
        self.solving_grid = self.input_grid.copy()


        for var in self.solving_grid:
            if self.solving_grid[var] == '?':
                self.solving_grid[var] = str(random.randint(1, BOARD_SIZE))

        while self.is_solving and self.steps < self.max_steps:
            self.draw()
            pygame.display.flip()
            pygame.event.pump()
            if self.min_conflicts_step() is True:
                self.result = True
                self.is_solving = False
            elif self.min_conflicts_step() is False:
                self.result = False
                self.is_solving = False
            pygame.time.wait(100)

        self.is_solving = False

    def reset(self):
        self.input_grid = {var: '?' for var in self.input_grid}
        self.solving_grid = {var: '?' for var in self.solving_grid}
        self.selected_cell = None
        self.is_solving = False
        self.steps = 0
        self.result = None
        self.step_list = []
        self.step_display_offset = 0

    def update(self):
        pass

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

        gui.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
