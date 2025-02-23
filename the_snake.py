from random import randint
import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (128, 128, 128)  # Цвет камня

# Скорость движения змейки:
SPEED = 10

def random_position(excluded_positions):
    while True:
        position = (randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1))
        if position not in excluded_positions:
            return position

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.body_color = SNAKE_COLOR
        self.apple_count = 0  # Счётчик съеденных яблок

    def update(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

        head_x, head_y = self.positions[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Проверка на выход за границы и телепортация
        if new_head[0] < 0:
            new_head = (GRID_WIDTH - 1, new_head[1])
        elif new_head[0] >= GRID_WIDTH:
            new_head = (0, new_head[1])
        if new_head[1] < 0:
            new_head = (new_head[0], GRID_HEIGHT - 1)
        elif new_head[1] >= GRID_HEIGHT:
            new_head = (new_head[0], 0)

        # Проверка на столкновение с телом
        if len(self.positions) >= 5 and new_head in self.positions[1:]:
            return True  # Столкновение с самим собой

        self.last = self.positions[-1]
        self.positions = [new_head] + self.positions[:-1]
        return False  # Нет столкновения

    def grow(self):
        self.apple_count += 1
        self.positions.append(self.last)

    def draw(self, screen):
        for position in self.positions[:-1]:
            rect = pygame.Rect(position[0] * GRID_SIZE, position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы
        head_rect = pygame.Rect(self.positions[0][0] * GRID_SIZE, self.positions[0][1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last[0] * GRID_SIZE, self.last[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

class Apple:
    def __init__(self):
        self.position = None
        self.body_color = APPLE_COLOR

    def random_position(self, excluded_positions):
        self.position = random_position(excluded_positions)

    def draw(self, screen):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

class Stone:
    def __init__(self, position):
        self.position = position
        self.body_color = STONE_COLOR

    @staticmethod
    def random_position(excluded_positions):
        return random_position(excluded_positions)

    def draw(self, screen):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

def handle_keys(game_object):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT

def main():
    # Инициализация PyGame:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption('Змейка')
    clock = pygame.time.Clock()

    # Создаем экземпляры классов
    snake = Snake()
    apple = Apple()
    apple.random_position(snake.positions)  # Генерируем позицию яблока
    stones = [Stone(Stone.random_position(snake.positions + [apple.position])) for _ in range(5)]  # Создаем 5 камней

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        if snake.update():  # Проверяем на столкновение с самим собой
            print("Игра окончена! Змея столкнулась сама с собой.")
            break

        # Проверка на столкновение со яблоком
        if snake.positions[0] == apple.position:
            snake.grow()
            apple.random_position(snake.positions + [stone.position for stone in stones])  # Генерируем новое яблоко

            # Добавляем проверку на появление камней
            if snake.apple_count % 5 == 0:  # Каждые 5 съеденных яблок
                new_stone_position = Stone.random_position(snake.positions + [apple.position] + [stone.position for stone in stones])
                stones.append(Stone(new_stone_position))

        # Проверка на столкновение с камнями
        if snake.positions[0] in [stone.position for stone in stones]:
            print("Игра окончена! Змея столкнулась с камнем.")
            break

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen)
        for stone in stones:
            stone.draw(screen)  # Отрисовка камней
        snake.draw(screen)
        pygame.display.flip()

    pygame.quit()  # Завершение игры

if __name__ == '__main__':
    main()
