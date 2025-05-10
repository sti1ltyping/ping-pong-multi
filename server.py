import socket
import threading
import pygame
from game import *

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Server - Player 1")

font = pygame.font.SysFont("Arial", 36)
clock = pygame.time.Clock()

p1 = Paddle(30)
p2 = Paddle(WIDTH - 40)
ball = Ball()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9999))
server.listen(1)

conn = None
addr = None
connected = False

score1 = 0
score2 = 0

def wait_for_connection():
    global conn, addr, connected
    conn, addr = server.accept()
    print(f"[INFO] Connected to {addr}")
    connected = True

threading.Thread(target=wait_for_connection, daemon=True).start()

def draw_waiting_screen():
    win.fill(BLACK)
    text = font.render("Waiting for player to join...", True, WHITE)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()

def draw_game():
    win.fill(BLACK)
    pygame.draw.rect(win, WHITE, p1.rect)
    pygame.draw.rect(win, WHITE, p2.rect)
    pygame.draw.ellipse(win, WHITE, ball.rect)

    score_text = font.render(f"{score1}   {score2}", True, WHITE)
    win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
    pygame.display.update()

def recv_data():
    global running
    buffer = ""
    while running:
        try:
            data = conn.recv(1024).decode()
            if not data:
                print("[ERROR] Client disconnected.")
                running = False
                break

            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                p2.rect.y = int(line.strip())
                print(f"[INFO] Received paddle y: {p2.rect.y}")

        except Exception as e:
            print(f"[ERROR] recv_data thread crashed: {e}")
            running = False
            break


running = True
game_started = False

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not connected:
        draw_waiting_screen()
        continue

    if not game_started:
        threading.Thread(target=recv_data, daemon=True).start()
        game_started = True

    mouse_y = pygame.mouse.get_pos()[1]
    p1.rect.y = mouse_y - p1.rect.height // 2

    if p1.rect.top < 0:
        p1.rect.top = 0
    elif p1.rect.bottom > HEIGHT:
        p1.rect.bottom = HEIGHT

    ball.move()

    if ball.rect.colliderect(p1.rect) and ball.vx < 0:
        ball.vx = -ball.vx
        ball.combo_hits += 1
        ball.increase_speed()

    if ball.rect.colliderect(p2.rect) and ball.vx > 0:
        ball.vx = -ball.vx
        ball.combo_hits += 1
        ball.increase_speed()

    if ball.rect.left <= 0:
        score2 += 1
        ball.reset()
    elif ball.rect.right >= WIDTH:
        score1 += 1
        ball.reset()

    try:
        message = f"{p1.rect.y}|{ball.rect.x},{ball.rect.y}|{score1},{score2}\n"
        conn.sendall(message.encode())
        print(f"[INFO] Sent: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to send data: {e}")
        running = False
        break

    draw_game()

pygame.quit()
if conn:
    conn.close()
