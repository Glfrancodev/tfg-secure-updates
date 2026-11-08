"""Juego de prueba: un cuadrado que se mueve con las flechas o WASD.

No usa la red ni lee archivos fuera de su propia carpeta.
"""
from pathlib import Path

import pygame

GAME_DIR = Path(__file__).resolve().parent
VERSION = (GAME_DIR / "VERSION").read_text(encoding="utf-8").strip()
OLD_VERSION_NOTE = "(versión antigua — fallo conocido corregido en 1.1.0)"

WIDTH, HEIGHT = 640, 480
SQUARE_SIZE = 40
SPEED = 5
FPS = 60

BACKGROUND = (24, 26, 33)
SQUARE_COLOR = (80, 170, 255)
TEXT_COLOR = (235, 235, 235)
NOTE_COLOR = (255, 190, 80)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mi Juego de Prueba")
    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 36)
    note_font = pygame.font.Font(None, 24)

    title = title_font.render(f"Mi Juego de Prueba — v{VERSION}", True, TEXT_COLOR)
    note = note_font.render(OLD_VERSION_NOTE, True, NOTE_COLOR)
    square = pygame.Rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)
    square.center = (WIDTH // 2, HEIGHT // 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        square.move_ip(dx * SPEED, dy * SPEED)
        square.clamp_ip(screen.get_rect())

        screen.fill(BACKGROUND)
        screen.blit(title, (20, 20))
        screen.blit(note, (20, 60))
        pygame.draw.rect(screen, SQUARE_COLOR, square)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
