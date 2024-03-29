import pygame, sys, random


class Game():
    """
    Author: Nico
    """
    def __init__(self):
        self.resolution = (640, 480)
        self.windowsize = pygame.display.set_mode(self.resolution, 0, 32)
        self.surface = pygame.Surface(self.windowsize.get_size())
        self.surface = self.surface.convert()
        self.image = pygame.image.load("bg.jpg").convert_alpha()
        self.settings = Settings(self.resolution)
        self.settings.start_button.update(self.surface, self.image, self.windowsize, self.resolution)
        self.score = 0
        self.rect = self.surface.get_rect()
        self.enemy_group = pygame.sprite.Group()
        self.dummy_alien = Alien(0, 0)
        self.ship_group = pygame.sprite.GroupSingle()
        self.ship = Ship(self.windowsize.get_size())
        self.ship_group.add(self.ship)
        self.all_bullets = pygame.sprite.GroupSingle()
        self.barrier_dummy = Barrier(0, 0)
        self.barrier_list = pygame.sprite.Group()
        x_coordinate = (self.resolution[0] - self.barrier_dummy.rect.width * 2) // 3
        y_coordinate = self.resolution[1] - self.ship.rect.height * 3
        for x in range (2):
            print(x_coordinate + self.barrier_dummy.rect.width * (x+0.5) + x_coordinate * x)
            print(self.resolution[1] - self.ship.rect.height * 3)
            self.barrier_list.add(Barrier(x_coordinate + self.barrier_dummy.rect.width * (x+0.5) + x_coordinate * x, y_coordinate))

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.ship.fire()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if 5 <= self.ship.rect.x:
                self.ship.direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.ship.rect.x <= self.resolution[0] * 0.9:
                self.ship.direction = "right"
        self.surface.blit(self.image, (0, 0))
        self.ship.move()
        self.ship.draw(self.surface)
        if len(self.enemy_group) < 1:
            y_spawn = self.resolution[1] // 40
            for alienspawn_row in range(4):
                center_x_coordinate = self.resolution[0] // 2
                center_x_coordinate -= self.dummy_alien.rect.width * 4 - 10 * 3
                y_spawn += self.dummy_alien.rect.height + 5
                for alienspawn_coloumn in range(7):
                    self.enemy_group.add(Alien(center_x_coordinate, y_spawn))
                    center_x_coordinate += self.dummy_alien.rect.width + 10
        if len(self.ship.all_lasers) > 0:
            for x in self.ship.all_lasers:
                x.update(self.surface)
        if len(self.all_bullets) < 1:
            random_number = random.randint(0, len(self.enemy_group)-1)
            self.all_bullets.add(Bullet(self.enemy_group.sprites()[random_number].rect.center))
        else:
            self.all_bullets.update(self.surface, self.resolution[1])
        self.enemy_group.update(self.surface, self.resolution, self.enemy_group)
        for x in pygame.sprite.groupcollide(self.ship.all_lasers, self.enemy_group, True, True):
            self.score += 10
        pygame.sprite.groupcollide(self.ship_group, self.all_bullets, True, True)
        for x in pygame.sprite.groupcollide(self.barrier_list, self.all_bullets, False, True):
            x.lives -= 1
        for x in pygame.sprite.groupcollide(self.barrier_list, self.ship.all_lasers, False, True):
            x.lives -= 1
        for x in pygame.sprite.groupcollide(self.barrier_list, self.enemy_group, False, True):
            x.lives -= 10
        self.barrier_list.update(self.surface)
        pygame.sprite.groupcollide(self.ship_group, self.enemy_group, True, True)


class Settings():
    """
    Author: Ayberk
    """
    def __init__(self, resolution):
        self.clock = pygame.time.Clock()
        self.start_button = Start_Button(resolution)


