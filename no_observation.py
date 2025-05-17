import itertools
import pygame
import sys
import time
import random
import copy

# Tăng giới hạn độ sâu đệ quy
sys.setrecursionlimit(2000)

# Khởi tạo Pygame
pygame.init()

# Các hằng số và cấu hình
CELL_SIZE = 60
BOARD_SIZE = 3
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("8-Puzzle Solver with No Observation")

# Màu sắc
BACKGROUND_COLOR = (200, 220, 255)
WHITE = (255, 255, 255)
BLACK = (172, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BUTTON_COLORS = [
    (255, 182, 193), (173, 216, 230), (144, 238, 144), (240, 230, 140),
    (221, 160, 221), (255, 218, 185), (255, 192, 203), (175, 238, 238)
]
FONT = pygame.font.SysFont(None, 40)
FONT_SMALL = pygame.font.SysFont(None, 30)

# Trạng thái mục tiêu
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIRECTION_NAMES = ["Up", "Down", "Left", "Right"]

def find_blank(state):
    state = list(state)
    for i in range(len(state)):
        if state[i] == 0:
            return i // BOARD_SIZE, i % BOARD_SIZE
    return None

def is_valid(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def move(state, direction):
    new_state = list(state)
    blank_i, blank_j = find_blank(new_state)
    di, dj = direction
    new_i, new_j = blank_i + di, blank_j + dj
    if 0 <= new_i < 3 and 0 <= new_j < 3:
        new_state[blank_i * BOARD_SIZE + blank_j], new_state[new_i * BOARD_SIZE + new_j] = \
            new_state[new_i * BOARD_SIZE + new_j], new_state[blank_i * BOARD_SIZE + blank_j]
        return tuple(new_state)
    return None

def actions_in_belief_state(belief_state):
    """Lấy tập hợp các hành động hợp lệ trong belief state (giao của tất cả hành động)."""
    possible_actions = set(range(len(MOVES))) 
    for state in belief_state:
        blank_i, blank_j = find_blank(state)
        state_actions = set()
        for action_idx, (dx, dy) in enumerate(MOVES):
            new_x, new_y = blank_i + dx, blank_j + dy
            if is_valid(new_x, new_y):
                state_actions.add(action_idx)
        possible_actions &= state_actions
    return list(possible_actions)

def predict(belief_state, action_idx):
    """Dự đoán belief state mới sau hành động (No Observation)."""
    new_belief_state = set()
    direction = MOVES[action_idx]
    for state in belief_state:
        new_state = move(state, direction)
        if new_state:
            new_belief_state.add(new_state)
    return new_belief_state

def is_goal_belief_state(belief_state):

    return all(state == GOAL_STATE for state in belief_state)

def no_observation_search(initial_belief_state):

    visited = set()  
    plan = [] 
    step = 0  

    def search(belief_state, path):
        nonlocal step

        belief_key = tuple(sorted(belief_state))
        if belief_key in visited:
            return None, step
        visited.add(belief_key)
        step += 1


        if is_goal_belief_state(belief_state):
            return path, step


        possible_actions = actions_in_belief_state(belief_state)
        for action_idx in possible_actions:

            new_belief = predict(belief_state, action_idx)
            if not new_belief:
                continue
    
            sub_plan, sub_step = search(new_belief, path + [f"Do {DIRECTION_NAMES[action_idx]}"])
            step = sub_step
            if sub_plan is not None:
                return sub_plan, step

        return None, step

    return search(initial_belief_state, [])

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

# Lớp PuzzleGUI
class PuzzleGUI:
    def __init__(self):
        self.input_state = [0] * 9  
        self.input_state[0], self.input_state[3], self.input_state[8] = 1, 4, 0
        self.belief_state = None
        self.selected_cell = None
        self.plan = None
        self.step = 0
        self.expanded_states = 0
        self.execution_time = 0
        self.last_step_time = pygame.time.get_ticks()
        self.step_interval = 1000
        self.is_solving = False
        self.current_algorithm = None
        self.show_solving_message = False
        self.current_belief_index = 0
        self.max_display_states = 8

        self.buttons = [
            Button("Reset", 550, 700, 120, 50, self.reset, (192, 192, 192)),
            Button("Random", 700, 700, 120, 50, self.randomize, (255, 165, 0)),
            Button("Run", 850, 700, 140, 50, lambda: self.solve(no_observation_search, "No Observation Search"), (0, 255, 0)),
        ]

    def draw_board(self, state, x_offset, y_offset, title, is_input=False):
        title_text = FONT.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(x_offset + CELL_SIZE * BOARD_SIZE // 2, y_offset - 40))
        WINDOW.blit(title_text, title_rect)

        board_rect = pygame.Rect(x_offset - 10, y_offset - 10, CELL_SIZE * BOARD_SIZE + 20, CELL_SIZE * BOARD_SIZE + 20)
        pygame.draw.rect(WINDOW, (230, 240, 255), board_rect, border_radius=10)
        pygame.draw.rect(WINDOW, (100, 150, 200), board_rect, 3, border_radius=10)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                val = state[i * BOARD_SIZE + j]
                rect = pygame.Rect(x_offset + j * CELL_SIZE, y_offset + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if val == 0:
                    cell_color = (180, 200, 220)
                else:
                    cell_color = WHITE
                
                if is_input and self.selected_cell == (i, j):
                    cell_color = (144, 238, 144)
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, (50, 50, 50), rect, 1, border_radius=5)
                
                if val != 0:
                    text = FONT.render(str(val), True, (255, 69, 0))
                    text_rect = text.get_rect(center=rect.center)
                    WINDOW.blit(text, text_rect)
        
        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(WINDOW, (150, 180, 210), 
                            (x_offset, y_offset + i * CELL_SIZE), 
                            (x_offset + CELL_SIZE * BOARD_SIZE, y_offset + i * CELL_SIZE), 2)
            pygame.draw.line(WINDOW, (150, 180, 210), 
                            (x_offset + i * CELL_SIZE, y_offset), 
                            (x_offset + i * CELL_SIZE, y_offset + CELL_SIZE * BOARD_SIZE), 2)

    def draw_belief_state(self, belief_state, x_offset, y_offset):
        if not belief_state:
            return

        title_text = FONT.render(f"Belief State ({len(belief_state)} states)", True, BLACK)
        WINDOW.blit(title_text, (x_offset, y_offset - 50))

        spacing = 40
        board_width = CELL_SIZE * BOARD_SIZE + 20
        board_height = CELL_SIZE * BOARD_SIZE + 20

        total_states = len(belief_state)
        start_idx = self.current_belief_index * self.max_display_states
        end_idx = min(start_idx + self.max_display_states, total_states)
        current_states = list(belief_state)[start_idx:end_idx]

        for idx, state in enumerate(current_states):
            row = idx // 4
            col = idx % 4
            x_pos = x_offset + col * (board_width + spacing)
            y_pos = y_offset + row * (board_height + spacing)
            self.draw_board(state, x_pos, y_pos, "")

    def draw(self):
        WINDOW.fill(BACKGROUND_COLOR)
        self.draw_board(self.input_state, 50, 100, "Trang thai dau", True)
        if self.belief_state:
            self.draw_belief_state(self.belief_state, 300, 100)
    
        for button in self.buttons:
            button.draw()

        if self.show_solving_message and self.current_algorithm:
            solving_text = f"Running {self.current_algorithm}..."
            text = FONT.render(solving_text, True, BLUE)
            WINDOW.blit(text, (50, 650))
    
        if self.plan:
            panel_x, panel_y = 40, 390
            panel_width = 600
            panel_height = 140
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
            pygame.draw.rect(WINDOW, (230, 240, 255), panel_rect, border_radius=10)
            pygame.draw.rect(WINDOW, (100, 150, 200), panel_rect, 3, border_radius=10)
        
            steps_text = f"Plan Steps: {len(self.plan)}"
            WINDOW.blit(FONT.render(steps_text, True, BLUE), (panel_x + 10, panel_y + 10))
            expanded_text = f"Expanded States: {self.expanded_states}"
            WINDOW.blit(FONT.render(expanded_text, True, BLUE), (panel_x + 10, panel_y + 40))
            time_text = f"Time: {self.execution_time:.3f}s"
            WINDOW.blit(FONT.render(time_text, True, BLUE), (panel_x + 10, panel_y + 70))
            plan_text = f"Step {self.step}: {self.plan[self.step] if self.step < len(self.plan) else 'Done'}"
            WINDOW.blit(FONT_SMALL.render(plan_text, True, BLACK), (panel_x + 10, panel_y + 100))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x < 50 + CELL_SIZE * BOARD_SIZE and 100 <= y < 100 + CELL_SIZE * BOARD_SIZE:
                i = (y - 100) // CELL_SIZE
                j = (x - 50) // CELL_SIZE
                self.selected_cell = (i, j)

        elif event.type == pygame.KEYDOWN and self.selected_cell:
            i, j = self.selected_cell
            idx = i * BOARD_SIZE + j
            if pygame.K_0 <= event.key <= pygame.K_9:
                num = event.key - pygame.K_0
                if num == 0 or (num not in self.input_state and 0 <= num <= 8):
                    self.input_state[idx] = num
            elif event.key == pygame.K_LEFT:
                self.selected_cell = (i, max(0, j - 1))
            elif event.key == pygame.K_RIGHT:
                self.selected_cell = (i, min(BOARD_SIZE - 1, j + 1))
            elif event.key == pygame.K_UP:
                self.selected_cell = (max(0, i - 1), j)
            elif event.key == pygame.K_DOWN:
                self.selected_cell = (min(BOARD_SIZE - 1, i + 1), j)

    def solve(self, solver, algorithm_name):
        # Tạo belief state ban đầu: tất cả các trạng thái có thể có
        self.show_solving_message = True
        self.current_algorithm = algorithm_name
        self.is_solving = True
        
        self.draw()
        pygame.display.flip()
        pygame.event.pump()
        start_time = time.time()

        try:
            # Belief state ban đầu: tất cả các trạng thái 8-puzzle có thể có
            numbers = list(range(9))
            belief_state = set()
            for perm in itertools.permutations(numbers):
                belief_state.add(perm)
            self.belief_state = belief_state

            # Chạy thuật toán No Observation
            plan, expanded = solver(belief_state)
            self.execution_time = time.time() - start_time
            self.plan = plan
            self.expanded_states = expanded
        except Exception as e:
            self.execution_time = time.time() - start_time
            self.is_solving = False
            return
        
        self.is_solving = False
        if not self.plan:
            self.plan = None

    def reset(self):
        self.input_state = [0] * 9
        self.input_state[0], self.input_state[3], self.input_state[8] = 1, 4, 0
        self.belief_state = None
        self.plan = None
        self.step = 0
        self.expanded_states = 0
        self.execution_time = 0
        self.selected_cell = None
        self.last_step_time = pygame.time.get_ticks()
        self.is_solving = False
        self.current_algorithm = None
        self.show_solving_message = False
        self.current_belief_index = 0

    def randomize(self):
        numbers = list(range(9))
        random.shuffle(numbers)
        self.input_state = numbers
        self.belief_state = None
        self.plan = None
        self.step = 0
        self.expanded_states = 0
        self.execution_time = 0
        self.selected_cell = None
        self.last_step_time = pygame.time.get_ticks()
        self.is_solving = False
        self.current_algorithm = None
        self.show_solving_message = False
        self.current_belief_index = 0

    def update(self):
        if self.belief_state:
            total_states = len(self.belief_state)
            max_index = (total_states - 1) // self.max_display_states
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_time >= self.step_interval:
                self.current_belief_index = (self.current_belief_index + 1) % (max_index + 1)
                self.last_step_time = current_time
        
        if self.plan and self.step < len(self.plan) - 1 and self.is_solving:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_time >= self.step_interval:
                self.step += 1
                self.last_step_time = current_time

def main():
    gui = PuzzleGUI()
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