import pygame
import sys
from collections import deque
import time
import heapq
import random
import math
import numpy as np
import subprocess

from math import exp
pygame.init()

# Cac hang so va cau hinh 
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

# Cac ham ho tro va thuat toan 
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

def dfs(ban_dau, dich):

    stack = [(ban_dau, [ban_dau])]  
    frontier = {ban_dau}  
    explored = set()  
    expanded = 0

    while stack:

        current_state, duong_di = stack.pop()
        frontier.remove(current_state)
        explored.add(current_state)
        expanded += 1

        if current_state == dich:
            return duong_di, expanded

        for next_state in get_next_states(current_state):
            if next_state not in explored and next_state not in frontier:
                stack.append((next_state, duong_di + [next_state]))
                frontier.add(next_state)

    return None, expanded

def bfs(ban_dau, dich):

    queue = deque([(ban_dau, [ban_dau])])  
    frontier = {ban_dau}  
    explored = set()  
    expanded = 0

    while queue:

        current_state, duong_di = queue.popleft()
        frontier.remove(current_state) 
        explored.add(current_state) 
        expanded += 1

        for next_state in get_next_states(current_state):
            if next_state not in explored and next_state not in frontier:

                if next_state == dich:
                    return duong_di + [next_state], expanded
                queue.append((next_state, duong_di + [next_state]))
                frontier.add(next_state)

    return None, expanded

def ucs(ban_dau, dich):

    pq = [(0, 0, ban_dau, [ban_dau])]  
    frontier = {ban_dau: 0} 
    explored = set()  
    expanded = 0
    counter = 0 

    while pq:
        cost, _, current_state, duong_di = heapq.heappop(pq)
        
        if current_state not in frontier:
            continue
        
        del frontier[current_state]
        explored.add(current_state)
        expanded += 1

        if current_state == dich:
            return duong_di, expanded

        for next_state in get_next_states(current_state):
            if next_state not in explored:
                new_cost = cost + 1  
                counter += 1
                
                if next_state not in frontier:
                    frontier[next_state] = new_cost
                    heapq.heappush(pq, (new_cost, counter, next_state, duong_di + [next_state]))

                elif new_cost < frontier[next_state]:
                    frontier[next_state] = new_cost
                    heapq.heappush(pq, (new_cost, counter, next_state, duong_di + [next_state]))

    return None, expanded

def iddfs(ban_dau, dich):
    def depth_limited_dfs(state, path, depth, limit, visited, expanded):
        if depth > limit:
            return None, expanded[0], False  
        expanded[0] += 1
        if state == dich:
            return path, expanded[0], True  
        any_successor = False
        for next_state in get_next_states(state):
            if next_state not in visited:
                visited.add(next_state)
                result, exp, success = depth_limited_dfs(next_state, path + [next_state], 
                                                       depth + 1, limit, visited, expanded)
                visited.remove(next_state)
                if result:
                    return result, exp, True
                any_successor |= success
        return None, expanded[0], any_successor

    max_depth = 0
    total_expanded = 0
    while True:
        visited = {ban_dau}
        expanded = [0]
        result, exp, success = depth_limited_dfs(ban_dau, [ban_dau], 0, max_depth, visited, expanded)
        total_expanded += exp
        if result:
            return result, total_expanded
        if not success and exp == 0:  
            return None, total_expanded
        max_depth += 1

def greedy_search(ban_dau, dich):

    pq = [(manhattan_distance(ban_dau, dich), 0, ban_dau, [ban_dau])] 
    frontier = {ban_dau: manhattan_distance(ban_dau, dich)} 
    explored = set() 
    expanded = 0
    counter = 0 

    while pq:
        h_value, _, current_state, duong_di = heapq.heappop(pq)
        
        if current_state not in frontier:
            continue
        
        del frontier[current_state]
        explored.add(current_state)
        expanded += 1

        if current_state == dich:
            return duong_di, expanded

        for next_state in get_next_states(current_state):
            if next_state not in explored and next_state not in frontier:
                h_next = manhattan_distance(next_state, dich)
                frontier[next_state] = h_next
                counter += 1
                heapq.heappush(pq, (h_next, counter, next_state, duong_di + [next_state]))

    return None, expanded

