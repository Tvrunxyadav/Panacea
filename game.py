import sys

import pygame

from scripts.utils import load_image, load_images, Animation, recolor
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.particle import Particle

WHITE = (255, 255, 255)
RETRO = (60, 82, 56)

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

def recolor_all(images):
    return [recolor(img, WHITE, RETRO, 0.1) for img in images]

Tilemap.physics_rects_around = wide_physics_rects

pygame.init()

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Panacea")
        self.screen = pygame.display.set_mode((704, 640))

        self.display = pygame.Surface((352, 320))

        self.clock = pygame.time.Clock()

        self.image_pos = [160, 260]
        self.movement = [False, False]

        self.assets = {
            'decor': recolor_all(load_images('tiles/decor')),
            'grass': recolor_all(load_images('tiles/grass')),
            'large_decor': load_images('tiles/large_decor'),
            'stone': recolor_all(load_images('tiles/stone')),
            'player': load_image('entities/player.png'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particles/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False)
        }

        idle_frame = self.assets['player/idle'].images[0]
        self.player_bbox = idle_frame.get_bounding_rect()
        self.player = Player(self, (50, 50), (14, 14))

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')

        self.enemies = []
        for spawner in self.tilemap.extract([('spawner', 0), ('spawner', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (14, 14)))

        self.particles = []

        self.scroll = [0, 0]

    def run(self):
        while True:
            self.display.fill((10, 16, 13))

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]) * 1.4, 0))
            self.player.render(self.display, offset=render_scroll)
            hitbox = self.player.rect()
            debug_rect = pygame.Rect(hitbox.x - render_scroll[0], hitbox.y - render_scroll[1], hitbox.width, hitbox.height)
            

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if kill:
                    self.particles.remove(particle)

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
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()