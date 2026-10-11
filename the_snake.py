"""A grid-based Snake game built with pygame."""

from random import choice, randint
from typing import TypeAlias

import pygame as pg

Position: TypeAlias = tuple[int, int]
Color: TypeAlias = tuple[int, int, int]

SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

UP: Position = (0, -1)
DOWN: Position = (0, 1)
LEFT: Position = (-1, 0)
RIGHT: Position = (1, 0)

BOARD_BACKGROUND_COLOR: Color = (0, 0, 0)
BORDER_COLOR: Color = (93, 216, 228)
APPLE_COLOR: Color = (255, 0, 0)
SNAKE_COLOR: Color = (0, 255, 0)
SPEED: int = 20

screen: pg.Surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock: pg.time.Clock = pg.time.Clock()


class GameObject:
    """Base class for objects placed on the game board."""

    def __init__(self, body_color: Color = BOARD_BACKGROUND_COLOR) -> None:
        """Create an object at the centre of the board."""
        self.position: Position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color: Color = body_color

    def draw(self) -> None:
        """Draw the game object on the screen."""


class Apple(GameObject):
    """A single-cell apple that appears at a random board position."""

    def __init__(
        self,
        occupied_positions: list[Position] | None = None,
        body_color: Color = APPLE_COLOR,
    ) -> None:
        """Create a red apple and place it on the board."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions: list[Position]) -> None:
        """Choose a random position aligned with the board grid."""
        while True:
            position: Position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied_positions:
                self.position = position
                return

    def draw(self) -> None:
        """Draw the apple as a coloured grid cell."""
        rect: pg.Rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """A snake that moves, grows and resets after self-collision."""

    def __init__(self, body_color: Color = SNAKE_COLOR) -> None:
        """Create a one-segment snake facing right."""
        super().__init__(body_color=body_color)
        self.length: int = 1
        self.positions: list[Position] = [self.position]
        self.direction: Position = RIGHT
        self.next_direction: Position | None = None
        self.last: Position | None = None

    def get_head_position(self) -> Position:
        """Return the coordinates of the snake's head."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Apply the direction selected during keyboard handling."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Move one cell in the current direction, wrapping at board edges."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head: Position = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        self.last = (
            self.positions.pop() if len(self.positions) > self.length else None
        )

        self.position = self.get_head_position()

    def reset(self) -> None:
        """Restore the snake to its initial one-segment state."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None

    def draw(self) -> None:
        """Draw all snake segments and clear the cell it left."""
        for position in self.positions:
            rect: pg.Rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        if self.last:
            last_rect: pg.Rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object: Snake) -> None:
    """Handle quit events and store a valid next direction for the snake."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_UP and game_object.direction != DOWN:
            game_object.next_direction = UP
        elif event.key == pg.K_DOWN and game_object.direction != UP:
            game_object.next_direction = DOWN
        elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
            game_object.next_direction = LEFT
        elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
            game_object.next_direction = RIGHT


def main() -> None:
    """Run the main game loop."""
    pg.init()
    snake: Snake = Snake()
    apple: Apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