def a_star(ban_dau, dich):

    pq = [(manhattan_distance(ban_dau, dich), 0, 0, ban_dau, [ban_dau])]  
    frontier = {ban_dau: (manhattan_distance(ban_dau, dich), 0)}  
    explored = set() 
    expanded = 0
    counter = 0 

    while pq:
        f_value, g_value, _, current_state, duong_di = heapq.heappop(pq)
        
        if current_state not in frontier or frontier[current_state][0] < f_value:
            continue
        
        del frontier[current_state]
        explored.add(current_state)
        expanded += 1

        if current_state == dich:
            return duong_di, expanded

        for next_state in get_next_states(current_state):
            if next_state not in explored:
                new_g = g_value + 1  
                new_f = new_g + manhattan_distance(next_state, dich)
                counter += 1
                
                if next_state not in frontier:
                    frontier[next_state] = (new_f, new_g)
                    heapq.heappush(pq, (new_f, new_g, counter, next_state, duong_di + [next_state]))
                elif new_f < frontier[next_state][0]:
                    frontier[next_state] = (new_f, new_g)
                    heapq.heappush(pq, (new_f, new_g, counter, next_state, duong_di + [next_state]))

    return None, expanded


def ida_star(ban_dau, dich):
    def search(state, g, path, threshold, visited, expanded):
        f = g + manhattan_distance(state, dich)
        if f > threshold:
            return None, f, expanded[0]
        if state == dich:
            return path, f, expanded[0]
        expanded[0] += 1
        next_threshold = float('inf')
        for next_state in get_next_states(state):
            if next_state not in visited:
                visited.add(next_state)
                result, new_f, exp = search(next_state, g + 1, path + [next_state], 
                                          threshold, visited, expanded)
                visited.remove(next_state)
                if result:
                    return result, new_f, exp
                next_threshold = min(next_threshold, new_f)
        return None, next_threshold, expanded[0]

    threshold = manhattan_distance(ban_dau, dich)
    total_expanded = 0
    while True:
        visited = {ban_dau}
        expanded = [0]
        result, new_threshold, exp = search(ban_dau, 0, [ban_dau], threshold, visited, expanded)
        total_expanded += exp
        if result:
            return result, total_expanded
        if new_threshold == float('inf') or exp == 0:  
            return None, total_expanded
        threshold = new_threshold

def simple_hill_climbing(ban_dau, dich):
    if ban_dau == dich:
        return [ban_dau], 0

    solution = [ban_dau]
    current_state = ban_dau
    current_score = manhattan_distance(current_state, dich)
    expanded = 1

    while True:
        if current_state == dich:
            return solution, expanded

        neighbors = get_next_states(current_state)
        best_move = None
        best_score = current_score

        for neighbor in neighbors:
            expanded += 1
            score = manhattan_distance(neighbor, dich)
            if score < best_score:
                best_score = score
                best_move = neighbor

        if best_move is None or best_score >= current_score:
            return None, expanded

        current_state = best_move
        current_score = best_score
        solution.append(current_state)

def steepest_ascent_hill_climbing(ban_dau, dich):

    if ban_dau == dich:
        return [ban_dau], 0

    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    max_sideways = 100  
    sideways_count = 0

    while current_state != dich:
        expanded += 1
        current_h = manhattan_distance(current_state, dich) + linear_conflict(current_state, dich)
        neighbors = get_next_states(current_state)
        best_neighbors = []
        best_h = float('inf')

        for neighbor in neighbors:
            if neighbor not in visited:
                h = manhattan_distance(neighbor, dich) + linear_conflict(neighbor, dich)
                if h < best_h:
                    best_neighbors = [neighbor]
                    best_h = h
                elif h == best_h:
                    best_neighbors.append(neighbor)

        if not best_neighbors and sideways_count < max_sideways:
            for neighbor in neighbors:
                if neighbor not in visited:
                    h = manhattan_distance(neighbor, dich) + linear_conflict(neighbor, dich)
                    if h == current_h:
                        best_neighbors.append(neighbor)
                        best_h = h

        if not best_neighbors:
            return None, expanded

        current_state = random.choice(best_neighbors)
        duong_di.append(current_state)
        visited.add(current_state)
        if best_h == current_h:
            sideways_count += 1
        else:
            sideways_count = 0

    return duong_di, expanded

