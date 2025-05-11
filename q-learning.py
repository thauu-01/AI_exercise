import pygame
import sys
import random
from collections import deque

# Khởi tạo Pygame
pygame.init()

# Các hằng số và cấu hình
CELL_SIZE = 50
BOARD_SIZE = 3  # Lưới 3x3 làm không gian trạng thái
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Q-Learning ")

# Màu sắc
BACKGROUND_COLOR = (200, 220, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (180, 200, 220)
RED = (255, 69, 0)
FONT = pygame.font.SysFont(None, 30)
FONT_SMALL = pygame.font.SysFont(None, 20)


ACTIONS = ['up', 'down', 'left', 'right']


STATES = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)]

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
        self.grid = {(i, j): 0 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)}  # Phần thưởng ban đầu
        self.selected_cell = None
        self.q_table = {(s, a): 0 for s in STATES for a in ACTIONS}  # Bảng Q, khởi tạo bằng 0
        self.steps = []
        self.step_index = 0
        self.last_step_time = pygame.time.get_ticks()
        self.step_interval = 1000
        self.is_learning = False
        self.show_learning_message = False
        self.result = None
        self.alpha = 0.1  # Tốc độ học
        self.gamma = 0.9  # Hệ số chiết khấu
        self.current_state = None
        self.current_action = None
        self.reward = 0
        self.next_state = None

        self.buttons = [
            Button("Reset", 50, 650, 120, 50, self.reset, (192, 192, 192)),
            Button("Run", 200, 650, 140, 50, self.learn, (0, 255, 0)),
            Button("Random", 370, 650, 140, 50, self.randomize, (128, 128, 128)),
        ]

    def get_next_state(self, state, action):
        i, j = state
        if action == 'up' and i > 0: i -= 1
        elif action == 'down' and i < BOARD_SIZE - 1: i += 1
        elif action == 'left' and j > 0: j -= 1
        elif action == 'right' and j < BOARD_SIZE - 1: j += 1
        return (i, j)

    def get_reward(self, state):
       
        if state == (2, 2):
            return 10
        elif state not in STATES:
            return -1
        return self.grid.get(state, 0)  

    def draw_board(self, x_offset, y_offset, title):
        title_text = FONT.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(x_offset + CELL_SIZE * BOARD_SIZE // 2, y_offset - 40))
        WINDOW.blit(title_text, title_rect)

        board_rect = pygame.Rect(x_offset - 10, y_offset - 10, CELL_SIZE * BOARD_SIZE + 20, CELL_SIZE * BOARD_SIZE + 20)
        pygame.draw.rect(WINDOW, (230, 240, 255), board_rect, border_radius=10)
        pygame.draw.rect(WINDOW, (100, 150, 200), board_rect, 3, border_radius=10)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                state = (i, j)
                val = self.grid[state]
                rect = pygame.Rect(x_offset + j * CELL_SIZE, y_offset + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell_color = WHITE
                if self.selected_cell == (i, j):
                    cell_color = (144, 238, 144)
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, (50, 50, 50), rect, 1, border_radius=5)
                
                text = FONT.render(str(val) if val != 0 else '', True, RED)
                text_rect = text.get_rect(center=rect.center)
                WINDOW.blit(text, text_rect)

    def draw_q_table(self, x_offset, y_offset):
        title_text = FONT.render("Q-Table", True, BLACK)
        WINDOW.blit(title_text, (x_offset, y_offset - 40))

        y_pos = y_offset
        for state in STATES:
            x_pos = x_offset
            state_text = FONT_SMALL.render(f"State {state}: ", True, BLACK)
            WINDOW.blit(state_text, (x_pos, y_pos))
            x_pos += 100
            for action in ACTIONS:
                q_value = self.q_table[(state, action)]
                action_text = FONT_SMALL.render(f"{action}: {q_value:.2f}", True, BLACK)
                WINDOW.blit(action_text, (x_pos, y_pos))
                x_pos += 150
            y_pos += 30

    def draw(self):
        WINDOW.fill(BACKGROUND_COLOR)
        self.draw_board(50, 100, "State Grid (Reward)")
        self.draw_q_table(400, 100)
        
        for button in self.buttons:
            button.draw()

        if self.show_learning_message:
            learning_text = "Running Q-Learning..."
            text = FONT.render(learning_text, True, BLUE)
            WINDOW.blit(text, (50, 600))

        if self.result is not None:
            result_text = "Optimal Policy Found!" if self.result else "No Convergence!"
            text = FONT.render(result_text, True, BLUE)
            WINDOW.blit(text, (50, 550))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x < 50 + CELL_SIZE * BOARD_SIZE and 100 <= y < 100 + CELL_SIZE * BOARD_SIZE:
                i = (y - 100) // CELL_SIZE
                j = (x - 50) // CELL_SIZE
                self.selected_cell = (i, j)

        elif event.type == pygame.KEYDOWN and self.selected_cell:
            i, j = self.selected_cell
            state = (i, j)
            if pygame.K_0 <= event.key <= pygame.K_9:
                num = event.key - pygame.K_0
                self.grid[state] = num
            elif event.key == pygame.K_BACKSPACE:
                self.grid[state] = 0

    def learn(self):
        self.show_learning_message = True
        self.is_learning = True
        self.step_index = 0
        self.steps = []
        self.result = None

        self.draw()
        pygame.display.flip()
        pygame.event.pump()

       
        episodes = 10
        for episode in range(episodes):
            current_state = (0, 0) 
            while current_state in STATES:
                
                action = random.choice(ACTIONS)
                next_state = self.get_next_state(current_state, action)
                reward = self.get_reward(next_state)

              
                old_q = self.q_table[(current_state, action)]
                next_max_q = max(self.q_table[(next_state, a)] for a in ACTIONS) if next_state in STATES else 0
                new_q = old_q + self.alpha * (reward + self.gamma * next_max_q - old_q)
                self.q_table[(current_state, action)] = new_q

              
                step = f"Q[{current_state}, {action}] = {old_q:.2f} -> {new_q:.2f} (r={reward})"
                self.steps.append(step)

               
                self.draw()
                pygame.display.flip()
                pygame.time.wait(500)  

                current_state = next_state
                if reward == 10:  
                    break

        self.result = True 
        self.show_learning_message = False
        self.is_learning = False

    def reset(self):
        self.grid = {(i, j): 0 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)}
        self.q_table = {(s, a): 0 for s in STATES for a in ACTIONS}
        self.steps = []
        self.step_index = 0
        self.is_learning = False
        self.show_learning_message = False
        self.result = None
        self.selected_cell = None

    def randomize(self):
    
        self.grid = {(i, j): random.randint(-5, 5) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)}
        self.grid[(2, 2)] = 10  
        self.q_table = {(s, a): 0 for s in STATES for a in ACTIONS}
        self.steps = []
        self.step_index = 0
        self.result = None
        self.selected_cell = None
        self.draw()
        pygame.display.flip()

    def update(self):
        if self.steps and self.step_index < len(self.steps) - 1 and self.is_learning:
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