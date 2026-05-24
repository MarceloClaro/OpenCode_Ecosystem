import pygame
import random
import sys
import time
import os
import threading
from dataclasses import dataclass

try:
    from ollama import chat
    from ollama import ChatResponse
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60
FIELD_MARGIN = 40

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚽ Futebol IA vs Humano — Atacante + Defensor Inteligente v3 (1x1)")
clock = pygame.time.Clock()

GREEN = (34, 139, 34)
DARK_GREEN = (24, 100, 24)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
GRAY = (120, 120, 120)

font = pygame.font.SysFont("Arial", 28)
small = pygame.font.SysFont("Arial", 20)

GOAL_WIDTH = 12
GOAL_HEIGHT = 180
FRICTION = 0.985

PLAYER_SIZE = 40
PLAYER_SPEED = 5.0
AI_SPEED = 4.8

BALL_RADIUS = 12
BALL_MAX_SPEED = 11.0
BALL_KICK_IMPULSE = 8.5

AI_INTERVAL = 0.4
REDUCED_W, REDUCED_H = 320, 180
MODEL_NAME = os.getenv("SOCCER_AI_MODEL", "qwen3-vl:235b-cloud")

os.makedirs("imagens/temp", exist_ok=True)

@dataclass
class Player:
    x: float
    y: float
    color: tuple
    speed: float
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)

@dataclass
class Ball:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    def pos(self):
        return (int(self.x), int(self.y))