class Start_Button(pygame.sprite.Sprite):
    """
    Author: Ayberk
    """
    def __init__(self, game_resolution):
        super(Start_Button, self).__init__()
        self.resolution = game_resolution
        self.image = pygame.image.load("start_button.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0]//2, self.image.get_size()[1]//2))
        self.position = [game_resolution[0] // 2, 400]
        self.rect = self.image.get_rect(center=self.position)

    def update(self, surface, game_image, windowsize, resolution):
        start = False
        myfont = pygame.font.SysFont("arial black", 60)
        screen = pygame.display.set_mode((resolution), 0, 32)
        title_text = myfont.render(f"SPACE INVADERS", True, (118, 238, 198))
        while not start:
            windowsize.blit(surface, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        start = True
            surface.blit(game_image, (0, 0))
            screen.blit(title_text, (30, 100))
            surface.blit(self.image, self.rect)
            pygame.display.update()



class Ship(pygame.sprite.Sprite):
    """
    Author: Ayberk
    """
    def __init__(self, windowsize):
        super().__init__()
        self.windowsize = windowsize
        self.image = pygame.image.load("ship.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0]//20, self.image.get_size()[1]//20))
        self.position = [self.windowsize[0]//2, (self.windowsize[1] - self.image.get_size()[1]) - 20]
        self.direction = ""
        self.rect = self.image.get_rect(center=self.position)
        self.all_lasers = pygame.sprite.GroupSingle()

    def move(self):
        if self.direction == "left":
            self.rect.x += -5
            self.direction = ""
        elif self.direction == "right":
            self.rect.x += 5
            self.direction = ""

    def fire(self):
        if len(self.all_lasers) == 0:
            self.all_lasers.add(Laser(self.position, self.rect.topleft, self.rect.width))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Laser(pygame.sprite.Sprite):
    """
    Author: Ayberk
    """
    def __init__(self, ship_position, ship_rect, ship_width):
        super().__init__()
        self.position = ship_position[:] # copying the list so they dont refer to the same memory
        self.position[0] = ship_rect[0] + ship_width / 2 - 5
        self.position[1] = self.position[1] - 10
        self.image = pygame.image.load("coca_cola.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0] // 60, self.image.get_size()[1] // 60))
        self.rect = self.image.get_rect(center=self.position)

    def update(self, surface):
        self.position[1] = self.position[1] - 10
        self.rect = self.image.get_rect(center=self.position)
        surface.blit(self.image, self.position)
        if self.position[1] < 0:
            self.kill()


class Alien(pygame.sprite.Sprite):
    """
    Author: Nico
    """
    def __init__(self, x, y):
        super().__init__()
        self.position = [x, y]
        self.image = pygame.image.load("enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0] // 9, self.image.get_size()[1] // 9))
        self.rect = self.image.get_rect(center=self.position)
        self.direction = "right"
        self.move_denier = True

    def update(self, surface, resolution, enemy_group):
        if self.move_denier:
            if self.direction == "right":
                self.rect.x += 1
                self.move_denier = False
                if self.rect.x >= resolution[0] - self.rect.width:
                    self.rect.y += self.rect.height + 5
                    self.direction = "left"
            else:
                self.rect.x -= 1
                self.move_denier = False
                if self.rect.x <= 0:
                    self.rect.y += self.rect.height + 5
                    self.direction = "right"
        else:
            self.move_denier = True
        surface.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    """
    Author: Nico
    """
    def __init__(self, enemy_rect):
        super(Bullet, self).__init__()
        self.position = [0, 0]
        self.position[0] = enemy_rect[0]
        self.position[1] = enemy_rect[1] + 10
        self.image = pygame.image.load("bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0] // 10, self.image.get_size()[1] // 10))
        self.rect = self.image.get_rect(center=self.position)

    def update(self, surface, y_height):
        self.rect.y = self.rect.y + 2.5
        surface.blit(self.image, self.rect)
        if self.rect.y > y_height:
            self.kill()


class Barrier(pygame.sprite.Sprite):
    """
    Author: Nico
    """
    def __init__(self, x_pos, y_pos):
        super(Barrier, self).__init__()
        self.position = [x_pos, y_pos]
        self.lives = 10
        self.image = pygame.image.load("Barrier.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0], self.image.get_size()[1]))
        self.rect = self.image.get_rect(center=self.position)

    def update(self, surface):
        if self.lives > 0:
            surface.blit(self.image, self.rect)
        else:
            self.kill()


def main():
    """
    Author: Nico
    :return: /
    """
    pygame.init()
    highscore = 0
    while True:
        game = Game()
        screen = pygame.display.set_mode((game.resolution), 0, 32)
        myfont = pygame.font.SysFont("arial black", 16)
        while True:
            game.settings.clock.tick(100)
            game.update()
            game.windowsize.blit(game.surface, (0, 0))
            highscore_text = myfont.render(f"Highscore: {highscore}", True, (238, 0, 0))
            score_text = myfont.render(f"Score: {game.score}", True, (118, 238, 198))
            screen.blit(highscore_text, (5, 10))
            screen.blit(score_text, (5, 30))
            pygame.display.update()
            if len(game.ship_group) < 1:
                if highscore < game.score:
                    highscore = game.score
                break


main()
