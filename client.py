import socket
import threading
import pygame
from game import *

FIXED_WIDTH = 730
FIXED_HEIGHT = 540

pygame.init()
win = pygame.display.set_mode((FIXED_WIDTH, FIXED_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Client - Player 2")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.x.x", 9999))  # Replace with your server IP

clock = pygame.time.Clock()
p1 = Paddle(30)
p2 = Paddle(WIDTH - 40)
ball = Ball()
font = pygame.font.SysFont("Arial", 32)

score1 = 0
score2 = 0

def recv_data():
    global score1, score2, running
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
                p1.rect.y = int(paddle_y)
                ball.rect.x, ball.rect.y = map(int, ball_pos.split(","))
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

def draw_scaled_game():
    temp_surface = pygame.Surface((WIDTH, HEIGHT))
    temp_surface.fill(BLACK)
    pygame.draw.rect(temp_surface, WHITE, p1.rect)
    pygame.draw.rect(temp_surface, WHITE, p2.rect)
    pygame.draw.ellipse(temp_surface, WHITE, ball.rect)
    score_text = font.render(f"{score1}   {score2}", True, WHITE)
    temp_surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
    scaled_surface = pygame.transform.scale(temp_surface, win.get_size())
    win.blit(scaled_surface, (0, 0))
    pygame.display.update()

running = True
threading.Thread(target=recv_data, daemon=True).start()

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_y_scaled = pygame.mouse.get_pos()[1] * HEIGHT / win.get_height()
    p2.rect.y = int(mouse_y_scaled - p2.rect.height // 2)
    p2.rect.y = max(0, min(p2.rect.y, HEIGHT - p2.rect.height))

    send_data()
    draw_scaled_game()

pygame.quit()
client.close()
