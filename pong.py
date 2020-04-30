from math import cos, sin, radians
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
        self.MAX_ACC = 10
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

        # Physics
        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(5, 0)

        self.last_collision_time = 0

        # Constants
        self.MAX_SPEED = 8
        self.MAX_BOUNCE_ANGLE = 50

    def collide_edge(self):
        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x = -self.vel.x
        if self.pos.x > Pong.RESOLUTION[0] - self.rect.width:
            self.pos.x = Pong.RESOLUTION[0] - self.rect.width
            self.vel.x = -self.vel.x
        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y = -self.vel.y
        if self.pos.y > Pong.RESOLUTION[1] - self.rect.height:
            self.pos.y = Pong.RESOLUTION[1] - self.rect.height
            self.vel.y = -self.vel.y

    def collide_paddle(self):
        collision = pygame.sprite.spritecollideany(self, Pong.paddle_sprites, False)
        current_time = pygame.time.get_ticks()
        if collision and current_time - self.last_collision_time > 500:
            self.last_collision_time = current_time  # Fixes bug where ball gets stuck on paddle

            intersect_point = collision.rect.clip(self.rect).center
            # Center-y of paddle - intersection point = distance from center-y
            distance_from_center_y = collision.pos.y + (collision.rect.height / 2) - intersect_point[1]
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

    def update(self):
        self.collide_paddle()
        self.collide_edge()

        self.pos += self.vel
        self.rect.topleft = self.pos


class Interface:
    def __init__(self, game):
        self.game = game
        self.font_name = pygame.font.match_font("arial")

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.game.screen.blit(text_surface, text_rect)


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

        self.interface = Interface(self)

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
        self.interface.draw_text("SCORE", 48, (255, 255, 255), Pong.RESOLUTION[0]/2, 50)
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def update(self):
        self.all_sprites.update()


def main():
    pong = Pong()
    pong.run()


if __name__ == "__main__":
    main()
