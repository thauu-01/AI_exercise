import pygame
import sys
import random
from collections import deque
import itertools
import pickle
import os

# Khởi tạo Pygame
pygame.init()

# Các hằng số và cấu hình
CELL_SIZE = 60
BOARD_SIZE = 3
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("8-Puzzle Solver with Pre-trained Q-Table and Enhanced Rewards")

# Màu sắc
BACKGROUND_COLOR = (200, 220, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (180, 200, 220)
RED = (255, 69, 0)
OPTIMAL_PATH_COLOR = (255, 165, 0)
FONT = pygame.font.SysFont(None, 40)
FONT_SMALL = pygame.font.SysFont(None, 30)

ACTIONS = ['up', 'down', 'left', 'right']
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Các hàm hỗ trợ
def is_solvable(state):
    inversion_count = 0
    state_list = [x for x in state if x != 0]
    for i in range(len(state_list)):
        for j in range(i + 1, len(state_list)):
            if state_list[i] > state_list[j]:
                inversion_count += 1
    return inversion_count % 2 == 0

def manhattan_distance(state, goal):
    distance = 0
    for i in range(BOARD_SIZE * BOARD_SIZE):
        if state[i] != 0:
            current_x, current_y = i // BOARD_SIZE, i % BOARD_SIZE
            goal_idx = goal.index(state[i])
            goal_x, goal_y = goal_idx // BOARD_SIZE, goal_idx % BOARD_SIZE
            distance += abs(current_x - goal_x) + abs(current_y - goal_y)
    return distance

def manhattan_distance_per_tile(state, goal, index):
    if state[index] == 0:
        return 0
    current_x, current_y = index // BOARD_SIZE, index % BOARD_SIZE
    goal_idx = goal.index(state[index])
    goal_x, goal_y = goal_idx // BOARD_SIZE, goal_idx % BOARD_SIZE
    return abs(current_x - goal_x) + abs(current_y - goal_y)

def correct_tiles(state, goal=GOAL_STATE):
    return sum(1 for i in range(BOARD_SIZE * BOARD_SIZE) if state[i] == goal[i])

# Tạo tập trạng thái
ALL_STATES = set(itertools.permutations(range(9)))
STATES = [state for state in ALL_STATES if is_solvable(state)]

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

# Lớp QLearningGUI
class QLearningGUI:
    def __init__(self):
        self.input_state = (2, 6, 5, 8, 0, 7, 4, 3, 1)  
        self.selected_cell = None
        self.q_table = self.load_q_table()  
        self.steps = []
        self.step_index = 0
        self.last_step_time = pygame.time.get_ticks()
        self.step_interval = 500
        self.is_learning = False
        self.show_learning_message = False
        self.result = None
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.3
        self.min_epsilon = 0.01
        self.epsilon_decay = 0.995
        self.current_state = None
        self.current_action = None
        self.reward = 0
        self.next_state = None
        self.optimal_path = []
        self.expanded_states = 0
        self.previous_state = None

        self.buttons = [
            Button("Train", 50, 650, 120, 50, self.train, (0, 255, 0)),
            Button("Run", 200, 650, 140, 50, self.find_optimal_path, (0, 0, 255)),
            Button("Reset", 540, 650, 120, 50, self.reset, (192, 192, 192)),
            Button("Stop", 690, 650, 120, 50, self.stop_training, (255, 0, 0)),
        ]

    def find_blank(self, state):
        for i in range(len(state)):
            if state[i] == 0:
                return i // BOARD_SIZE, i % BOARD_SIZE

    def get_next_state(self, state, action):
        blank_x, blank_y = self.find_blank(state)
        new_state = list(state)
        if action == 'up' and blank_x > 0:
            new_state[blank_x * 3 + blank_y], new_state[(blank_x - 1) * 3 + blank_y] = new_state[(blank_x - 1) * 3 + blank_y], new_state[blank_x * 3 + blank_y]
        elif action == 'down' and blank_x < 2:
            new_state[blank_x * 3 + blank_y], new_state[(blank_x + 1) * 3 + blank_y] = new_state[(blank_x + 1) * 3 + blank_y], new_state[blank_x * 3 + blank_y]
        elif action == 'left' and blank_y > 0:
            new_state[blank_x * 3 + blank_y], new_state[blank_x * 3 + blank_y - 1] = new_state[blank_x * 3 + blank_y - 1], new_state[blank_x * 3 + blank_y]
        elif action == 'right' and blank_y < 2:
            new_state[blank_x * 3 + blank_y], new_state[blank_x * 3 + blank_y + 1] = new_state[blank_x * 3 + blank_y + 1], new_state[blank_x * 3 + blank_y]
        return tuple(new_state)

    def get_reward(self, new_state, previous_state=None):
        if new_state == previous_state:
            return -20
        if new_state not in STATES:
            return -20
        
        if new_state == GOAL_STATE:
            return 200
        
        reward = -0.1
        reward += -manhattan_distance(new_state, GOAL_STATE) * 0.5
        reward += correct_tiles(new_state, GOAL_STATE) * 5
        
        if previous_state:
            prev_distance = manhattan_distance(previous_state, GOAL_STATE)
            curr_distance = manhattan_distance(new_state, GOAL_STATE)
            prev_correct = correct_tiles(previous_state, GOAL_STATE)
            curr_correct = correct_tiles(new_state, GOAL_STATE)
            if curr_distance < prev_distance:
                reward += 10
            elif curr_distance > prev_distance:
                reward -= 5
            if curr_correct > prev_correct:
                reward += 10
        
        return reward

    def get_reward_per_tile(self, state, index):
        if state == GOAL_STATE:
            return 5.0
        distance = manhattan_distance_per_tile(state, GOAL_STATE, index)
        is_correct = state[index] == GOAL_STATE[index]
        base_penalty = -0.1 / (BOARD_SIZE * BOARD_SIZE)
        distance_penalty = -distance * 0.5 / (BOARD_SIZE * BOARD_SIZE)
        position_reward = 5.0 if is_correct else 0.0
        return base_penalty + distance_penalty + position_reward

    def get_optimal_path(self, start_state, goal_state):
        path = [start_state]
        current_state = start_state
        max_steps = 100
        visited = set([current_state])
        
        for _ in range(max_steps):
            if current_state == goal_state:
                return path
            if (current_state, ACTIONS[0]) not in self.q_table:
                return []
            best_action = max(ACTIONS, key=lambda a: self.q_table.get((current_state, a), -float('inf')))
            next_state = self.get_next_state(current_state, best_action)
            if next_state == current_state or next_state in visited:
                return []
            path.append(next_state)
            visited.add(next_state)
            current_state = next_state
        
        return []

    def draw_board(self, state, x_offset, y_offset, title, show_rewards=False):
        title_text = FONT.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(x_offset + CELL_SIZE * BOARD_SIZE // 2, y_offset - 40))
        WINDOW.blit(title_text, title_rect)

        board_rect = pygame.Rect(x_offset - 10, y_offset - 10, CELL_SIZE * BOARD_SIZE + 20, CELL_SIZE * BOARD_SIZE + 20)
        pygame.draw.rect(WINDOW, (230, 240, 255), board_rect, border_radius=10)
        pygame.draw.rect(WINDOW, (100, 150, 200), board_rect, 3, border_radius=10)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                val = state[i * BOARD_SIZE + j]
                index = i * BOARD_SIZE + j
                rect = pygame.Rect(x_offset + j * CELL_SIZE, y_offset + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell_color = WHITE
                if state in self.optimal_path and title == "Path to Goal":
                    cell_color = OPTIMAL_PATH_COLOR
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, (50, 50, 50), rect, 1, border_radius=5)
                
                text = FONT.render(str(val) if val != 0 else '', True, RED)
                text_rect = text.get_rect(center=rect.center)
                WINDOW.blit(text, text_rect)

                if show_rewards:
                    reward_val = self.get_reward_per_tile(state, index)
                    reward_text = FONT_SMALL.render(f"{reward_val:.1f}", True, BLUE)
                    reward_rect = reward_text.get_rect(center=(rect.centerx, rect.centery + 20))
                    WINDOW.blit(reward_text, reward_rect)

    def draw_q_table(self, x_offset, y_offset):
        title_text = FONT.render("Q-Table (Top 10 States)", True, BLACK)
        WINDOW.blit(title_text, (x_offset, y_offset - 40))

        y_pos = y_offset
        displayed_states = list(self.q_table.keys())[:10]
        for state, action in displayed_states:
            x_pos = x_offset
            state_text = FONT_SMALL.render(f"State {state[:3]}... : ", True, BLACK)
            WINDOW.blit(state_text, (x_pos, y_pos))
            x_pos += 250
            q_value = self.q_table[(state, action)]
            action_text = FONT_SMALL.render(f"{action}: {q_value:.2f}", True, BLACK)
            WINDOW.blit(action_text, (x_pos, y_pos))
            y_pos += 30

    def draw(self):
        WINDOW.fill(BACKGROUND_COLOR)
        self.draw_board(self.input_state, 50, 100, "8-Puzzle Board")
        self.draw_board(self.input_state, 300, 100, "Reward Board", show_rewards=True)
        if self.optimal_path:
            self.draw_board(self.optimal_path[self.step_index], 50, 350, "Path to Goal")
        else:
            self.draw_board(self.input_state, 50, 350, "Path to Goal")
        self.draw_q_table(1000, 100)
        
        for button in self.buttons:
            button.draw()

        if self.show_learning_message:
            learning_text = f"Training Q-Learning... Episode: {self.current_episode}/{self.total_episodes}"
            if len(self.q_table) > 0:
                learning_text += " (Continuing from existing Q-table)"
            text = FONT.render(learning_text, True, BLUE)
            WINDOW.blit(text, (50, 600))

        if self.result is not None:
            result_text = f"States Expanded: {self.expanded_states}"
            text = FONT.render(result_text, True, BLUE)
            WINDOW.blit(text, (50, 550))
        
        if self.optimal_path:
            path_text = FONT_SMALL.render(f"Optimal Path Length: {len(self.optimal_path)}", True, BLACK)
            WINDOW.blit(path_text, (50, 500))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x < 50 + CELL_SIZE * BOARD_SIZE and 100 <= y < 100 + CELL_SIZE * BOARD_SIZE:
                i = (y - 100) // CELL_SIZE
                j = (x - 50) // CELL_SIZE
                self.selected_cell = (i, j)

    def train(self):
        self.show_learning_message = True
        self.is_learning = True
        self.step_index = 0
        self.steps = []
        self.result = None
        self.expanded_states = 0
        current_epsilon = self.epsilon
        self.total_episodes = 2000
        self.current_episode = 0
        max_steps = 1000


        if len(self.q_table) > 0:
            print("Continuing training with existing Q-table")
        else:
            print("Starting training with new Q-table")

        for episode in range(self.total_episodes):
            if not self.is_learning:
                break
            self.current_episode = episode + 1
            current_state = (2, 6, 5, 8, 0, 7, 4, 3, 1) 
            self.previous_state = current_state
            steps = 0

            while current_state != GOAL_STATE and steps < max_steps:
                if random.random() < current_epsilon:
                    action = random.choice(ACTIONS)
                else:
                    action = max(ACTIONS, key=lambda a: self.q_table.get((current_state, a), 0))

                next_state = self.get_next_state(current_state, action)
                reward = self.get_reward(next_state, current_state)

                if (current_state, action) not in self.q_table:
                    self.q_table[(current_state, action)] = 0
                old_q = self.q_table[(current_state, action)]
                next_max_q = max(self.q_table.get((next_state, a), 0) for a in ACTIONS) if (next_state, ACTIONS[0]) in self.q_table else 0
                new_q = old_q + self.alpha * (reward + self.gamma * next_max_q - old_q)
                self.q_table[(current_state, action)] = new_q

                step = f"Q[{current_state}, {action}] = {old_q:.2f} -> {new_q:.2f} (r={reward:.2f})"
                self.steps.append(step)

                current_state = next_state
                self.expanded_states += 1
                self.previous_state = current_state
                steps += 1

   
            current_epsilon = max(self.min_epsilon, current_epsilon * self.epsilon_decay)

        
            if episode % 10 == 0:
                self.draw()
                pygame.display.flip()
                pygame.event.pump()

      
            if episode % 100 == 0:
                q_table_path = r"D:\tri tue nhan tao\New folder\123\q_table.pkl"
                with open(q_table_path, 'wb') as f:
                    pickle.dump(self.q_table, f)


        q_table_path = r"D:\tri tue nhan tao\New folder\123\q_table.pkl"
        with open(q_table_path, 'wb') as f:
            pickle.dump(self.q_table, f)
        
        self.result = True
        self.show_learning_message = False
        self.is_learning = False

    def load_q_table(self):
        q_table_path = r"D:\tri tue nhan tao\New folder\123\q_table.pkl"
        if os.path.exists(q_table_path):
            try:
                with open(q_table_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading Q-table: {e}")
                return {}
        return {}

    def find_optimal_path(self):
        if not self.q_table:
            self.q_table = self.load_q_table()
            if not self.q_table:
                self.show_learning_message = True
                self.train()
                self.show_learning_message = False
        
        self.optimal_path = self.get_optimal_path(self.input_state, GOAL_STATE)
        self.step_index = 0
        self.result = bool(self.optimal_path)

    def stop_training(self):
        self.is_learning = False
        self.show_learning_message = False
        self.result = None

    def reset(self):
        self.input_state = (2, 6, 5, 8, 0, 7, 4, 3, 1)  
        self.q_table = self.load_q_table()  
        self.steps = []
        self.step_index = 0
        self.is_learning = False
        self.show_learning_message = False
        self.result = None
        self.selected_cell = None
        self.optimal_path = []
        self.expanded_states = 0
        self.previous_state = None

    def update(self):
        if self.optimal_path and self.step_index < len(self.optimal_path) - 1:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_time >= self.step_interval:
                self.step_index += 1
                self.last_step_time = current_time

def main():
    gui = QLearningGUI()
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