def draw_field(surface: pygame.Surface):
    surface.fill(DARK_GREEN)
    field_rect = pygame.Rect(FIELD_MARGIN, FIELD_MARGIN, WIDTH - 2*FIELD_MARGIN, HEIGHT - 2*FIELD_MARGIN)
    pygame.draw.rect(surface, GREEN, field_rect)
    pygame.draw.rect(surface, WHITE, field_rect, 2)
    center_line_x = WIDTH // 2
    pygame.draw.line(surface, WHITE, (center_line_x, FIELD_MARGIN), (center_line_x, HEIGHT - FIELD_MARGIN), 2)
    pygame.draw.circle(surface, WHITE, (center_line_x, HEIGHT // 2), 70, 2)
    left_goal = pygame.Rect(FIELD_MARGIN - GOAL_WIDTH, (HEIGHT - GOAL_HEIGHT) // 2, GOAL_WIDTH, GOAL_HEIGHT)
    right_goal = pygame.Rect(WIDTH - FIELD_MARGIN, (HEIGHT - GOAL_HEIGHT) // 2, GOAL_WIDTH, GOAL_HEIGHT)
    pygame.draw.rect(surface, WHITE, left_goal)
    pygame.draw.rect(surface, WHITE, right_goal)
    return left_goal, right_goal

def goal_rects():
    left_goal = pygame.Rect(FIELD_MARGIN - GOAL_WIDTH, (HEIGHT - GOAL_HEIGHT) // 2, GOAL_WIDTH, GOAL_HEIGHT)
    right_goal = pygame.Rect(WIDTH - FIELD_MARGIN, (HEIGHT - GOAL_HEIGHT) // 2, GOAL_WIDTH, GOAL_HEIGHT)
    return left_goal, right_goal

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def reset_positions(player_h: Player, player_ai: Player, ball: Ball):
    player_h.x, player_h.y = FIELD_MARGIN + 90, HEIGHT/2 - PLAYER_SIZE/2
    player_ai.x, player_ai.y = WIDTH - FIELD_MARGIN - 90 - PLAYER_SIZE, HEIGHT/2 - PLAYER_SIZE/2
    ball.x, ball.y = WIDTH/2, HEIGHT/2
    ball.vx = random.uniform(-2, 2)
    ball.vy = random.uniform(-2, 2)

aI_lock = threading.Lock()
ai_busy = False
ai_target = None
last_ai_time = 0.0

def save_reduced_screenshot(surface: pygame.Surface) -> str:
    path_full = "imagens/temp/soccer_full.jpg"
    pygame.image.save(surface, path_full)
    img = pygame.image.load(path_full)
    reduced = pygame.transform.smoothscale(img, (REDUCED_W, REDUCED_H))
    path_small = "imagens/temp/soccer_small.jpg"
    pygame.image.save(reduced, path_small)
    return path_small

def ask_ai_target(surface: pygame.Surface, ball: Ball, player_h: Player, player_ai: Player):
    global ai_busy, ai_target
    with aI_lock:
        if ai_busy:
            return
        ai_busy = True

    def _worker():
        global ai_busy, ai_target
        try:
            img_path = save_reduced_screenshot(surface)
            left_goal, right_goal = goal_rects()
            context = (
                f"Contexto:\n"
                f"- Bola: ({int(ball.x)}, {int(ball.y)})\n"
                f"- Humano: ({int(player_h.x)}, {int(player_h.y)})\n"
                f"- IA: ({int(player_ai.x)}, {int(player_ai.y)})\n"
                f"- Gol HUMANO: lado ESQUERDO (x < {left_goal.right})\n"
                f"- Gol IA: lado DIREITO (x > {right_goal.left})\n"
            )

            prompt = (
                "Você controla o jogador VERMELHO (IA) em um jogo de futebol 2D. "
                "Seu estilo é ATACANTE AGRESSIVO, mas deve DEFENDER seu gol se a bola estiver próxima.\n\n"
                + context +
                "Regras de decisão (em prioridade):\n"
                "1) ⚠️ Se a bola estiver dentro de 200px do seu gol (lado direito), ABANDONE o ataque e vá defender. Posicione-se entre a bola e o gol ou tente afastá-la.\n"
                "2) ⚽️ Se puder chutar em direção ao gol da ESQUERDA, posicione-se ATRÁS da bola e chute.\n"
                "3) 🚫 Se a bola estiver com o humano, intercepte o caminho entre ele e o gol.\n"
                "4) 🔁 Se estiver longe, antecipe a trajetória da bola e se posicione.\n"
                "5) 📍 Nunca fique travado nos cantos. Reposicione-se centralmente antes de atacar.\n\n"
                "Responda SOMENTE com coordenadas 'X, Y'. Exemplo: '720, 300'"
            )

            if not OLLAMA_AVAILABLE:
                raise RuntimeError("Cliente de modelo não disponível.")

            response: ChatResponse = chat(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': prompt, 'images': [img_path]}]
            )
            action = response.message.content.strip()
            parts = action.split(',')
            if len(parts) == 2:
                tx = int(float(parts[0].strip()))
                ty = int(float(parts[1].strip()))
                ai_target = (tx, ty)
            else:
                ai_target = None
        except Exception:
            ai_target = None
        finally:
            with aI_lock:
                ai_busy = False

    threading.Thread(target=_worker, daemon=True).start()

def circle_rect_collision(cx, cy, r, rect: pygame.Rect):
    closest_x = clamp(cx, rect.left, rect.right)
    closest_y = clamp(cy, rect.top, rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx*dx + dy*dy) <= r*r

def handle_ball_player_collision(ball: Ball, player: Player, left_goal: pygame.Rect):
    rect = player.rect()
    if circle_rect_collision(ball.x, ball.y, BALL_RADIUS, rect):
        px = rect.centerx
        py = rect.centery
        dx = ball.x - px
        dy = ball.y - py
        mag = (dx*dx + dy*dy) ** 0.5 or 1.0
        dx /= mag
        dy /= mag
        impulse = BALL_KICK_IMPULSE
        dist_to_left = abs(ball.x - left_goal.right)
        if left_goal.top - 40 <= ball.y <= left_goal.bottom + 40 and dist_to_left < 180:
            impulse *= 1.35
        ball.vx = clamp(ball.vx + dx * impulse, -BALL_MAX_SPEED, BALL_MAX_SPEED)
        ball.vy = clamp(ball.vy + dy * impulse, -BALL_MAX_SPEED, BALL_MAX_SPEED)
        ball.x += dx * (BALL_RADIUS + 2)
        ball.y += dy * (BALL_RADIUS + 2)

def update_ball(ball: Ball):
    ball.vx *= FRICTION
    ball.vy *= FRICTION
    if abs(ball.vx) < 0.02: ball.vx = 0.0
    if abs(ball.vy) < 0.02: ball.vy = 0.0
    ball.x += ball.vx
    ball.y += ball.vy
    left = FIELD_MARGIN
    right = WIDTH - FIELD_MARGIN
    top = FIELD_MARGIN
    bottom = HEIGHT - FIELD_MARGIN
    goal_top = (HEIGHT - GOAL_HEIGHT) // 2
    goal_bottom = goal_top + GOAL_HEIGHT
    if ball.x - BALL_RADIUS < left:
        if not (goal_top <= ball.y <= goal_bottom):
            ball.x = left + BALL_RADIUS
            ball.vx *= -0.9
    if ball.x + BALL_RADIUS > right:
        if not (goal_top <= ball.y <= goal_bottom):
            ball.x = right - BALL_RADIUS
            ball.vx *= -0.9
    if ball.y - BALL_RADIUS < top:
        ball.y = top + BALL_RADIUS
        ball.vy *= -0.9
    if ball.y + BALL_RADIUS > bottom:
        ball.y = bottom - BALL_RADIUS
        ball.vy *= -0.9

def main():
    global last_ai_time
    player_h = Player(FIELD_MARGIN + 90, HEIGHT/2 - PLAYER_SIZE/2, BLUE, PLAYER_SPEED)
    player_ai = Player(WIDTH - FIELD_MARGIN - 90 - PLAYER_SIZE, HEIGHT/2 - PLAYER_SIZE/2, RED, AI_SPEED)
    ball = Ball(WIDTH/2, HEIGHT/2)

    score_h = 0
    score_ai = 0
    running = True
    show_help = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    show_help = not show_help
                if event.key == pygame.K_r:
                    reset_positions(player_h, player_ai, ball)

        keys = pygame.key.get_pressed()
        vx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        vy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        if vx != 0 or vy != 0:
            mag = (vx*vx + vy*vy) ** 0.5
            vx /= mag
            vy /= mag
            player_h.x += vx * player_h.speed
            player_h.y += vy * player_h.speed
        player_h.x = clamp(player_h.x, FIELD_MARGIN, WIDTH - FIELD_MARGIN - PLAYER_SIZE)
        player_h.y = clamp(player_h.y, FIELD_MARGIN, HEIGHT - FIELD_MARGIN - PLAYER_SIZE)

        now = time.time()
        if now - last_ai_time >= AI_INTERVAL:
            last_ai_time = now
            ask_ai_target(screen, ball, player_h, player_ai)

        if ai_target is not None:
            tx, ty = ai_target
            dx = tx - (player_ai.x + PLAYER_SIZE/2)
            dy = ty - (player_ai.y + PLAYER_SIZE/2)
            dist = (dx*dx + dy*dy) ** 0.5 or 1.0
            dx /= dist
            dy /= dist
            player_ai.x += dx * player_ai.speed
            player_ai.y += dy * player_ai.speed
        player_ai.x = clamp(player_ai.x, FIELD_MARGIN, WIDTH - FIELD_MARGIN - PLAYER_SIZE)
        player_ai.y = clamp(player_ai.y, FIELD_MARGIN, HEIGHT - FIELD_MARGIN - PLAYER_SIZE)

        left_goal, right_goal = goal_rects()
        handle_ball_player_collision(ball, player_h, right_goal)
        handle_ball_player_collision(ball, player_ai, left_goal)
        update_ball(ball)

        lg, rg = draw_field(screen)
        pygame.draw.circle(screen, YELLOW, (int(ball.x), int(ball.y)), BALL_RADIUS)
        pygame.draw.rect(screen, player_h.color, player_h.rect())
        pygame.draw.rect(screen, player_ai.color, player_ai.rect())

        score_text = font.render(f"Humano {score_h}  x  {score_ai} IA", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 8))

        if show_help:
            tips = [
                "Setas/WASD: mover (campo todo)",
                "R: reiniciar | H: ajuda",
                f"Modelo: {MODEL_NAME} | IA cada {AI_INTERVAL:.1f}s",                
            ]
            for i, t in enumerate(tips):
                screen.blit(small.render(t, True, WHITE), (12, 10 + 24 * i))

        if ai_target is not None:
            pygame.draw.line(screen, WHITE, (player_ai.x + PLAYER_SIZE/2, player_ai.y + PLAYER_SIZE/2), ai_target, 2)
            pygame.draw.circle(screen, WHITE, (int(ai_target[0]), int(ai_target[1])), 5, 1)

        if (ball.x - BALL_RADIUS) < lg.right and lg.top < ball.y < lg.bottom:
            score_ai += 1
            reset_positions(player_h, player_ai, ball)
        if (ball.x + BALL_RADIUS) > rg.left and rg.top < ball.y < rg.bottom:
            score_h += 1
            reset_positions(player_h, player_ai, ball)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
