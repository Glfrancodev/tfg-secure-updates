"""Juego de prueba: Snake. Se juega con las flechas o WASD.

No usa la red ni lee archivos fuera de su propia carpeta.
"""
import random
from pathlib import Path

import pygame

GAME_DIR = Path(__file__).resolve().parent
VERSION = (GAME_DIR / "VERSION").read_text(encoding="utf-8").strip()
OLD_VERSION_NOTE = "(versión antigua — fallo conocido corregido en 1.1.0)"

WIDTH, HEIGHT = 640, 480
HUD_HEIGHT = 80
CELL = 20
COLS = WIDTH // CELL
ROWS = (HEIGHT - HUD_HEIGHT) // CELL
STEP_MS = 110
FPS = 60

BACKGROUND = (24, 26, 33)
BOARD = (32, 35, 44)
SNAKE_HEAD = (120, 200, 255)
SNAKE_BODY = (80, 170, 255)
FOOD = (240, 90, 90)
TEXT_COLOR = (235, 235, 235)
NOTE_COLOR = (255, 190, 80)

DIRECTIONS = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}


class Snake:
    """Estado del juego en celdas de la cuadrícula; no sabe nada de la pantalla."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(COLS // 2 - i, ROWS // 2) for i in range(3)]  # la cabeza va primero
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.over = False
        self.food = self.place_food()

    def place_food(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in self.body]
        if not free:
            self.over = True
            return None
        return random.choice(free)

    def turn(self, direction):
        # No se permite girar 180°: la serpiente chocaría consigo misma.
        if direction != (-self.direction[0], -self.direction[1]):
            self.next_direction = direction

    def step(self):
        if self.over:
            return
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        head = (head_x + self.direction[0], head_y + self.direction[1])
        grows = head == self.food
        # Si no crece, la cola se mueve en este mismo paso y deja libre su celda.
        obstacles = self.body if grows else self.body[:-1]
        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in obstacles:
            self.over = True
            return
        self.body.insert(0, head)
        if grows:
            self.score += 1
            self.food = self.place_food()
        else:
            self.body.pop()


def cell_rect(cell):
    x, y = cell
    return pygame.Rect(x * CELL + 1, HUD_HEIGHT + y * CELL + 1, CELL - 2, CELL - 2)


def draw(screen, fonts, game):
    title_font, note_font = fonts
    screen.fill(BACKGROUND)
    screen.blit(title_font.render(f"Mi Juego de Prueba — v{VERSION}", True, TEXT_COLOR), (20, 20))
    screen.blit(note_font.render(OLD_VERSION_NOTE, True, NOTE_COLOR), (20, 54))
    score = note_font.render(f"Puntaje: {game.score}", True, TEXT_COLOR)
    screen.blit(score, (WIDTH - score.get_width() - 20, 26))

    pygame.draw.rect(screen, BOARD, (0, HUD_HEIGHT, WIDTH, HEIGHT - HUD_HEIGHT))
    if game.food:
        pygame.draw.rect(screen, FOOD, cell_rect(game.food), border_radius=6)
    for i, cell in enumerate(game.body):
        pygame.draw.rect(screen, SNAKE_HEAD if i == 0 else SNAKE_BODY, cell_rect(cell), border_radius=4)

    if game.over:
        lines = [f"Fin del juego — puntaje {game.score}", "R o Espacio para jugar de nuevo"]
        for i, text in enumerate(lines):
            surface = (title_font if i == 0 else note_font).render(text, True, TEXT_COLOR)
            y = HUD_HEIGHT + (HEIGHT - HUD_HEIGHT) // 2 - 30 + i * 40
            screen.blit(surface, ((WIDTH - surface.get_width()) // 2, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mi Juego de Prueba")
    clock = pygame.time.Clock()
    fonts = (pygame.font.Font(None, 36), pygame.font.Font(None, 24))
    game = Snake()
    elapsed = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in DIRECTIONS:
                    game.turn(DIRECTIONS[event.key])
                elif event.key in (pygame.K_r, pygame.K_SPACE) and game.over:
                    game.reset()
                    elapsed = 0

        elapsed += clock.tick(FPS)
        while elapsed >= STEP_MS:
            game.step()
            elapsed -= STEP_MS

        draw(screen, fonts, game)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
