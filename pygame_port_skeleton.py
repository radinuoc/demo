"""Skeleton to start porting a ZX Spectrum game to pygame.

Replace placeholder logic with behavior extracted from .tap/.z80 analysis.
"""

import pygame

SCREEN_W, SCREEN_H = 256, 192
SCALE = 3
FPS = 50


class Game:
    def __init__(self) -> None:
        self.player_x = SCREEN_W // 2
        self.player_y = SCREEN_H - 24
        self.speed = 2

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        if keys[pygame.K_LEFT]:
            self.player_x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.player_x += self.speed
        if keys[pygame.K_UP]:
            self.player_y -= self.speed
        if keys[pygame.K_DOWN]:
            self.player_y += self.speed

        self.player_x = max(0, min(SCREEN_W - 8, self.player_x))
        self.player_y = max(0, min(SCREEN_H - 8, self.player_y))

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill((0, 0, 0))
        pygame.draw.rect(surf, (0, 255, 255), (self.player_x, self.player_y, 8, 8))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W * SCALE, SCREEN_H * SCALE))
    buffer = pygame.Surface((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        game.update(keys)
        game.draw(buffer)

        pygame.transform.scale(buffer, screen.get_size(), screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
