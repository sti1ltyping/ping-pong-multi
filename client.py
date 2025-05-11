import socket
import asyncio
import pygame
from game import *

FIXED_WIDTH = 730
FIXED_HEIGHT = 540

pygame.init()
win = pygame.display.set_mode((FIXED_WIDTH, FIXED_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Client - Player 2")
font = pygame.font.SysFont("Arial", 32)
clock = pygame.time.Clock()

p1 = Paddle(30)
p2 = Paddle(WIDTH - 40)
ball = Ball()
score1 = 0
score2 = 0

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.x.x", 9999))  # Local Host IP
client.setblocking(False)


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


async def recv_data():
    global score1, score2
    loop = asyncio.get_running_loop()
    buffer = ""
    try:
        while True:
            data = await loop.sock_recv(client, 1024)
            if not data:
                print("[ERROR] Server disconnected.")
                break
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                paddle_y, ball_pos, score_str = line.strip().split("|")
                p1.rect.y = int(paddle_y)
                ball.rect.x, ball.rect.y = map(int, ball_pos.split(","))
                score1, score2 = map(int, score_str.split(","))
    except Exception as e:
        print(f"[ERROR] recv_data crashed: {e}")


async def send_data_loop():
    loop = asyncio.get_running_loop()
    try:
        while True:
            await asyncio.sleep(0.01)
            y_data = f"{p2.rect.y}\n".encode()
            await loop.sock_sendall(client, y_data)
    except Exception as e:
        print(f"[ERROR] send_data crashed: {e}")


async def main():
    recv_task = asyncio.create_task(recv_data())
    send_task = asyncio.create_task(send_data_loop())

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_y_scaled = pygame.mouse.get_pos()[1] * HEIGHT / win.get_height()
        p2.rect.y = int(mouse_y_scaled - p2.rect.height // 2)
        p2.rect.y = max(0, min(p2.rect.y, HEIGHT - p2.rect.height))

        draw_scaled_game()

        await asyncio.sleep(0)

    recv_task.cancel()
    send_task.cancel()
    pygame.quit()
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
