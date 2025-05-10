import socket
import threading
import pygame
from game import *

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client - Player 2")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.x.x", 9999)) # Your loacal server IP

clock = pygame.time.Clock()
p1 = Paddle(30)
p2 = Paddle(WIDTH - 40)
ball = Ball()

score1 = 0
score2 = 0
font = pygame.font.SysFont("Arial", 32)

def recv_data():
    global score1, score2
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break

            paddle_y, ball_pos, score_str = data.split("|")
            p1.rect.y = int(paddle_y)

            bx, by = map(int, ball_pos.split(","))
            ball.rect.x, ball.rect.y = bx, by

            score1, score2 = map(int, score_str.split(","))
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

threading.Thread(target=recv_data, daemon=True).start()

run = True
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    mouse_y = pygame.mouse.get_pos()[1]
    p2.rect.y = mouse_y - p2.rect.height // 2

    if p2.rect.top < 0:
        p2.rect.top = 0
    elif p2.rect.bottom > HEIGHT:
        p2.rect.bottom = HEIGHT

    try:
        client.sendall(f"{p2.rect.y}\n".encode())
    except Exception as e:
        print(f"Error sending data: {e}")
        break

    win.fill(BLACK)
    pygame.draw.rect(win, WHITE, p1.rect)
    pygame.draw.rect(win, WHITE, p2.rect)
    pygame.draw.ellipse(win, WHITE, ball.rect)

    score_text = font.render(f"{score1}   {score2}", True, WHITE)
    win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    pygame.display.update()

pygame.quit()
client.close()
