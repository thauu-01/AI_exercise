import pygame
import sys
from collections import deque
import time
import heapq
import random
import math
import numpy as np

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

    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    max_sideways = 100  
    sideways_count = 0

    while current_state != dich:
        expanded += 1
        current_h = manhattan_distance(current_state, dich) + linear_conflict(current_state, dich)
        better_found = False
        max_attempts = 10 

        neighbors = get_next_states(current_state)
        valid_neighbors = [n for n in neighbors if n not in visited]

        if not valid_neighbors:
            return None, expanded  

        for _ in range(min(max_attempts, len(valid_neighbors))):
            neighbor = random.choice(valid_neighbors)
            h = manhattan_distance(neighbor, dich) + linear_conflict(neighbor, dich)
            if h < current_h or (h == current_h and sideways_count < max_sideways):
                current_state = neighbor
                duong_di.append(current_state)
                visited.add(current_state)
                better_found = True
                if h == current_h:
                    sideways_count += 1
                else:
                    sideways_count = 0
                break
            valid_neighbors.remove(neighbor)  

        if not better_found:
            return None, expanded 

    return duong_di, expanded

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

def stochastic_hill_climbing(ban_dau, dich):

    if ban_dau == dich:
        return [ban_dau], 0

    current_state = ban_dau
    duong_di = [current_state]
    visited = {current_state}
    expanded = 0
    max_sideways = 100  
    sideways_count = 0
    temperature = 10.0 
    cooling_rate = 0.99 

    while current_state != dich:
        expanded += 1
        neighbors = get_next_states(current_state)
        valid_neighbors = [n for n in neighbors if n not in visited]
        
        if not valid_neighbors:
            return None, expanded 

        current_h = manhattan_distance(current_state, dich) + linear_conflict(current_state, dich)
        weights = []
        next_states = []

        for neighbor in valid_neighbors:
            h = manhattan_distance(neighbor, dich) + linear_conflict(neighbor, dich)
            delta_h = current_h - h  
            if delta_h > 0 or (delta_h == 0 and sideways_count < max_sideways) or random.random() < exp(delta_h / temperature):
                weight = exp(delta_h / temperature) if temperature > 0 else (1 if delta_h >= 0 else 0)
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
        visited.add(current_state)
        new_h = manhattan_distance(current_state, dich) + linear_conflict(current_state, dich)
        if new_h == current_h:
            sideways_count += 1
        else:
            sideways_count = 0

        temperature *= cooling_rate 

    return duong_di, expanded

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

