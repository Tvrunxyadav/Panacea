import sys

import pygame

pygame.init()

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Panacea")
        self.screen = pygame.display.set_mode((640, 480))

        self.clock = pygame.time.Clock()

        self.image_pos = [160, 260]
        self.movement = [False, False]

        self.collision_area = pygame.Rect(100, 50, 100, 100)

        self.img = pygame.image.load("data/images/entities/player.png")

    def run(self):
        while True:
            self.screen.fill((221, 198, 161))

            img_r = pygame.Rect(self.image_pos[0], self.image_pos[1], self.img.get_width(), self.img.get_height())
            if img_r.colliderect(self.collision_area):
                pygame.draw.rect(self.screen, (100, 100, 100), self.collision_area)
            else:
                pygame.draw.rect(self.screen, (0,0,0), self.collision_area)

            
            self.image_pos[1] += (self.movement[1] - self.movement[0]) *5
            self.screen.blit(self.img, self.image_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False
                    
            pygame.display.update()
            self.clock.tick(60)

Game().run()