def stochastic_hill_climbing(ban_dau, dich, max_iterations=10000, max_sideways=10, initial_temperature=100.0, cooling_rate=0.995):
   
    if ban_dau == dich:
        return [ban_dau], 0

    current_state = ban_dau
    duong_di = [current_state]
    expanded = 0
    sideways_count = 0
    temperature = initial_temperature
    iteration = 0

    while current_state != dich and iteration < max_iterations:
        expanded += 1
        iteration += 1

        current_h = manhattan_distance(current_state, dich) + linear_conflict(current_state, dich)
        
        neighbors = get_next_states(current_state)
        if not neighbors:
            return None, expanded

        weights = []
        next_states = []
        for neighbor in neighbors:
            h = manhattan_distance(neighbor, dich) + linear_conflict(neighbor, dich)
            delta_h = current_h - h  
            if delta_h > 0 or (delta_h == 0 and sideways_count < max_sideways):
                weight = exp(delta_h / temperature) if temperature > 0 else (1 if delta_h >= 0 else 0)
                weights.append(weight)
                next_states.append(neighbor)
            elif random.random() < exp(delta_h / temperature):

                weight = exp(delta_h / temperature) if temperature > 0 else 0
                weights.append(weight)
                next_states.append(neighbor)

        if not next_states:
            return None, expanded

        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
            current_state = random.choices(next_states, weights=weights, k=1)[0]
        else:
            current_state = random.choice(next_states)

        duong_di.append(current_state)
        new_h = manhattan_distance(current_state, dich) + linear_conflict(current_state, dich)
        if new_h == current_h:
            sideways_count += 1
        else:
            sideways_count = 0

        temperature *= cooling_rate

    if current_state == dich:
        return duong_di, expanded
    return None, expanded

def simulated_annealing(ban_dau, dich):

    if ban_dau == dich:
        return [ban_dau], 0

    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    temperature = 1000.0 
    cooling_rate = 0.995 
    max_iterations = 10000  
    iteration = 0

    while current_state != dich and temperature > 0.01 and iteration < max_iterations:
        expanded += 1
        iteration += 1

        neighbors = get_next_states(current_state)
        valid_neighbors = [n for n in neighbors if n not in visited]

        if not valid_neighbors:
            return None, expanded  

        next_state = random.choice(valid_neighbors)
        current_h = manhattan_distance(current_state, dich) + linear_conflict(current_state, dich)
        next_h = manhattan_distance(next_state, dich) + linear_conflict(next_state, dich)
        delta_h = next_h - current_h  

        if delta_h <= 0 or random.random() < exp(-delta_h / temperature):
            current_state = next_state
            duong_di.append(current_state)
            visited.add(current_state)

        temperature *= cooling_rate  

    if current_state == dich:
        return duong_di, expanded
    return None, expanded  

