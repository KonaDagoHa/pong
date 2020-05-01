from math import cos, sin, radians
from random import choice
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Pygame
        self.image = pygame.Surface((15, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(10, 10))

        # Physics
        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)

        # Constants
        self.MAX_ACC = 1
        self.FRICTION = -0.12

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
            self.acc.y -= self.MAX_ACC
        # if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            # self.acc.x -= self.ACC_MAGNITUDE
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.acc.y += self.MAX_ACC
        # if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            # self.acc.x += self.ACC_MAGNITUDE

        self.collide_edge()

        self.acc += self.vel * self.FRICTION
        self.vel += self.acc
        self.pos += self.vel + (0.5 * self.acc)

        self.rect.topleft = self.pos


class Computer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(Pong.RESOLUTION[0] - 15 - 10, 10))

        # Physics
        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)

        self.last_move_time = 0

        # Constants
        self.MAX_ACC = 5
        self.FRICTION = -0.12

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
        self.acc = pygame.Vector2(0, 0)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time > 100:
            for ball in Pong.ball_sprites:
                distance_from_ball = abs(self.pos.x - ball.pos.x)
                if distance_from_ball < 200:
                    if ball.pos.y < self.pos.y:
                        self.acc.y -= self.MAX_ACC
                    if ball.pos.y > self.pos.y:
                        self.acc.y += self.MAX_ACC
                    self.last_move_time = current_time  # Fixes computer shaking

        self.collide_edge()

        self.acc += self.vel * self.FRICTION
        self.vel += self.acc
        self.pos += self.vel + (0.5 * self.acc)

        self.rect.topleft = self.pos


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(Pong.RESOLUTION[0]/2, Pong.RESOLUTION[1]/2))

        # Constants
        self.MAX_SPEED = 8
        self.MAX_BOUNCE_ANGLE = 60

        # Physics
        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(choice((-self.MAX_SPEED/2, self.MAX_SPEED/2)),
                                  choice((-self.MAX_SPEED/2, 0, self.MAX_SPEED/2)))

        # Misc.
        self.last_collision_time = 0

        # Future invisible ball used for AI to predict ball path
        self.future_rect = self.rect.copy()
        self.future_pos = pygame.Vector2(self.future_rect.topleft)
        self.future_vel = pygame.Vector2(self.vel.xy * 2)

        """ DELETE THIS LATER """
        self.future_image = pygame.Surface((15, 15))
        self.future_image.fill((0, 255, 0))

    def collide_edge(self):
        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x = -self.vel.x
        elif self.pos.x > Pong.RESOLUTION[0] - self.rect.width:
            self.pos.x = Pong.RESOLUTION[0] - self.rect.width
            self.vel.x = -self.vel.x
        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y = -self.vel.y
        elif self.pos.y > Pong.RESOLUTION[1] - self.rect.height:
            self.pos.y = Pong.RESOLUTION[1] - self.rect.height
            self.vel.y = -self.vel.y

        # Future ball
        if self.future_pos.x < 0:
            self.future_pos.x = 0
            self.future_vel.x = 0
            self.future_vel.y = 0
        elif self.future_pos.x > Pong.RESOLUTION[0] - self.future_rect.width:
            self.future_pos.x = Pong.RESOLUTION[0] - self.future_rect.width
            self.future_vel.x = 0
            self.future_vel.y = 0
        if self.future_pos.y < 0:
            self.future_pos.y = 0
            self.future_vel.y = -self.future_vel.y
        elif self.future_pos.y > Pong.RESOLUTION[1] - self.future_rect.height:
            self.future_pos.y = Pong.RESOLUTION[1] - self.future_rect.height
            self.future_vel.y = -self.future_vel.y

    def collide_paddle(self):
        collision = pygame.sprite.spritecollideany(self, Pong.paddle_sprites, False)
        current_time = pygame.time.get_ticks()
        if collision and current_time - self.last_collision_time > 500:
            self.last_collision_time = current_time  # Fixes bug where ball gets stuck on paddle

            self.future_rect.topleft = self.rect.topleft

            # Bounce ball off paddle
            collision_point = collision.rect.clip(self.rect).center
            # Center-y of paddle - intersection point = distance from center-y
            distance_from_center_y = collision.pos.y + (collision.rect.height / 2) - collision_point[1]
            # Distance from center-y / half of paddle height = normalized distance from center-y
            normed_distance = distance_from_center_y / (collision.rect.height / 2)
            # Hit ball at edge -> bigger angle, higher speed
            bounce_angle = normed_distance * self.MAX_BOUNCE_ANGLE
            speed = max(normed_distance * self.MAX_SPEED, self.MAX_SPEED / 2)
            # Ball speed * cos(max bounce angle) = velocity
            if self.vel.x < 0:
                self.vel.x = speed * cos(radians(bounce_angle))
            else:
                self.vel.x = speed * -cos(radians(bounce_angle))
            self.vel.y = speed * -sin(radians(bounce_angle))

            # Future ball
            self.future_pos = pygame.Vector2(self.pos.xy)
            self.future_vel = pygame.Vector2(self.vel.xy) * 2

    def update(self):
        self.collide_paddle()
        self.collide_edge()

        self.pos += self.vel
        self.rect.topleft = self.pos

        # Future ball
        self.future_pos += self.future_vel
        self.future_rect.topleft = self.future_pos

        print("{} {}".format(self.pos, self.future_pos))


class Interface:
    def __init__(self):
        self.font_name = pygame.font.match_font("arial")

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        Pong.screen.blit(text_surface, text_rect)


class Pong:
    # Constants
    RESOLUTION = (800, 600)
    MAX_FPS = 60
    # Globals
    all_sprites = pygame.sprite.Group()
    paddle_sprites = pygame.sprite.Group()
    ball_sprites = pygame.sprite.Group()
    screen = None

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pong")
        Pong.screen = pygame.display.set_mode(Pong.RESOLUTION)
        self.clock = pygame.time.Clock()

        self.is_running = True

        # Sprites
        player = Player()
        computer = Computer()
        ball = Ball()
        Pong.all_sprites.add(player, computer, ball)
        Pong.paddle_sprites.add(player, computer)
        Pong.ball_sprites.add(ball)

        self.interface = Interface()

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
        Pong.screen.fill((0, 0, 0))
        self.interface.draw_text("SCORE", 48, (255, 255, 255), Pong.RESOLUTION[0]/2, 50)
        self.all_sprites.draw(Pong.screen)

        """ DELETE THIS LATER """
        for ball in Pong.ball_sprites:
            Pong.screen.blit(ball.future_image, ball.future_pos)

        pygame.display.update()

    def update(self):
        self.all_sprites.update()


def main():
    pong = Pong()
    pong.run()


if __name__ == "__main__":
    main()
