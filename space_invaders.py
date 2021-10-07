import pygame
import sys


class Game(pygame.sprite.Sprite):
    def __init__(self):
        super(Game, self).__init__()
        self.resolution = (640, 480)
        self.windowsize = pygame.display.set_mode(self.resolution, 0, 32)
        self.surface = pygame.Surface(self.windowsize.get_size())
        self.surface = self.surface.convert()
        self.level = 1
        self.rect = self.surface.get_rect()

    def level_up(self, level):
        return level+1


class Settings():
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.difficulty = "Easy"

    def open(self):
        pass

    def pause_game(self):
        pass

    def draw(self, resolution, surface):
        r = pygame.Rect((0, 0), resolution)
        pygame.draw.rect(surface, (0, 0, 0), r)


class Ship(pygame.sprite.Sprite):
    def __init__(self, windowsize):
        super().__init__()
        self.windowsize = windowsize
        self.score = 0
        self.image = pygame.image.load("ship.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0]//20, self.image.get_size()[1]//20))
        self.position = [self.windowsize[0]//2, (self.windowsize[1] - self.image.get_size()[1]) - 20]
        self.direction = ""
        self.rect = self.image.get_rect(center=self.position)
        self.all_lasers = pygame.sprite.GroupSingle()

    def move(self):
        if self.direction == "left":
            self.position[0] += -5
            self.rect = self.image.get_rect(center=self.position)
            self.direction = ""
        elif self.direction == "right":
            self.position[0] += 5
            self.rect = self.image.get_rect(center=self.position)
            self.direction = ""

    def fire(self):
        pass

    def draw(self, surface):
        surface.blit(self.image, self.position)

    def handle_keys(self, resolution):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    if len(self.all_lasers) == 0:
                        self.all_lasers.add(Laser(self.position, self.rect.topright))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if 5 <= self.position[0]:
                self.direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.position[0] <= resolution[0] * 0.9:
                self.direction = "right"


class Laser(pygame.sprite.Sprite):
    def __init__(self, ship_position, ship_rect):
        super().__init__()
        self.position = ship_position[:] # copying the list so they dont refer to the same memory
        self.position[0] = ship_rect[0] - 7
        self.position[1] = self.position[1] - 10
        self.image = pygame.image.load("coca_cola.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0] // 60, self.image.get_size()[1] // 60))
        self.rect = self.image.get_rect(center=self.position)

    def update(self, surface, ship):
        self.position[1] = self.position[1] - 10
        self.rect = self.image.get_rect(center=self.position)
        surface.blit(self.image, self.position)
        if self.position[1] < 0:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.position = [x, y]
        self.image = pygame.image.load("enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0] // 9, self.image.get_size()[1] // 9))
        self.rect = self.image.get_rect(center=self.position)
        self.direction = "right"

    def update(self, surface, resolution, enemy_group, all_lasers):
        if self.direction == "right":
            self.position[0] = self.position[0] + 0.5
            if self.position[0] >= resolution[0] - self.rect.width:
                self.position[1] += self.rect.height + 5
                self.direction = "left"
        else:
            self.position[0] = self.position[0] - 0.5
            if self.position[0] <= 0:
                self.position[1] += self.rect.height + 5
                self.direction = "right"
        self.rect = self.image.get_rect(center=self.position)
        pygame.sprite.groupcollide(all_lasers, enemy_group, True, True)
        surface.blit(self.image, self.position)


def main():
    pygame.init()
    game = Game()
    settings = Settings()
    ship = Ship(game.windowsize.get_size())
    test_alien = Alien(0, 0)
    enemy_group = pygame.sprite.Group()
    while True:
        if len(enemy_group) < 1:
            y_spawn = game.resolution[1] // 40
            for alienspawn_row in range(4):
                center_x_coordinate = game.resolution[0] // 2
                center_x_coordinate -= test_alien.rect.width * 4 - 10 * 3
                y_spawn += test_alien.rect.height + 5
                for alienspawn_coloumn in range(7):
                    enemy_group.add(Alien(center_x_coordinate, y_spawn))
                    center_x_coordinate += test_alien.rect.width + 10
        settings.clock.tick(100)
        settings.draw(game.resolution, game.surface)
        ship.draw(game.surface)
        ship.handle_keys(game.resolution)
        ship.move()
        if len(ship.all_lasers) > 0:
            for x in ship.all_lasers:
                x.update(game.surface, ship)
        enemy_group.update(game.surface, game.resolution, enemy_group, ship.all_lasers)
        game.windowsize.blit(game.surface, (0, 0))
        pygame.display.update()


main()