def beam_search(ban_dau, dich, beam_width=3, stochastic=True):

    if ban_dau == dich:
        return [ban_dau], 0

    h = manhattan_distance(ban_dau, dich) + linear_conflict(ban_dau, dich)
    queue = [(h, ban_dau, [ban_dau])]
    visited = {ban_dau}
    expanded = 0

    while queue:

        current_level = queue
        queue = []
        expanded += len(current_level)

        next_states = []
        for _, current_state, duong_di in current_level:
            if current_state == dich:
                return duong_di, expanded

            for next_state in get_next_states(current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    h = manhattan_distance(next_state, dich) + linear_conflict(next_state, dich)
                    next_states.append((h, next_state, duong_di + [next_state]))

        if not next_states:
            return None, expanded 


        if stochastic:
            weights = [exp(-h / 10.0) for h, _, _ in next_states]  
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                weights = [1.0 / len(next_states)] * len(next_states) 
            selected_indices = random.choices(range(len(next_states)), weights=weights, k=min(beam_width, len(next_states)))
            queue = [next_states[i] for i in selected_indices]
        else:

            next_states.sort(key=lambda x: x[0])  
            queue = next_states[:beam_width]

    return None, expanded

def repair_solvability(state):

    state = state[:] 
    if is_solvable(tuple(state)):
        return state  
    non_zero_indices = [i for i, val in enumerate(state) if val != 0]
    
    if len(non_zero_indices) >= 2:
        i, j = non_zero_indices[0], non_zero_indices[1]
        state[i], state[j] = state[j], state[i]

    if not is_solvable(tuple(state)):
        i, j = non_zero_indices[1], non_zero_indices[2] if len(non_zero_indices) > 2 else non_zero_indices[0]
        state[i], state[j] = state[j], state[i]
    
    return state

def genetic_algorithm(ban_dau, dich, population_size=100, max_generations=1000, crossover_rate=0.8, mutation_rate=0.1):
    if ban_dau == dich:
        return [ban_dau], 0

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    def fitness(individual, start_state, goal_state):
        state = start_state
        for move in individual:
            next_states = get_next_states(state)
            for next_state in next_states:
                blank_idx = state.index(0)
                new_blank_idx = next_state.index(0)
                dx = (new_blank_idx // 3 - blank_idx // 3)
                dy = (new_blank_idx % 3 - blank_idx % 3)
                if (dx, dy) == move:
                    state = next_state
                    break
            else:
                continue
        return 1 / (manhattan_distance(state, goal_state) + linear_conflict(state, goal_state) + 1)

    def mutate(individual, mutation_rate=mutation_rate):
        return [random.choice(moves) if random.random() < mutation_rate else m for m in individual]

    def reproduce(parent1, parent2):
        if random.random() >= crossover_rate:
            return parent1[:]
        n = len(parent1)
        c = random.randint(1, n - 1)
        return parent1[:c] + parent2[c:]

    def weighted_random_choices(population, weights, k=2):
        return random.choices(population, weights=weights, k=k)

    seq_length = 20
    population = [[random.choice(moves) for _ in range(seq_length)] for _ in range(population_size)]
    expanded = 0

    for _ in range(max_generations):
        fitness_values = []
        for ind in population:
            fitness_values.append(fitness(ind, ban_dau, dich))
            expanded += 1  
        weights = fitness_values
        population2 = []

        for _ in range(population_size):
            parent1, parent2 = weighted_random_choices(population, weights)
            child = reproduce(parent1, parent2)
            child = mutate(child)
            population2.append(child)

        population = population2

        for individual in population:
            state = ban_dau
            path = [state]
            for move in individual:
                next_states = get_next_states(state)
                for next_state in next_states:
                    blank_idx = state.index(0)
                    new_blank_idx = next_state.index(0)
                    dx = (new_blank_idx // 3 - blank_idx // 3)
                    dy = (new_blank_idx % 3 - blank_idx % 3)
                    if (dx, dy) == move:
                        if not is_solvable(next_state):
                            break
                        state = next_state
                        path.append(state)
                        expanded += 1 
                        break
                else:
                    continue
                if state == dich:
                    return path, expanded

    best_individual = max(population, key=lambda ind: fitness(ind, ban_dau, dich))
    state = ban_dau
    path = [state]
    for move in best_individual:
        next_states = get_next_states(state)
        for next_state in next_states:
            blank_idx = state.index(0)
            new_blank_idx = next_state.index(0)
            dx = (new_blank_idx // 3 - blank_idx // 3)
            dy = (new_blank_idx % 3 - blank_idx % 3)
            if (dx, dy) == move:
                if not is_solvable(next_state):
                    break
                state = next_state
                path.append(state)
                expanded += 1
                break
        else:
            continue
    if state == dich:
        return path, expanded
    return None, expanded


def ao_star(ban_dau, dich, max_iterations=10000):
    if ban_dau == dich:
        return [ban_dau], 0

    actions = ["MoveUp", "MoveDown", "MoveLeft", "MoveRight"]

    def apply_action(state, action):
        blank_idx = state.index(0)
        x, y = blank_idx // 3, blank_idx % 3
        dx, dy = {"MoveUp": (-1, 0), "MoveDown": (1, 0), "MoveLeft": (0, -1), "MoveRight": (0, 1)}[action]
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < 3 and 0 <= new_y < 3:
            new_state = list(state)
            new_idx = new_x * 3 + new_y
            new_state[blank_idx], new_state[new_idx] = new_state[new_idx], new_state[blank_idx]
            return tuple(new_state)
        return None

    def get_action_outcomes(state, action):
        outcomes = []
        success_state = apply_action(state, action)
        if success_state:
            outcomes.append(success_state)
        outcomes.append(state) 
        return outcomes

    def heuristic(state, goal):
        return manhattan_distance(state, goal) + linear_conflict(state, goal)


    def or_search(state, problem, path, expanded):
        if state == problem['goal']:
            return [], expanded[0]  
        if state in path:
            return None, expanded[0]  
        for action in problem['actions']:
            plan = and_search(get_action_outcomes(state, action), problem, [state] + path, expanded)
            if plan is not None:
                return [action] + [plan], expanded[0]
        return None, expanded[0]

    def and_search(states, problem, path, expanded):
        plans = []
        for si in states:
            expanded[0] += 1
            plan = or_search(si, problem, path, expanded)
            if plan is None:
                return None, expanded[0]
            plans.append({"state": si, "plan": plan})
        if len(plans) == 1:
            return plans[0]["plan"], expanded[0]
        result = []
        for i, plan in enumerate(plans[:-1]):
            result.append(f"if State = {plan['state']} then")
            result.append(plan['plan'])
            result.append("else")
        result.append(plans[-1]["plan"])
        return result, expanded[0]

    def convert_plan_to_path(plan, start_state, goal, max_steps=100):
        path = [start_state]
        current = start_state
        steps = 0
        while current != goal and steps < max_steps:
            if not plan or isinstance(plan, str):
                return None
            action = plan[0]
            outcomes = get_action_outcomes(current, action)
            subplans = plan[1]
            for subplan in subplans:
                if isinstance(subplan, dict) and subplan["state"] == outcomes[0]: 
                    next_state = outcomes[0]
                    path.append(next_state)
                    current = next_state
                    plan = subplan["plan"]
                    break
                elif isinstance(subplan, dict) and subplan["state"] == outcomes[1]:  
                    next_state = outcomes[1]
                    path.append(next_state)
                    current = next_state
                    plan = subplan["plan"]
                    break
            else:

                if isinstance(subplans[-1], list):
                    plan = subplans[-1]
                    continue
                return None
            steps += 1
        if current == goal:
            return path
        return None


    problem = {
        'actions': actions,
        'goal': dich
    }
    expanded = [0]
    plan, exp = or_search(ban_dau, problem, [], expanded)
    if plan is None:
        return None, exp

    path = convert_plan_to_path(plan, ban_dau, dich)
    if path:
        return path, exp
    return None, exp

def heuristic(state, goal):
    return manhattan_distance(state, goal) + linear_conflict(state, goal)


def trust_based_search(ban_dau, dich):

    ACTIONS = {
        'UP': -3,
        'DOWN': 3,
        'LEFT': -1,
        'RIGHT': 1
    }

    def is_valid_move(state, action):
        blank = state.index(0)
        if action == 'UP' and blank < 3: return False
        if action == 'DOWN' and blank > 5: return False
        if action == 'LEFT' and blank % 3 == 0: return False
        if action == 'RIGHT' and blank % 3 == 2: return False
        return True

    def apply_action_to_state(state, action):
        if not is_valid_move(state, action):
            return state
        blank = state.index(0)
        delta = ACTIONS[action]
        new_blank = blank + delta
        lst = list(state)
        lst[blank], lst[new_blank] = lst[new_blank], lst[blank]
        return tuple(lst)

    def apply_action(belief, action):
        new_belief = set()
        for state in belief:
            new_state = apply_action_to_state(state, action)
            new_belief.add(new_state)
        return frozenset(new_belief)

    def calculate_belief_score(belief, belief_states, goal):
  
        heuristic_sum = 0
        for state in belief:
            heuristic_sum += manhattan_distance(state, goal) + linear_conflict(state, goal)
        avg_heuristic = heuristic_sum / len(belief) if belief else float('inf')

        belief_factor = 0
        for past_belief in belief_states:
            for state in belief:
                for past_state in past_belief:
                    if abs(manhattan_distance(past_state, goal) - manhattan_distance(state, goal)) < 2:
                        belief_factor += 1
                        break
        belief_factor = min(belief_factor / 5.0, 2.0)  
        return avg_heuristic - belief_factor

    def is_goal(belief):
        return len(belief) == 1 and dich in belief

    def reconstruct_path(initial_state, actions):

        path = [initial_state]
        current = initial_state
        for action in actions:
            current = apply_action_to_state(current, action)
            path.append(current)
        return path


    initial_belief = frozenset([ban_dau])
    belief_states = deque([initial_belief], maxlen=10)  
    pq = [(calculate_belief_score(initial_belief, belief_states, dich), 0, initial_belief, [])]
    visited = set([initial_belief])
    expanded = 0
    counter = 0

    while pq:
        score, _, current_belief, action_path = heapq.heappop(pq)
        expanded += 1

        if is_goal(current_belief):

            state_path = reconstruct_path(ban_dau, action_path)
            return state_path, expanded

        belief_states.append(current_belief)


        for action in ACTIONS:
            new_belief = apply_action(current_belief, action)
            if new_belief not in visited:
                visited.add(new_belief)
                counter += 1
                score = calculate_belief_score(new_belief, belief_states, dich)
                heapq.heappush(pq, (score, counter, new_belief, action_path + [action]))

        if len(belief_states) > 10:
            belief_states.popleft()

    return None, expanded


# Lop Button (giu nguyen)
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

# Lop ComboBox 
class ComboBox:
    def __init__(self, x, y, width, height, options, callback, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = 0
        self.is_open = False
        self.callback = callback
        self.color = color
        self.option_rects = []

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, self.rect, border_radius=10)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, (255, 255, 0), self.rect, 3, border_radius=10)
        
        text = FONT.render(self.options[self.selected_index], True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        WINDOW.blit(text, text_rect)

        if self.is_open:
            self.option_rects = []
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                self.option_rects.append(option_rect)
                pygame.draw.rect(WINDOW, self.color, option_rect, border_radius=10)
                option_text = FONT.render(option, True, BLACK)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                WINDOW.blit(option_text, option_text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
            elif self.is_open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        self.callback(self.options[self.selected_index])
                        break
                self.is_open = False

# Lop PuzzleGUI 
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
        self.speed_options = ["1x", "2x", "5x", "10x"]
        self.current_speed = "1x"
        self.current_algorithm = None
        self.last_algorithm = None  
        self.show_solving_message = False  




        self.buttons = [
            Button("DFS", 550, 50, 120, 50, lambda: self.solve(dfs, "DFS"), BUTTON_COLORS[0]),
            Button("BFS", 550, 110, 120, 50, lambda: self.solve(bfs, "BFS"), BUTTON_COLORS[1]),
            Button("UCS", 550, 170, 120, 50, lambda: self.solve(ucs, "UCS"), BUTTON_COLORS[2]),
            Button("IDDFS", 550, 230, 120, 50, lambda: self.solve(iddfs, "IDDFS"), BUTTON_COLORS[3]),

            Button("Greedy", 550, 350, 120, 50, lambda: self.solve(greedy_search, "Greedy"), BUTTON_COLORS[4]),
            Button("A*", 550, 410, 120, 50, lambda: self.solve(a_star, "A*"), BUTTON_COLORS[5]),
            Button("IDA*", 550, 470, 120, 50, lambda: self.solve(ida_star, "IDA*"), BUTTON_COLORS[6]),
           
            Button("Simple Hill", 750, 50, 200, 50, lambda: self.solve(simple_hill_climbing, "Simple Hill"), BUTTON_COLORS[7]),
            Button("Steepest Hill", 750, 110, 200, 50, lambda: self.solve(steepest_ascent_hill_climbing, "Steepest Hill"), (135, 206, 235)),
            Button("Stochastic Hill", 750, 170, 200, 50, lambda: self.solve(stochastic_hill_climbing, "Stochastic Hill"), (147, 112, 219)),
            Button("Simulated Annealing", 700, 230, 300, 50, lambda: self.solve(simulated_annealing, "Simulated Annealing"), (255, 140, 0)),
            Button("Beam Search", 750, 290, 200, 50, lambda: self.solve(lambda s, g: beam_search(s, g, self.beam_width), "Beam Search"), (100, 149, 237)),
            Button("Beam Width +", 750, 350, 200, 50, self.increase_beam_width, (100, 149, 237)),
            Button("Beam Width -", 750, 410, 200, 50, self.decrease_beam_width, (100, 149, 237)),
            Button("Genetic", 790, 530, 120, 50, lambda: self.solve(genetic_algorithm, "Genetic"), (100, 200, 100)),

            Button("AO*", 1050, 50, 200, 50, lambda: self.solve(ao_star, "AO*"), (150, 200, 150)),
            Button("Trust Search", 1050, 110, 200, 50, lambda: self.solve(trust_based_search, "Trust Search"), (255, 99, 71)),
            Button("Trust Partial", 1050, 170, 200, 50, self.run_partial, BUTTON_COLORS[0]),

            
            Button("Backtracking", 1050, 290, 200, 50, self.run_backtracking, (100, 200, 200)),
            Button("AC-3", 1050, 350, 200, 50, self.run_ac3, (100, 200, 200)),
            Button("Min-Conflicts", 1050, 410, 200, 50, self.run_min_conflicts, (150, 200, 150)),

            Button("Q-Learning", 1050, 530, 200, 50, self.run_q_learning, (120, 180, 220)),
            
            Button("Reset", 550, 700, 120, 50, self.reset, (192, 192, 192)),
            Button("Random", 700, 700, 120, 50, self.randomize, (255, 165, 0)),
            Button("Stop", 850, 700, 120, 50, self.stop_solving, (255, 0, 0)),
            Button("Continue", 1000, 700, 140, 50, self.continue_solving, (0, 255, 0)),
        ]

        self.combo_box = ComboBox(1350, 500, 100, 50, self.speed_options, self.set_speed, (135, 206, 250))


    def run_backtracking(self):
        try:
            subprocess.run(["python", r"D:\tri tue nhan tao\New folder\123\backtracking.py"], check=True)
        except FileNotFoundError:
            self.no_solution_message = "Không tìm thấy file backtracking.py!"
            self.message_timer = 180
        except subprocess.CalledProcessError:
            self.no_solution_message = "Lỗi khi chạy backtracking.py!"
            self.message_timer = 180

    def run_ac3(self):
        try:
            subprocess.run(["python", r"D:\tri tue nhan tao\New folder\123\ac_3.py"], check=True)
        except FileNotFoundError:
            self.no_solution_message = "Không tìm thấy file ac_3.py!"
            self.message_timer = 180
        except subprocess.CalledProcessError:
            self.no_solution_message = "Lỗi khi chạy ac_3.py!"
            self.message_timer = 180

    def run_min_conflicts(self):
        try:
            subprocess.run(["python", r"D:\tri tue nhan tao\New folder\123\min-conflict.py"], check=True)
        except FileNotFoundError:
            self.no_solution_message = "Không tìm thấy file min-conflict.py!"
            self.message_timer = 180
        except subprocess.CalledProcessError:
            self.no_solution_message = "Lỗi khi chạy min-conflict.py!"
            self.message_timer = 180

    def run_partial(self):
        try:
            subprocess.run(["python", r"D:\tri tue nhan tao\New folder\123\partial.py"], check=True)
        except FileNotFoundError:
            self.no_solution_message = "Không tìm thấy file partial.py!"
            self.message_timer = 180
        except subprocess.CalledProcessError:
            self.no_solution_message = "Lỗi khi chạy partial.py!"
            self.message_timer = 180

    def run_q_learning(self):
        try:
            subprocess.run(["python", r"D:\tri tue nhan tao\New folder\123\q-learning.py"], check=True)
        except FileNotFoundError:
            self.no_solution_message = "Không tìm thấy file q-learning.py!"
            self.message_timer = 180
        except subprocess.CalledProcessError:
            self.no_solution_message = "Lỗi khi chạy q-learning.py!"
            self.message_timer = 180

    def set_speed(self, speed):
        self.current_speed = speed
        speed_factor = float(speed[:-1])
        self.step_interval = 1000 / speed_factor

    def continue_solving(self):
        if self.solution and self.step < len(self.solution) - 1:
            self.is_solving = True
            self.no_solution_message = None
            self.message_timer = 0
            self.last_step_time = pygame.time.get_ticks()
            if self.last_algorithm:
                self.show_solving_message = True
                self.current_algorithm = self.last_algorithm

    def draw_board(self, state, x_offset, y_offset, title, is_input=False):
        title_text = FONT.render(title, True, BLACK)
        title_rect = title_text.get_rect(center=(x_offset + CELL_SIZE * BOARD_SIZE // 2, y_offset - 40))
        WINDOW.blit(title_text, title_rect)

        board_rect = pygame.Rect(x_offset - 10, y_offset - 10, CELL_SIZE * BOARD_SIZE + 20, CELL_SIZE * BOARD_SIZE + 20)
        pygame.draw.rect(WINDOW, (230, 240, 255), board_rect, border_radius=10)
        pygame.draw.rect(WINDOW, (100, 150, 200), board_rect, 3, border_radius=10)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                num = state[i * BOARD_SIZE + j]
                rect = pygame.Rect(x_offset + j * CELL_SIZE, y_offset + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if num == 0:
                    cell_color = (180, 200, 220)
                else:
                    cell_color = WHITE
                
                if is_input and self.selected_cell == (i, j):
                    cell_color = (144, 238, 144)
                pygame.draw.rect(WINDOW, cell_color, rect, border_radius=5)
                pygame.draw.rect(WINDOW, (50, 50, 50), rect, 1, border_radius=5)
                
                if num != 0:
                    text = FONT.render(str(num), True, (255, 69, 0))
                    text_rect = text.get_rect(center=rect.center)
                    WINDOW.blit(text, text_rect)
        
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
        
        speed_text = FONT.render("Speed", True, BLACK)
        WINDOW.blit(speed_text, (1355, 450))
        self.combo_box.draw()
    
        text_1 = FONT.render("Nhom 1", True, BLACK)
        WINDOW.blit(text_1, (560, 10))

        text_2 = FONT.render("Nhom 2", True, BLACK)
        WINDOW.blit(text_2, (560, 310))

        text_3 = FONT.render("Nhom 3", True, BLACK)
        WINDOW.blit(text_3, (800, 10))

        text_4 = FONT.render("Nhom 4", True, BLACK)
        WINDOW.blit(text_4, (1100, 10))

        text_5 = FONT.render("Nhom 5", True, BLACK)
        WINDOW.blit(text_5, (1100, 250))

        text_5 = FONT.render("Nhom 6", True, BLACK)
        WINDOW.blit(text_5, (1100, 480))

        if self.show_solving_message and self.current_algorithm:
            solving_text = f"Dang giai thuat toan {self.current_algorithm}"
            text = FONT.render(solving_text, True, BLUE)
            WINDOW.blit(text, (50, 650))
    
        if self.solution:
            panel_x, panel_y = 40, 390
            panel_width = 400
            panel_height = 140
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
            pygame.draw.rect(WINDOW, (230, 240, 255), panel_rect, border_radius=10)
            pygame.draw.rect(WINDOW, (100, 150, 200), panel_rect, 3, border_radius=10)
        
            steps_text = f"So buoc: {len(self.solution) - 1}"
            WINDOW.blit(FONT.render(steps_text, True, BLUE), (panel_x + 10, panel_y + 10))
            expanded_text = f"Trang thai mo rong: {self.expanded_states}"
            WINDOW.blit(FONT.render(expanded_text, True, BLUE), (panel_x + 10, panel_y + 40))
            time_text = f"Thoi gian: {self.execution_time:.3f}s"
            WINDOW.blit(FONT.render(time_text, True, BLUE), (panel_x + 10, panel_y + 70))
            path_text = f"Buoc {self.step}: {self.solution[self.step]}"
            WINDOW.blit(FONT_SMALL.render(path_text, True, BLACK), (panel_x + 10, panel_y + 100))
    
        if self.no_solution_message and self.message_timer > 0:
            panel2_x, panel2_y = 40, 540
            panel2_width = 400
            panel2_height = 50
            panel2_rect = pygame.Rect(panel2_x, panel2_y, panel2_width, panel2_height)
        
            pygame.draw.rect(WINDOW, (255, 220, 220), panel2_rect, border_radius=10)
            pygame.draw.rect(WINDOW, (200, 100, 100), panel2_rect, 3, border_radius=10)
        
            text = FONT.render(self.no_solution_message, True, RED)
            text_rect = text.get_rect(center=panel2_rect.center)
            WINDOW.blit(text, text_rect)
        
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.no_solution_message = None
    
        beam_width_text = f"Beam Width: {self.beam_width}"
        WINDOW.blit(FONT.render(beam_width_text, True, BLACK), (750, 480))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 50 <= x < 50 + CELL_SIZE * BOARD_SIZE and 100 <= y < 100 + CELL_SIZE * BOARD_SIZE:
                i = (y - 100) // CELL_SIZE
                j = (x - 50) // CELL_SIZE
                self.selected_cell = (i, j)

        elif event.type == pygame.KEYDOWN and self.selected_cell:
            i, j = self.selected_cell
            if pygame.K_0 <= event.key <= pygame.K_9:
                num = event.key - pygame.K_0
                idx = i * BOARD_SIZE + j
                if num == 0 or num not in self.input_state or self.input_state[idx] == num:
                    self.input_state[idx] = num
            elif event.key == pygame.K_BACKSPACE:
                self.input_state[i * BOARD_SIZE + j] = 0
            
            elif event.key == pygame.K_LEFT:
                self.selected_cell = (i, max(0, j - 1))
            elif event.key == pygame.K_RIGHT:
                self.selected_cell = (i, min(BOARD_SIZE - 1, j + 1))
            elif event.key == pygame.K_UP:
                self.selected_cell = (max(0, i - 1), j)
            elif event.key == pygame.K_DOWN:
                self.selected_cell = (min(BOARD_SIZE - 1, i + 1), j)

    def solve(self, solver, algorithm_name):
        if 0 in self.input_state and len(set(self.input_state)) == 9 and all(0 <= x <= 8 for x in self.input_state):
            start_state = tuple(self.input_state)
            if not is_solvable(start_state):
                self.no_solution_message = "Trang thai ban dau khong the giai duoc!"
                self.message_timer = 180
                return
        
            self.show_solving_message = True
            self.current_algorithm = algorithm_name
            self.last_algorithm = algorithm_name  
            self.is_solving = True
            
            self.draw()
            pygame.display.flip()
            pygame.event.pump()
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
        self.is_solving = False
        self.current_speed = "1x"
        self.step_interval = 1000
        self.combo_box.selected_index = 0
        self.current_algorithm = None
        self.last_algorithm = None
        self.show_solving_message = False

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
        self.is_solving = False
        self.current_algorithm = None
        self.last_algorithm = None
        self.show_solving_message = False

    def increase_beam_width(self):
        self.beam_width = min(10, self.beam_width + 1)

    def decrease_beam_width(self):
        self.beam_width = max(1, self.beam_width - 1)

    def stop_solving(self):
        self.is_solving = False
        self.no_solution_message = "Da dung giai!"
        self.message_timer = 180
        self.current_algorithm = None
        self.show_solving_message = False

    def update(self):
        if self.solution and self.step < len(self.solution) - 1 and self.is_solving:
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
            gui.combo_box.handle_event(event)

        gui.update()
        gui.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()