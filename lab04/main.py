import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка")

GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

font = pygame.font.Font(None, 36)

def draw_text(text, pos, color=WHITE):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)

def main_menu():
    running = True
    difficulty = "medium"
    while running:
        screen.fill(BLACK)
        draw_text("Змейка", (WIDTH // 2 - 50, HEIGHT // 4))
        draw_text("1. Начать игру", (WIDTH // 2 - 80, HEIGHT // 2 - 40))
        draw_text("2. Выбор сложности", (WIDTH // 2 - 80, HEIGHT // 2))
        draw_text(f"   Текущая: {difficulty}", (WIDTH // 2 - 80, HEIGHT // 2 + 30), GRAY)
        draw_text("3. Выход", (WIDTH // 2 - 80, HEIGHT // 2 + 60))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return difficulty
                elif event.key == pygame.K_2:
                    difficulty = change_difficulty(difficulty)
                elif event.key == pygame.K_3:
                    pygame.quit()
                    exit()

def change_difficulty(current):
    difficulties = ["easy", "medium", "hard"]
    index = difficulties.index(current)
    return difficulties[(index + 1) % len(difficulties)]

def get_speed(difficulty):
    return {"easy": 5, "medium": 10, "hard": 15}[difficulty]

def generate_food(snake):
    while True:
        food = (random.randrange(0, WIDTH, CELL_SIZE), random.randrange(0, HEIGHT, CELL_SIZE))
        if food not in snake:
            return food

def game_loop(difficulty):
    snake = [(100, 100), (90, 100), (80, 100)]
    direction = (CELL_SIZE, 0)
    food = generate_food(snake)
    score = 0
    speed = get_speed(difficulty)
    
    running = True
    clock = pygame.time.Clock()
    while running:
        screen.fill(BLACK)
        draw_grid()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                    direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                    direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                    direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                    direction = (CELL_SIZE, 0)

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        if new_head in snake or new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
            running = False 
        else:
            snake.insert(0, new_head)
            if new_head == food:
                score += 1
                food = generate_food(snake)
            else:
                snake.pop()

        for segment in snake:
            pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, RED, (*food, CELL_SIZE, CELL_SIZE))

        text = font.render(f"Очки: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(speed)

while True:
    difficulty = main_menu()
    game_loop(difficulty)
