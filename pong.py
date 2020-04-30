from random import randint
from math import cos, sin, radians
import pygame


class Player(pygame.sprite.Sprite):
    # Constants
    ACC_MAGNITUDE = 1
    FRICTION = -0.12

    def __init__(self):
        super().__init__()
        # Pygame
        self.image = pygame.Surface((15, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(50, 50))

        # Physics
        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)

    def collide_edge(self):
        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x = 0
        if self.pos.x > Pong.RESOLUTION[0] - self.rect.width:
            self.pos.x = Pong.RESOLUTION[0] - self.rect.width
            self.vel.x = 0
        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y = 0
        if self.pos.y > Pong.RESOLUTION[1] - self.rect.height:
            self.pos.y = Pong.RESOLUTION[1] - self.rect.height
            self.vel.y = 0

    def update(self):
        keys = pygame.key.get_pressed()
        self.acc = pygame.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.acc.y -= Player.ACC_MAGNITUDE
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acc.x -= Player.ACC_MAGNITUDE
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.acc.y += Player.ACC_MAGNITUDE
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.acc.x += Player.ACC_MAGNITUDE

        self.collide_edge()

        self.acc += self.vel * Player.FRICTION
        self.vel += self.acc
        self.pos += self.vel + (0.5 * self.acc)

        self.rect.topleft = self.pos


class Computer(pygame.sprite.Sprite):
    # Constants
    ACC_MAGNITUDE = 0.5
    FRICTION = -0.12

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(Pong.RESOLUTION[0] - 50, 50))

        # Physics
        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)

        self.moving_up = False

    def collide_edge(self):
        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x = 0
        if self.pos.x > Pong.RESOLUTION[0] - self.rect.width:
            self.pos.x = Pong.RESOLUTION[0] - self.rect.width
            self.vel.x = 0
        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y = 0
            self.moving_up = False
        if self.pos.y > Pong.RESOLUTION[1] - self.rect.height:
            self.pos.y = Pong.RESOLUTION[1] - self.rect.height
            self.vel.y = 0
            self.moving_up = True

    def update(self):
        self.acc = pygame.Vector2(0, 0)

        if self.moving_up:
            self.acc.y -= Computer.ACC_MAGNITUDE
        else:
            self.acc.y += Computer.ACC_MAGNITUDE

        self.collide_edge()

        self.acc += self.vel * Computer.FRICTION
        self.vel += self.acc
        self.pos += self.vel + (0.5 * self.acc)

        self.rect.topleft = self.pos


class Ball(pygame.sprite.Sprite):
    # Constants
    VEL_MAGNITUDE = 10
    MAX_BOUNCE_ANGLE = 45

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(Pong.RESOLUTION[0]/2, Pong.RESOLUTION[1]/2))

        # Physics
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(randint(-1, 1) * Ball.VEL_MAGNITUDE, 0)

        self.radius = self.rect.width / 2

    def collide_edge(self):
        if self.pos.x < self.radius:
            self.pos.x = self.radius
            self.vel.x = -self.vel.x
        if self.pos.x > Pong.RESOLUTION[0] - self.radius:
            self.pos.x = Pong.RESOLUTION[0] - self.radius
            self.vel.x = -self.vel.x
        if self.pos.y < self.radius:
            self.pos.y = self.radius
            self.vel.y = -self.vel.y
        if self.pos.y > Pong.RESOLUTION[1] - self.radius:
            self.pos.y = Pong.RESOLUTION[1] - self.radius
            self.vel.y = -self.vel.y

    def collide_paddle(self):
        collision = pygame.sprite.spritecollideany(self, Pong.paddle_sprites, False)
        if collision:
            intersect_point = self.rect.clip(collision.rect).center
            # Center-y of paddle - intersection point = relative intersection point
            relative_intersect_y = collision.pos.y + (collision.rect.height / 2) - intersect_point[1]
            # Relative intersection / half of paddle height = normalized relative intersection point
            normed_relative_intersect_y = relative_intersect_y / (collision.rect.height / 2)
            # Hit ball at edge -> bigger angle, higher speed
            bounce_angle = normed_relative_intersect_y * Ball.MAX_BOUNCE_ANGLE
            # Ball speed * cos(max bounce angle) = velocity
            self.vel.x = Ball.VEL_MAGNITUDE * cos(radians(bounce_angle))
            self.vel.y = Ball.VEL_MAGNITUDE * -sin(radians(bounce_angle))

    def update(self):
        self.collide_paddle()
        self.collide_edge()

        self.pos += self.vel
        self.rect.center = self.pos


class Pong:
    # Constants
    RESOLUTION = (800, 600)
    MAX_FPS = 60
    # Globals
    all_sprites = pygame.sprite.Group()
    paddle_sprites = pygame.sprite.Group()
    ball_sprites = pygame.sprite.Group()

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode(Pong.RESOLUTION)
        self.clock = pygame.time.Clock()

        self.is_running = True

        # Sprites
        player = Player()
        computer = Computer()
        ball = Ball()
        Pong.all_sprites.add(player, computer, ball)
        Pong.paddle_sprites.add(player, computer)
        Pong.ball_sprites.add(ball)

    def run(self):
        # Game loop
        while self.is_running:
            self.draw()
            self.update()
            self.clock.tick(Pong.MAX_FPS)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def update(self):
        self.all_sprites.update()


def main():
    pong = Pong()
    pong.run()


if __name__ == "__main__":
    main()
