import pygame
import sys
from collections import deque
import time
import heapq
import random
import math

pygame.init()

CELL_SIZE = 60
BOARD_SIZE = 3
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("8-Puzzle Solver")

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
trang_thai_dich = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Hàm hỗ trợ
def tim_o_trong(state):
    for i in range(len(state)):
        if state[i] == 0:
            return i // BOARD_SIZE, i % BOARD_SIZE

def is_valid(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def get_next_states(state):
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

def is_solvable(state):
    inversion_count = 0
    state_list = [x for x in state if x != 0]
    for i in range(len(state_list)):
        for j in range(i + 1, len(state_list)):
            if state_list[i] > state_list[j]:
                inversion_count += 1
    return inversion_count % 2 == 0

def generate_solvable_puzzle():
    while True:
        state = list(range(9))
        random.shuffle(state)
        if is_solvable(state):
            return state

def manhattan_distance(state, goal):
    distance = 0
    for i in range(BOARD_SIZE * BOARD_SIZE):
        if state[i] != 0:
            current_x, current_y = i // BOARD_SIZE, i % BOARD_SIZE
            goal_idx = goal.index(state[i])
            goal_x, goal_y = goal_idx // BOARD_SIZE, goal_idx % BOARD_SIZE
            distance += abs(current_x - goal_x) + abs(current_y - goal_y)
    return distance

def linear_conflict(state, goal):
    conflict = 0
    size = BOARD_SIZE
    goal_pos = {val: (i // size, i % size) for i, val in enumerate(goal) if val != 0}
    
    # Kiểm tra hàng
    for i in range(size):
        row = state[i * size:(i + 1) * size]
        for j1 in range(size):
            for j2 in range(j1 + 1, size):
                if row[j1] != 0 and row[j2] != 0:
                    if row[j1] in goal_pos and row[j2] in goal_pos:
                        g1_x, g1_y = goal_pos[row[j1]]
                        g2_x, g2_y = goal_pos[row[j2]]
                        if g1_x == i and g2_x == i and j1 < j2 and g1_y > g2_y:
                            conflict += 2
    
    # Kiểm tra cột
    for j in range(size):
        col = [state[i * size + j] for i in range(size)]
        for i1 in range(size):
            for i2 in range(i1 + 1, size):
                if col[i1] != 0 and col[i2] != 0:
                    if col[i1] in goal_pos and col[i2] in goal_pos:
                        g1_x, g1_y = goal_pos[col[i1]]
                        g2_x, g2_y = goal_pos[col[i2]]
                        if g1_y == j and g2_y == j and i1 < i2 and g1_x > g2_x:
                            conflict += 2
    
    return conflict

# Các thuật toán tìm kiếm
def dfs(ban_dau, dich):
    stack = [(ban_dau, [ban_dau])]
    visited = {ban_dau}
    expanded = 0
    while stack:
        current_state, duong_di = stack.pop()
        expanded += 1
        if current_state == dich:
            return duong_di, expanded
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                stack.append((next_state, duong_di + [next_state]))
    return None, expanded

def bfs(ban_dau, dich):
    queue = deque([(ban_dau, [ban_dau])])
    visited = {ban_dau}
    expanded = 0
    while queue:
        current_state, duong_di = queue.popleft()
        expanded += 1
        if current_state == dich:
            return duong_di, expanded
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, duong_di + [next_state]))
    return None, expanded

def ucs(ban_dau, dich):
    pq = [(0, ban_dau, [ban_dau])]
    visited = set()
    expanded = 0
    while pq:
        cost, current_state, duong_di = heapq.heappop(pq)
        if current_state in visited:
            continue
        expanded += 1
        if current_state == dich:
            return duong_di, expanded
        visited.add(current_state)
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                new_cost = cost + 1
                heapq.heappush(pq, (new_cost, next_state, duong_di + [next_state]))
    return None, expanded

def iddfs(ban_dau, dich):
    def dls(current_state, depth, duong_di, visited, expanded):
        if depth < 0:
            return None, expanded
        expanded[0] += 1
        if current_state == dich:
            return duong_di, expanded[0]
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                result, exp = dls(next_state, depth - 1, duong_di + [next_state], visited, expanded)
                if result:
                    return result, exp
        return None, expanded[0]

    depth = 0
    while True:
        visited = {ban_dau}
        expanded = [0]
        result, exp = dls(ban_dau, depth, [ban_dau], visited, expanded)
        if result:
            return result, exp
        depth += 1
        if depth > 50:
            return None, exp

def greedy_search(ban_dau, dich):
    pq = [(manhattan_distance(ban_dau, dich), 0, ban_dau, [ban_dau])]
    visited = set()
    counter = 0
    expanded = 0
    while pq:
        _, _, current_state, duong_di = heapq.heappop(pq)
        if current_state in visited:
            continue
        expanded += 1
        if current_state == dich:
            return duong_di, expanded
        visited.add(current_state)
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                counter += 1
                tu_tim_duong = manhattan_distance(next_state, dich)
                heapq.heappush(pq, (tu_tim_duong, counter, next_state, duong_di + [next_state]))
    return None, expanded

def a_star(ban_dau, dich):
    h_init = manhattan_distance(ban_dau, dich) + linear_conflict(ban_dau, dich)
    pq = [(h_init, 0, ban_dau, [ban_dau])]  # (f_cost, counter, state, path)
    visited = set()
    counter = 0
    expanded = 0
    
    while pq:
        f_cost, _, current_state, duong_di = heapq.heappop(pq)
        if current_state in visited:
            continue
        expanded += 1
        if current_state == dich:
            return duong_di, expanded
        visited.add(current_state)
        g_cost = len(duong_di) - 1
        
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                counter += 1
                g_next = g_cost + 1
                h_next = manhattan_distance(next_state, dich) + linear_conflict(next_state, dich)
                f_next = g_next + h_next
                heapq.heappush(pq, (f_next, counter, next_state, duong_di + [next_state]))
    return None, expanded

def ida_star(ban_dau, dich):
    def search(state, g, threshold, path, visited, expanded):
        f = g + manhattan_distance(state, dich)
        if f > threshold:
            return None, f, expanded[0]
        if state == dich:
            return path, f, expanded[0]
        
        expanded[0] += 1
        min_threshold = float('inf')
        for next_state in get_next_states(state):
            if next_state not in visited:
                visited.add(next_state)
                result, new_f, exp = search(next_state, g + 1, threshold, path + [next_state], visited, expanded)
                if result:
                    return result, new_f, exp
                min_threshold = min(min_threshold, new_f)
        return None, min_threshold, expanded[0]

    threshold = manhattan_distance(ban_dau, dich)
    while True:
        visited = {ban_dau}
        expanded = [0]
        path = [ban_dau]
        result, new_threshold, exp = search(ban_dau, 0, threshold, path, visited, expanded)
        if result:
            return result, exp
        if new_threshold == float('inf'):
            return None, exp
        threshold = new_threshold

def simple_hill_climbing(ban_dau, dich):
    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    
    while current_state != dich:
        expanded += 1
        neighbors = get_next_states(current_state)
        best_neighbor = None
        best_heuristic = float('inf')
        
        for neighbor in neighbors:
            if neighbor not in visited:
                h = manhattan_distance(neighbor, dich)
                if h < best_heuristic:
                    best_heuristic = h
                    best_neighbor = neighbor
        
        if best_neighbor is None or best_heuristic >= manhattan_distance(current_state, dich):
            return None, expanded
            
        current_state = best_neighbor
        visited.add(current_state)
        duong_di.append(current_state)
    
    return duong_di, expanded

def steepest_ascent_hill_climbing(ban_dau, dich):
    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    
    while current_state != dich:
        expanded += 1
        neighbors = get_next_states(current_state)
        best_neighbor = None
        best_heuristic = manhattan_distance(current_state, dich)  

        for neighbor in neighbors:
            if neighbor not in visited:
                h = manhattan_distance(neighbor, dich)
                if h < best_heuristic:  
                    best_heuristic = h
                    best_neighbor = neighbor
    
        if best_neighbor is None or best_heuristic >= manhattan_distance(current_state, dich):
            return None, expanded

        current_state = best_neighbor
        visited.add(current_state)
        duong_di.append(current_state)
    
    return duong_di, expanded

def stochastic_hill_climbing(ban_dau, dich):
    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    max_iterations = 1000
    temperature = 10.0
    
    while current_state != dich and len(duong_di) < max_iterations:
        expanded += 1
        neighbors = get_next_states(current_state)
        valid_neighbors = [n for n in neighbors if n not in visited]
        
        if not valid_neighbors:
            return None, expanded
            
        current_h = manhattan_distance(current_state, dich)
        better_neighbors = [n for n in valid_neighbors if manhattan_distance(n, dich) < current_h]
        
        if better_neighbors and random.random() < 0.8:
            next_state = random.choice(better_neighbors)
        else:
            next_state = random.choice(valid_neighbors)
            delta_h = manhattan_distance(next_state, dich) - current_h
            if delta_h > 0 and random.random() > math.exp(-delta_h / temperature):
                continue
        
        current_state = next_state
        visited.add(current_state)
        duong_di.append(current_state)
        temperature *= 0.99
    
    if current_state == dich:
        return duong_di, expanded
    return None, expanded

def simulated_annealing(ban_dau, dich):
    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    
    initial_h = manhattan_distance(ban_dau, dich)
    temperature = max(100.0, initial_h * 2)
    min_temperature = 0.01
    cooling_rate = 0.99
    max_iterations = 1000
    no_improvement_limit = 100
    no_improvement_count = 0
    
    best_state = current_state
    best_h = initial_h
    
    while temperature > min_temperature and len(duong_di) < max_iterations:
        expanded += 1
        neighbors = get_next_states(current_state)
        valid_neighbors = [n for n in neighbors if n not in visited]
        
        if not valid_neighbors:
            break
            
        next_state = random.choice(valid_neighbors)
        current_h = manhattan_distance(current_state, dich)
        next_h = manhattan_distance(next_state, dich)
        delta_h = next_h - current_h
        
        if delta_h < 0 or random.random() < math.exp(-delta_h / temperature):
            current_state = next_state
            visited.add(current_state)
            duong_di.append(current_state)
            
            if next_h < best_h:
                best_h = next_h
                best_state = current_state
                no_improvement_count = 0
            else:
                no_improvement_count += 1
            
            if current_state == dich:
                return duong_di, expanded
        
        temperature *= cooling_rate
        
        if no_improvement_count >= no_improvement_limit:
            break
    
    if best_state == dich:
        return duong_di, expanded
    return None, expanded

def beam_search(ban_dau, dich, beam_width=3):
    queue = [(manhattan_distance(ban_dau, dich), ban_dau, [ban_dau])]
    visited = {ban_dau}
    expanded = 0
    
    while queue:
        current_level = queue
        queue = []
        expanded += len(current_level)
        
        for _, current_state, duong_di in current_level:
            if current_state == dich:
                return duong_di, expanded
            
            next_states = []
            for next_state in get_next_states(current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    h = manhattan_distance(next_state, dich)
                    next_states.append((h, next_state, duong_di + [next_state]))
            
            if len(next_states) > beam_width and random.random() < 0.3:
                next_states = random.sample(next_states, min(beam_width, len(next_states)))
            else:
                next_states.sort(key=lambda x: x[0])
                next_states = next_states[:beam_width]
            
            queue.extend(next_states)
        
    return None, expanded

# Lớp Button và PuzzleGUI
class Button:
    def __init__(self, text, x, y, width, height, callback, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, self.rect)
        text = FONT.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        WINDOW.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

class PuzzleGUI:
    def __init__(self):
        self.input_state = [0] * 9
        self.result_state = None
        self.selected_cell = None
        self.solution = None
        self.step = 0
        self.expanded_states = 0
        self.no_solution_message = None
        self.message_timer = 0
        self.execution_time = 0
        self.last_step_time = pygame.time.get_ticks()
        self.step_interval = 1000
        self.is_solving = False
        self.beam_width = 3
        self.buttons = [
            Button("DFS", 550, 50, 120, 50, lambda: self.solve(dfs), BUTTON_COLORS[0]),
            Button("BFS", 550, 110, 120, 50, lambda: self.solve(bfs), BUTTON_COLORS[1]),
            Button("UCS", 550, 170, 120, 50, lambda: self.solve(ucs), BUTTON_COLORS[2]),
            Button("IDDFS", 550, 230, 120, 50, lambda: self.solve(iddfs), BUTTON_COLORS[3]),
            Button("Greedy", 550, 290, 120, 50, lambda: self.solve(greedy_search), BUTTON_COLORS[4]),
            Button("A*", 550, 350, 120, 50, lambda: self.solve(a_star), BUTTON_COLORS[5]),
            Button("IDA*", 550, 410, 120, 50, lambda: self.solve(ida_star), BUTTON_COLORS[6]),
            Button("Simple Hill", 750, 50, 200, 50, lambda: self.solve(simple_hill_climbing), BUTTON_COLORS[7]),
            Button("Steepest Hill", 750, 110, 200, 50, lambda: self.solve(steepest_ascent_hill_climbing), (135, 206, 235)),
            Button("Stochastic Hill", 750, 170, 200, 50, lambda: self.solve(stochastic_hill_climbing), (147, 112, 219)),
            Button("Simulated Annealing", 700, 230, 300, 50, lambda: self.solve(simulated_annealing), (255, 140, 0)),
            Button("Beam Search", 1100, 50, 200, 50, lambda: self.solve(lambda s, g: beam_search(s, g, self.beam_width)), (100, 149, 237)),
            Button("Beam Width +", 1100, 110, 200, 50, self.increase_beam_width, (100, 149, 237)),
            Button("Beam Width -", 1100, 170, 200, 50, self.decrease_beam_width, (100, 149, 237)),
            Button("Reset", 550, 590, 120, 50, self.reset, (192, 192, 192)),
            Button("Random", 790, 590, 120, 50, self.randomize, (255, 165, 0))
        ]

    def draw_board(self, state, x_offset, y_offset, title, is_input=False):
    # Vẽ tiêu đề
        title_text = FONT.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(x_offset + CELL_SIZE * BOARD_SIZE // 2, y_offset - 40))
        WINDOW.blit(title_text, title_rect)

    # Vẽ nền bảng
        board_rect = pygame.Rect(x_offset - 10, y_offset - 10, CELL_SIZE * BOARD_SIZE + 20, CELL_SIZE * BOARD_SIZE + 20)
        pygame.draw.rect(WINDOW, (230, 240, 255), board_rect, border_radius=10)  # Nền bảng với góc bo tròn
        pygame.draw.rect(WINDOW, (100, 150, 200), board_rect, 3, border_radius=10)  # Viền bảng

    # Vẽ các ô
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                num = state[i * BOARD_SIZE + j]
                rect = pygame.Rect(x_offset + j * CELL_SIZE, y_offset + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Màu nền ô
                if num == 0:
                    cell_color = (180, 200, 220)  # Màu xám nhạt cho ô trống
                else:
                    cell_color = WHITE
            
            # Hiệu ứng chọn ô (nếu là bảng đầu vào)
                if is_input and self.selected_cell == (i, j):
                    cell_color = (144, 238, 144)  # Màu xanh lá nhạt khi chọn
            
            # Vẽ ô với góc bo tròn và bóng đổ nhẹ
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, (50, 50, 50), rect, 1, border_radius=5)  # Viền ô
            
            # Vẽ số trong ô
                if num != 0:
                    text = FONT.render(str(num), True, (255, 69, 0))  # Màu cam đậm cho số
                    text_rect = text.get_rect(center=rect.center)
                    WINDOW.blit(text, text_rect)
    
    # Thêm lưới phân cách giữa các ô
        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(WINDOW, (150, 180, 210), 
                            (x_offset, y_offset + i * CELL_SIZE), 
                            (x_offset + CELL_SIZE * BOARD_SIZE, y_offset + i * CELL_SIZE), 2)
            pygame.draw.line(WINDOW, (150, 180, 210), 
                            (x_offset + i * CELL_SIZE, y_offset), 
                            (x_offset + i * CELL_SIZE, y_offset + CELL_SIZE * BOARD_SIZE), 2)

    def draw(self):
        WINDOW.fill(BACKGROUND_COLOR)
        self.draw_board(self.input_state, 50, 100, "Trang thai dau", True)
        if self.result_state:
            self.draw_board(self.result_state, 300, 100, "Trang thai cuoi")
        
        for button in self.buttons:
            button.draw()
        
        if self.is_solving:
            text = FONT.render("Dang giai...", True, BLUE)
            WINDOW.blit(text, (50, 550))
        
        if self.solution:
            steps_text = f"So buoc: {len(self.solution) - 1}"
            WINDOW.blit(FONT.render(steps_text, True, BLUE), (50, 400))
            expanded_text = f"Trang thai mo rong: {self.expanded_states}"
            WINDOW.blit(FONT.render(expanded_text, True, BLUE), (50, 430))
            time_text = f"Thoi gian: {self.execution_time:.3f}s"
            WINDOW.blit(FONT.render(time_text, True, BLUE), (50, 460))
            path_text = f"Buoc {self.step}: {self.solution[self.step]}"
            WINDOW.blit(FONT_SMALL.render(path_text, True, BLACK), (50, 490))
        
        if self.no_solution_message and self.message_timer > 0:
            text = FONT.render(self.no_solution_message, True, RED)
            WINDOW.blit(text, (50, 520))
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.no_solution_message = None
        
        beam_width_text = f"Beam Width: {self.beam_width}"
        WINDOW.blit(FONT.render(beam_width_text, True, BLACK), (1100, 240))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x < 50 + CELL_SIZE * BOARD_SIZE and 100 <= y < 100 + CELL_SIZE * BOARD_SIZE:
                i = (y - 100) // CELL_SIZE
                j = (x - 50) // CELL_SIZE
                self.selected_cell = (i, j)
        
        elif event.type == pygame.KEYDOWN and self.selected_cell:
            if pygame.K_0 <= event.key <= pygame.K_9:
                num = event.key - pygame.K_0
                i, j = self.selected_cell
                idx = i * BOARD_SIZE + j
                if num == 0 or num not in self.input_state or self.input_state[idx] == num:
                    self.input_state[idx] = num
            elif event.key == pygame.K_BACKSPACE:
                i, j = self.selected_cell
                self.input_state[i * BOARD_SIZE + j] = 0

    def solve(self, solver):
        if 0 in self.input_state and len(set(self.input_state)) == 9 and all(0 <= x <= 8 for x in self.input_state):
            start_state = tuple(self.input_state)
            if not is_solvable(start_state):
                self.no_solution_message = "Trang thai ban dau khong the giai duoc!"
                self.message_timer = 180
                return
        
            self.is_solving = True
            pygame.display.flip()
        
            self.solution = None
            self.step = 0
            self.expanded_states = 0
            self.result_state = None
            self.no_solution_message = None
            self.message_timer = 0
            self.last_step_time = pygame.time.get_ticks()
        
            start_time = time.time()
            try:
                if solver == beam_search:
                    solution, expanded = solver(start_state, trang_thai_dich, beam_width=self.beam_width)
                else:
                    solution, expanded = solver(start_state, trang_thai_dich)
                self.execution_time = time.time() - start_time
            except Exception as e:
                self.execution_time = time.time() - start_time
                self.no_solution_message = f"Loi khi giai: {str(e)}"
                self.message_timer = 180
                self.is_solving = False
                return
        
            self.is_solving = False
            self.solution = solution
            self.expanded_states = expanded
            if self.solution:
                self.result_state = self.input_state.copy()
            else:
                self.result_state = None
                self.no_solution_message = f"Khong tim thay loi giai! (Mo rong: {expanded})"
                self.message_timer = 180 
            self.selected_cell = None

    def reset(self):
        self.input_state = [0] * 9
        self.result_state = None
        self.solution = None
        self.step = 0
        self.expanded_states = 0
        self.execution_time = 0
        self.no_solution_message = None
        self.selected_cell = None
        self.last_step_time = pygame.time.get_ticks()

    def randomize(self):
        self.input_state = generate_solvable_puzzle()
        self.result_state = None
        self.solution = None
        self.step = 0
        self.expanded_states = 0
        self.execution_time = 0
        self.no_solution_message = None
        self.selected_cell = None
        self.last_step_time = pygame.time.get_ticks()

    def increase_beam_width(self):
        self.beam_width = min(10, self.beam_width + 1)

    def decrease_beam_width(self):
        self.beam_width = max(1, self.beam_width - 1)

    def update(self):
        if self.solution and self.step < len(self.solution) - 1:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_time >= self.step_interval:
                self.step += 1
                self.result_state = list(self.solution[self.step])
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