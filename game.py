import os
import sys

import pygame
import random
import math

from scripts.crt import CRT
from scripts.utils import load_image, load_images, Animation, recolor
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.particle import Particle
from scripts.spark import Spark

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
        self.display = pygame.Surface((352, 320)).convert((255, 65280, 16711680, 0))
        pygame.display.set_mode((704, 640), pygame.DOUBLEBUF | pygame.OPENGL)
        self.crt = CRT(self.display)

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
            'particles/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'projectile': load_image('projectile.png')
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'wall_hit': pygame.mixer.Sound('data/sfx/hit.wav'),
        }

        self.sfx['jump'].set_volume(0.1)
        self.sfx['dash'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['wall_hit'].set_volume(0.1)

        idle_frame = self.assets['player/idle'].images[0]
        self.player_bbox = idle_frame.get_bounding_rect()
        self.player = Player(self, (50, 50), (14, 14))

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 0
        self.screenshake = 0
        self.play_time = 0
        self.hud_font = pygame.font.SysFont('couriernew,courier,consolas,monospace', 12, bold=True)
        self.load_level(self.level)

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.enemies = []
        for spawner in self.tilemap.extract([('spawner', 0), ('spawner', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (14, 14)))

        
        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def fmt_time(self, ms):
        return '%02d:%02d.%02d' % (ms // 60000, (ms // 1000) % 60, (ms % 1000) // 10)

    def run(self):
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.07)
        pygame.mixer.music.play(-1)

        while True:
            self.display.fill((10, 16, 13))

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    if self.level >= len(os.listdir('data/maps')) - 1:
                        self.level = 0
                        self.play_time = 0
                    else:
                        self.level += 1
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.level = 0
                    self.play_time = 0
                    self.load_level(self.level)

            shake = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            render_scroll = (int(self.scroll[0] + shake[0]), int(self.scroll[1] + shake[1]))

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            self.tilemap.render(self.display, offset=render_scroll)

            if not self.dead:
                self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]) * 1.4, 0))
                self.player.render(self.display, offset=render_scroll)
                hitbox = self.player.rect()
                debug_rect = pygame.Rect(hitbox.x - render_scroll[0], hitbox.y - render_scroll[1], hitbox.width, hitbox.height)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.sfx['wall_hit'].play()
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] < 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

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
                    if event.key == pygame.K_r:
                        self.load_level(self.level)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            hud = self.hud_font.render(self.fmt_time(self.play_time), False, (79, 110, 72))
            self.display.blit(hud, (6 - render_scroll[0], 6 - render_scroll[1]))

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
            
            self.crt.render()
            dt = self.clock.tick(60)
            if len(self.enemies):
                self.play_time += dt

Game().run()