def genetic_algorithm(ban_dau, dich, population_size=50, max_generations=200, crossover_rate=0.7, mutation_rate=0.05):

    def generate_initial_population(start_state, size):
        population = []
        visited = set()
        
        population.append(list(start_state))
        visited.add(tuple(start_state))
        
        while len(population) < size:
            state = list(range(9))
            random.shuffle(state)
            if is_solvable(tuple(state)):
                if tuple(state) not in visited:
                    population.append(state)
                    visited.add(tuple(state))
            else:
                state = repair_solvability(state)
                if tuple(state) not in visited:
                    population.append(state)
                    visited.add(tuple(state))
        
        return population[:size]

    def fitness(state, goal):

        h = manhattan_distance(state, goal) + linear_conflict(state, goal)

    def tournament_selection(population, fitnesses, tournament_size=5):
        selected = random.sample(list(zip(population, fitnesses)), tournament_size)
        return max(selected, key=lambda x: x[1])[0]

    def crossover(parent1, parent2):
        size = len(parent1)
        crossover_point = random.randint(1, size - 1)
        child = [-1] * size
        

        child[:crossover_point] = parent1[:crossover_point]
        
        pos = crossover_point
        for val in parent2:
            if val not in child:
                child[pos] = val
                pos += 1
        
        if not is_solvable(tuple(child)):
            child = repair_solvability(child)
        
        return child

    def mutation(state):
        state = state[:]
        i, j = random.sample(range(len(state)), 2)
        state[i], state[j] = state[j], state[i]
        
        if not is_solvable(tuple(state)):
            state = repair_solvability(state)
        
        return state

    if ban_dau == dich:
        return [ban_dau], 0

    population = generate_initial_population(ban_dau, population_size)
    expanded = 0
    elite_count = max(1, population_size // 10) 

    for generation in range(max_generations):

        fitnesses = [fitness(state, dich) for state in population]
        expanded += len(population)

        for state in population:
            if tuple(state) == dich:
                return [state], expanded

        elite_indices = sorted(range(len(fitnesses)), key=lambda x: fitnesses[x], reverse=True)[:elite_count]
        new_population = [population[i][:] for i in elite_indices]

        while len(new_population) < population_size:

            parent1 = tournament_selection(population, fitnesses)
            parent2 = tournament_selection(population, fitnesses)
            

            if random.random() < crossover_rate:
                child = crossover(parent1, parent2)
            else:
                child = parent1[:]  
            

            if random.random() < mutation_rate:
                child = mutation(child)
            
            new_population.append(child)
        
        population = new_population[:population_size]
    

    return None, expanded

def ao_star(ban_dau, dich):

    if ban_dau == dich:
        return [], 0

    def get_action_outcomes(current_state, action):
 
        next_states = []

        success_state = apply_action(current_state, action)
        if success_state:
            next_states.append(success_state)
 
        next_states.append(current_state)
        return next_states

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

    open_list = [(heuristic(ban_dau, dich), ban_dau, [], 0, [])]
    heapq.heapify(open_list)
    visited = set() 
    expanded = 0
    best_plan = {ban_dau: []}
    best_f_cost = {ban_dau: heuristic(ban_dau, dich)}
    labels = {}  

    actions = ["MoveUp", "MoveDown", "MoveLeft", "MoveRight"]

    while open_list:
        f_cost, current_state, plan, g_cost, path = heapq.heappop(open_list)
        expanded += 1

        if current_state == dich:
            return plan, expanded


        if current_state in path:
            continue

        visited.add(current_state)

        for action in actions:

            outcomes = get_action_outcomes(current_state, action)
            subplans = []
            all_failed = True

            for next_state in outcomes:
                if next_state in visited and next_state != current_state:
                    continue

                new_g_cost = g_cost + 1
                h_cost = heuristic(next_state, dich)
                new_f_cost = new_g_cost + h_cost

                if next_state in path:
                    label = f"L{len(labels) + 1}"
                    labels[label] = next_state
                    subplan = [label]
                else:

                    subplan = best_plan.get(next_state, [])
                    if not subplan and next_state != dich:
                        continue

                subplans.append({"state": next_state, "plan": subplan})
                all_failed = False

            if not all_failed:

                new_plan = [action, subplans]
                if current_state not in best_plan or new_f_cost < best_f_cost[current_state]:
                    best_plan[current_state] = new_plan
                    best_f_cost[current_state] = new_f_cost
                    heapq.heappush(open_list, (new_f_cost, current_state, new_plan, new_g_cost, path + [current_state]))

    return None, expanded

def heuristic(state, goal):
    return manhattan_distance(state, goal) + linear_conflict(state, goal)

def trust_based_search(ban_dau, dich):

    def calculate_belief_score(state, belief_states, goal):

        heuristic = manhattan_distance(state, goal) + linear_conflict(state, goal)

        belief_factor = sum(1 for bs in belief_states 
                           if abs(manhattan_distance(bs, goal) - manhattan_distance(state, goal)) < 2)
        belief_factor = min(belief_factor / 5.0, 2.0)  
        return heuristic - belief_factor

    belief_states = deque([ban_dau], maxlen=10) 
    pq = [(calculate_belief_score(ban_dau, belief_states, dich), 0, ban_dau, [ban_dau])]
    visited = set([ban_dau])
    expanded = 0
    counter = 0

    while pq:
        score, _, current_state, duong_di = heapq.heappop(pq)
        expanded += 1

        if current_state == dich:
            return duong_di, expanded


        belief_states.append(current_state)


        next_states = get_next_states(current_state)
        for next_state in next_states:
            if next_state not in visited:
                visited.add(next_state)
                counter += 1

                score = calculate_belief_score(next_state, belief_states, dich)
                heapq.heappush(pq, (score, counter, next_state, duong_di + [next_state]))

        if len(belief_states) > 10:
            belief_states.popleft()

    return None, expanded

def trust_based_search_partial(ban_dau, dich):

    known_goal_row = (1, 2, 3)  
    full_goal = dich

    def calculate_belief_score(state, belief_states, visited_states):

        state_row_1 = state[:3]
        row_match_score = sum(1 for a, b in zip(state_row_1, known_goal_row) if a == b)
        row_trust = row_match_score * 5 

        heuristic = manhattan_distance(state, full_goal) + linear_conflict(state, full_goal)

        trust_factor = 0
        if visited_states:
            good_states = [s for s in visited_states if s[:3] == known_goal_row]
            if good_states:
                avg_distance = sum(manhattan_distance(state, s) for s in good_states) / len(good_states)
                trust_factor = max(0, 5 - avg_distance / 3)
        return -(heuristic - row_trust - trust_factor)

    def update_belief_state(belief_states, observation, action, current_state):
 
        new_belief = []
        predicted_states = get_next_states(current_state) if action else [current_state]
        for state in predicted_states:

            if state[:3] == observation:
                new_belief.append(state)
        return new_belief if new_belief else belief_states

    belief_states = [ban_dau]
    pq = [(calculate_belief_score(ban_dau, belief_states, []), 0, ban_dau, [ban_dau], belief_states)]
    visited = set([ban_dau])
    expanded = 0
    counter = 0
    recent_visited = deque(maxlen=10) 

    while pq:
        score, _, current_state, duong_di, current_belief = heapq.heappop(pq)
        expanded += 1

        if current_state[:3] == known_goal_row:
            if current_state == full_goal:
                return duong_di, expanded

            path, extra_expanded = a_star(current_state, full_goal)
            if path:
                return duong_di + path[1:], expanded + extra_expanded

        recent_visited.append(current_state)


        next_states = get_next_states(current_state)
        for next_state in next_states:
            if next_state not in visited:
                visited.add(next_state)
                counter += 1

                observation = next_state[:3]

                new_belief = update_belief_state(current_belief, observation, next_state, current_state)
                score = calculate_belief_score(next_state, new_belief, recent_visited)
                heapq.heappush(pq, (score, counter, next_state, duong_di + [next_state], new_belief))

    return None, expanded


from collections import deque

def backtracking_csp(ban_dau, dich):


    variables = list(range(9))  
    domain = {var: list(range(9)) for var in variables}  
    assignment = {} 
    goal = {i: dich[i] for i in range(9)}  
    expanded = [0]  

    def is_consistent(var, value, assignment, current_state):

        for assigned_var, assigned_value in assignment.items():
            if assigned_var != var and assigned_value == value:
                return False

        temp_state = list(current_state)
        temp_state[var] = value

        return is_reachable_from_initial(temp_state, ban_dau)

    def is_reachable_from_initial(state, initial):
        state_tuple = tuple(state)
        queue = deque([(initial, [])])
        visited = {tuple(initial)}
        max_steps = 10 
        steps = 0
        while queue and steps < max_steps:
            current, _ = queue.popleft()
            if tuple(current) == state_tuple:
                return True
            for next_state in get_next_states(tuple(current)):
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((list(next_state), []))
            steps += 1
        return False

    def select_unassigned_variable(assignment, variables):
        unassigned = [var for var in variables if var not in assignment]
        if not unassigned:
            return None

        for var in unassigned:
            if ban_dau[var] == 0:
                return var

        return min(unassigned, key=lambda var: len(domain[var]))

    def order_domain_values(var, assignment):

        values = domain[var]
        if not values:
            return []

        goal_value = goal[var]
        if goal_value in values:
            values = [goal_value] + [v for v in values if v != goal_value]
        return values

    def inference(var, value, assignment):

        inferences = {}
        for other_var in variables:
            if other_var != var and other_var not in assignment:
 
                if value in domain[other_var]:
                    inferences[other_var] = domain[other_var].copy()
                    domain[other_var].remove(value)
                    if not domain[other_var]:
                        return None  
        return inferences

    def backtrack(assignment, current_state):

        expanded[0] += 1

        if len(assignment) == len(variables):
            state = tuple(assignment.get(i, current_state[i]) for i in range(9))
            if state == dich:

                path = [ban_dau]
                current = list(ban_dau)
                while current != list(state):
                    for next_state in get_next_states(tuple(current)):
                        if all(next_state[i] == state[i] for i in range(9) if i in assignment):
                            path.append(next_state)
                            current = list(next_state)
                            break
                return path, expanded[0]
            return None, expanded[0]


        var = select_unassigned_variable(assignment, variables)
        if var is None:
            return None, expanded[0]

        for value in order_domain_values(var, assignment):
            if is_consistent(var, value, assignment, current_state):
                assignment[var] = value
                inferences = inference(var, value, assignment)
                if inferences is not None:

                    for inf_var, inf_values in inferences.items():
                        domain[inf_var] = inf_values
 
                    new_state = list(current_state)
                    new_state[var] = value
                    result, exp = backtrack(assignment, new_state)
                    if result is not None:
                        return result, exp
   
                    for inf_var in inferences:
                        domain[inf_var] = inferences[inf_var][:]
       
                del assignment[var]

        return None, expanded[0]
    result, exp = backtrack({}, ban_dau)
    return result, exp

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
            Button("Greedy", 550, 290, 120, 50, lambda: self.solve(greedy_search, "Greedy"), BUTTON_COLORS[4]),
            Button("A*", 550, 350, 120, 50, lambda: self.solve(a_star, "A*"), BUTTON_COLORS[5]),
            Button("IDA*", 550, 410, 120, 50, lambda: self.solve(ida_star, "IDA*"), BUTTON_COLORS[6]),
            Button("Genetic", 550, 470, 120, 50, lambda: self.solve(genetic_algorithm, "Genetic"), (100, 200, 100)),
            Button("Simple Hill", 750, 50, 200, 50, lambda: self.solve(simple_hill_climbing, "Simple Hill"), BUTTON_COLORS[7]),
            Button("Steepest Hill", 750, 110, 200, 50, lambda: self.solve(steepest_ascent_hill_climbing, "Steepest Hill"), (135, 206, 235)),
            Button("Stochastic Hill", 750, 170, 200, 50, lambda: self.solve(stochastic_hill_climbing, "Stochastic Hill"), (147, 112, 219)),
            Button("Simulated Annealing", 700, 230, 300, 50, lambda: self.solve(simulated_annealing, "Simulated Annealing"), (255, 140, 0)),
            Button("AO*", 790, 290, 120, 50, lambda: self.solve(ao_star, "AO*"), (150, 200, 150)),
            Button("Trust Search", 750, 350, 200, 50, lambda: self.solve(trust_based_search, "Trust Search"), (255, 99, 71)),
            Button("Trust Partial", 750, 410, 200, 50, lambda: self.solve(trust_based_search_partial, "Trust Partial"), BUTTON_COLORS[0]),
            Button("Beam Search", 1100, 50, 200, 50, lambda: self.solve(lambda s, g: beam_search(s, g, self.beam_width), "Beam Search"), (100, 149, 237)),
            Button("Beam Width +", 1100, 110, 200, 50, self.increase_beam_width, (100, 149, 237)),
            Button("Beam Width -", 1100, 170, 200, 50, self.decrease_beam_width, (100, 149, 237)),
            Button("Backtracking", 1100, 290, 200, 50, lambda: self.solve(backtracking_csp, "Backtracking"), (100, 200, 200)),

            Button("Reset", 550, 590, 120, 50, self.reset, (192, 192, 192)),
            Button("Random", 790, 590, 120, 50, self.randomize, (255, 165, 0)),
            Button("Stop", 1050, 590, 120, 50, self.stop_solving, (255, 0, 0)),
            Button("Continue", 1290, 590, 120, 50, self.continue_solving, (0, 255, 0)),
        ]

        self.combo_box = ComboBox(1100, 485, 200, 50, self.speed_options, self.set_speed, (135, 206, 250))

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
        WINDOW.blit(speed_text, (1155, 450))
        self.combo_box.draw()
    
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
        WINDOW.blit(FONT.render(beam_width_text, True, BLACK), (1100, 240))

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
