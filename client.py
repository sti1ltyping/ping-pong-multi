import socket
import threading
import pygame
from game import *

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client - Player 2")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.192.158", 9999))  # Replace with your server IP

clock = pygame.time.Clock()
p1 = Paddle(30)
p2 = Paddle(WIDTH - 40)
ball = Ball()

score1 = 0
score2 = 0
font = pygame.font.SysFont("Arial", 32)

target_p1_y = p1.rect.y
target_ball_x = ball.rect.x
target_ball_y = ball.rect.y

def lerp(a, b, t):
    return a + (b - a) * t

def recv_data():
    global score1, score2, running
    global target_p1_y, target_ball_x, target_ball_y
    buffer = ""
    while running:
        try:
            data = client.recv(1024).decode()
            if not data:
                print("[ERROR] Server disconnected.")
                running = False
                break

            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                paddle_y, ball_pos, score_str = line.strip().split("|")

                target_p1_y = int(paddle_y)

                bx, by = map(int, ball_pos.split(","))
                target_ball_x, target_ball_y = bx, by

                score1, score2 = map(int, score_str.split(","))
        except Exception as e:
            print(f"[ERROR] recv_data thread crashed: {e}")
            running = False
            break

def send_data():
    try:
        client.sendall(f"{p2.rect.y}\n".encode())
    except Exception as e:
        print(f"[ERROR] Failed to send: {e}")

running = True
threading.Thread(target=recv_data, daemon=True).start()

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_y = pygame.mouse.get_pos()[1]
    p2.rect.y = mouse_y - p2.rect.height // 2
    p2.rect.y = max(0, min(p2.rect.y, HEIGHT - p2.rect.height))

    send_data()

    p1.rect.y = int(lerp(p1.rect.y, target_p1_y, 0.2))
    ball.rect.x = int(lerp(ball.rect.x, target_ball_x, 0.2))
    ball.rect.y = int(lerp(ball.rect.y, target_ball_y, 0.2))

    win.fill(BLACK)
    pygame.draw.rect(win, WHITE, p1.rect)
    pygame.draw.rect(win, WHITE, p2.rect)
    pygame.draw.ellipse(win, WHITE, ball.rect)

    score_text = font.render(f"{score1}   {score2}", True, WHITE)
    win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    fps_text = font.render(str(int(clock.get_fps())), True, WHITE)
    win.blit(fps_text, (10, 10))

    pygame.display.update()

pygame.quit()
client.close()
