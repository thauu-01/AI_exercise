import pygame
import sys
import time
import copy
import itertools
import random

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
pygame.display.set_caption("8-Puzzle Solver with Partial Observability")

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


def tim_o_trong(state):
    state = list(state)
    for i in range(len(state)):
        if state[i] == 0:
            return i // BOARD_SIZE, i % BOARD_SIZE
    return None

def is_valid(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def get_next_states(state):
    state = list(state)
    _x, _y = tim_o_trong(state)
    next_states = []
    for dx, dy in MOVES:
        new_x, new_y = _x + dx, _y + dy
        if is_valid(new_x, new_y):
            new_state = list(state)
            blank_idx = _x * BOARD_SIZE + _y
            new_idx = new_x * BOARD_SIZE + new_y
            new_state[blank_idx], new_state[new_idx] = new_state[new_idx], new_state[blank_idx]
            next_states.append(tuple(new_state))
    return next_states

def generate_possible_states(observed_state, max_states=100):
    known_numbers = []
    unknown_positions = []
    for i in range(9):
        val = observed_state[i]
        if val != "?" and val != 0:
            known_numbers.append(val)
        elif val == "?" or val == 0:
            unknown_positions.append(i)
    
    missing_numbers = list(set(range(9)) - set(known_numbers))
    possible_states = []
    for perm in itertools.permutations(missing_numbers, len(unknown_positions)):
        new_state = list(observed_state)
        for idx, pos in enumerate(unknown_positions):
            new_state[pos] = perm[idx] if idx < len(perm) else 0
        if sorted([x for x in new_state if x != "?"]) == list(range(9)):
            possible_states.append(tuple(new_state))
        if len(possible_states) >= max_states:  
            break
    return possible_states

def get_percept(state):
    blank_i, blank_j = tim_o_trong(state)
    right_val = state[blank_i * BOARD_SIZE + blank_j + 1] if blank_j + 1 < 3 else None
    return (blank_i, blank_j, right_val)

def predict(belief_state, action_idx):
    new_belief_state = set()
    direction = MOVES[action_idx]
    for state in belief_state:
        new_state = move(state, direction)
        if new_state:
            new_belief_state.add(new_state)
        new_belief_state.add(state)  
    return new_belief_state

def update(belief_state, percept):
    blank_i, blank_j, right_val = percept
    new_belief_state = set()
    for state in belief_state:
        state_list = list(state)
        state_blank_i, state_blank_j = tim_o_trong(state_list)
        state_right_val = state_list[blank_i * BOARD_SIZE + blank_j + 1] if blank_j + 1 < 3 else None
        if (state_blank_i, state_blank_j, state_right_val) == (blank_i, blank_j, right_val):
            new_belief_state.add(state)
    return new_belief_state

def move(state, direction):
    new_state = list(state)
    blank_i, blank_j = tim_o_trong(new_state)
    di, dj = direction
    new_i, new_j = blank_i + di, blank_j + dj
    if 0 <= new_i < 3 and 0 <= new_j < 3:
        new_state[blank_i * BOARD_SIZE + blank_j], new_state[new_i * BOARD_SIZE + new_j] = \
            new_state[new_i * BOARD_SIZE + new_j], new_state[blank_i * BOARD_SIZE + blank_j]
        return tuple(new_state)
    return None

def is_goal_belief_state(belief_state):
    return all(state == GOAL_STATE for state in belief_state)

def and_or_search(initial_belief_state):
    def or_search(belief_state, path, step):
        if is_goal_belief_state(belief_state):
            return path, step
        
        for action_idx, direction_name in enumerate(DIRECTION_NAMES):
            predicted_belief = predict(belief_state, action_idx)
            if not predicted_belief:
                continue
            
            possible_percepts = set()
            for state in predicted_belief:
                percept = get_percept(state)
                possible_percepts.add(percept)
            
            conditional_plan = []
            for percept in possible_percepts:
                updated_belief = update(predicted_belief, percept)
                if not updated_belief:
                    continue
                
                sub_plan, sub_step = or_search(updated_belief, path + [f"After {direction_name}, if percept={percept}"], step + 1)
                if sub_plan is None:
                    return None, step
                conditional_plan.append((percept, sub_plan))
            
            if conditional_plan:
                return path + [f"Do {direction_name}"] + [f"If percept={p}, then {sub}" for p, sub in conditional_plan], step
        
        return None, step

    return or_search(initial_belief_state, [], 0)

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
        self.input_state = ["?"] * 9  
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
            Button("Run", 850, 700, 140, 50, lambda: self.solve(and_or_search, "Partial Observability Search"), (0, 255, 0)),
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
                elif val == "?":
                    cell_color = (255, 220, 220)
                else:
                    cell_color = WHITE
                
                if is_input and self.selected_cell == (i, j):
                    cell_color = (144, 238, 144)
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, (50, 50, 50), rect, 1, border_radius=5)
                
                if val != 0 and val != "?":
                    text = FONT.render(str(val), True, (255, 69, 0))
                    text_rect = text.get_rect(center=rect.center)
                    WINDOW.blit(text, text_rect)
                elif val == "?":
                    text = FONT.render("?", True, (255, 69, 0))
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

        title_text = FONT.render(f"Trang thai niem tin ({len(belief_state)} trang thai)", True, BLACK)
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
            solving_text = f"Dang giai thuat toan {self.current_algorithm}"
            text = FONT.render(solving_text, True, BLUE)
            WINDOW.blit(text, (50, 650))
    
        if self.plan:
            panel_x, panel_y = 40, 390
            panel_width = 600
            panel_height = 140
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
            pygame.draw.rect(WINDOW, (230, 240, 255), panel_rect, border_radius=10)
            pygame.draw.rect(WINDOW, (100, 150, 200), panel_rect, 3, border_radius=10)
        
            steps_text = f"Số bước trong kế hoạch: {len(self.plan)}"
            WINDOW.blit(FONT.render(steps_text, True, BLUE), (panel_x + 10, panel_y + 10))
            expanded_text = f"Trạng thái mở rộng: {self.expanded_states}"
            WINDOW.blit(FONT.render(expanded_text, True, BLUE), (panel_x + 10, panel_y + 40))
            time_text = f"Thời gian: {self.execution_time:.3f}s"
            WINDOW.blit(FONT.render(time_text, True, BLUE), (panel_x + 10, panel_y + 70))
            plan_text = f"Bước {self.step}: {self.plan[self.step] if self.step < len(self.plan) else 'Hoàn thành'}"
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
            elif event.key == pygame.K_BACKSPACE:
                self.input_state[idx] = "?"
            elif event.key == pygame.K_LEFT:
                self.selected_cell = (i, max(0, j - 1))
            elif event.key == pygame.K_RIGHT:
                self.selected_cell = (i, min(BOARD_SIZE - 1, j + 1))
            elif event.key == pygame.K_UP:
                self.selected_cell = (max(0, i - 1), j)
            elif event.key == pygame.K_DOWN:
                self.selected_cell = (min(BOARD_SIZE - 1, i + 1), j)

    def solve(self, solver, algorithm_name):
    
        known_numbers = [x for x in self.input_state if x != "?" and x != 0]
        if len(known_numbers) != 3 or len(set(known_numbers)) != len(known_numbers): 
            return  
        
        self.show_solving_message = True
        self.current_algorithm = algorithm_name
        self.is_solving = True
        
        self.draw()
        pygame.display.flip()
        pygame.event.pump()
        start_time = time.time()

        try:
            possible_states = generate_possible_states(self.input_state)
            if not possible_states:
                self.is_solving = False
                return
            belief_state = set(possible_states)
            self.belief_state = belief_state
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
        self.input_state = ["?"] * 9
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
        self.input_state = ["?"] * 9
        positions = random.sample(range(9), 3)
        for i, pos in enumerate(positions):
            self.input_state[pos] = numbers[i]
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
