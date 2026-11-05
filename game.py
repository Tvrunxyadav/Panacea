import sys

import pygame

from scripts.utils import load_image, load_images
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap

def wide_physics_rects(self, pos):
    ts = self.tile_size
    bx, by = int(pos[0] // ts), int(pos[1] // ts)
    rects = []
    for dx in range(-2, 4):
        for dy in range(-2, 4):
            tile = self.tilemap.get(f'{bx + dx};{by + dy}')
            if tile and tile['type'] in ('grass', 'stone'):
                rects.append(pygame.Rect(tile['pos'][0] * ts, tile['pos'][1] * ts, ts, ts))
    return rects

Tilemap.physics_rects_around = wide_physics_rects

pygame.init()

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Panacea")
        self.screen = pygame.display.set_mode((640, 480))

        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.image_pos = [160, 260]
        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png')
        }

        self.player_bbox = self.assets['player'].get_bounding_rect()
        self.player = PhysicsEntity(self, 'player', (50, 50), (self.player_bbox.width - 8, self.player_bbox.height))

        self.tilemap = Tilemap(self, tile_size=16)

        self.scroll = [0, 0]

    def run(self):
        while True:
            self.display.fill((221, 198, 161))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            hitbox = self.player.rect()
            self.display.blit(self.assets['player'],(hitbox.centerx - self.player_bbox.centerx - render_scroll[0], hitbox.bottom - self.player_bbox.bottom - render_scroll[1]))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()