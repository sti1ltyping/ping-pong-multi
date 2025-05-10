import pygame

WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 120

class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    def move(self, up=True):
        if up:
            self.rect.y -= 5
        else:
            self.rect.y += 5
        self.rect.y = max(0, min(self.rect.y, HEIGHT - PADDLE_HEIGHT))

class Ball:
    def __init__(self):
        self.default_speed = 5
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
        self.vx = self.default_speed * (-1 if pygame.time.get_ticks() % 2 == 0 else 1)
        self.vy = self.default_speed
        self.combo_hits = 0


    def move(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vy = -self.vy

    def increase_speed(self):
        if self.combo_hits < 3:
            speed = self.default_speed
        else:
            speed = min(self.default_speed + (self.combo_hits - 2) * 0.5, 12)

        self.vx = speed if self.vx > 0 else -speed
        self.vy = self.vy if self.vy == 0 else (self.vy / abs(self.vy)) * speed


