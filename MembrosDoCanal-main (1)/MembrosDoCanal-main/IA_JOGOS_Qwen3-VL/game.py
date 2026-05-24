import pygame
import random
import sys
import time
import os
import threading
from ollama import chat
from ollama import ChatResponse

# -------------------------------
# CONFIGURAÇÕES INICIAIS
# -------------------------------
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caça ao Tesouro com IA Real (Imagem Reduzida) 🤖")

# Cores
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)     # Jogador
GOLD = (255, 215, 0)   # Tesouro
RED = (255, 0, 0)      # Inimigos
BLACK = (0, 0, 0)      # Fundo
GRAY = (100, 100, 100) # Texto debug

# Jogador
player_size = 50
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT // 2 - player_size // 2
player_speed = 5

# Tesouro
treasure_size = 40
treasure_x = random.randint(0, WIDTH - treasure_size)
treasure_y = random.randint(0, HEIGHT - treasure_size)

# Inimigos
enemy_size = 40
num_enemies = 3
enemies = []
for _ in range(num_enemies):
    x = random.randint(0, WIDTH - enemy_size)
    y = random.randint(0, HEIGHT - enemy_size)
    dx = random.choice([-2, 2])
    dy = random.choice([-2, 2])
    enemies.append([x, y, dx, dy])

# Fonte
font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 24)
debug_font = pygame.font.SysFont("Arial", 18)

# Estado do jogo
game_won = False
game_over = False
last_ai_action_time = 0
ai_action_interval = 1.0  # 1s — menos chamadas, mais suave

# Memória da IA
visited_positions = set()
last_target = None

# Variáveis globais para thread
ai_target_x = None
ai_target_y = None
ai_busy = False

# Cria pasta temp
os.makedirs("imagens/temp", exist_ok=True)

# -------------------------------
# FUNÇÃO PARA SALVAR SCREENSHOT REDUZIDO
# -------------------------------
def save_screenshot_reduced():
    # Salva screenshot original
    screenshot_path = "imagens/temp/imagem_original.jpg"
    pygame.image.save(screen, screenshot_path)

    # Carrega a imagem e redimensiona para 400x300
    original_surface = pygame.image.load(screenshot_path)
    reduced_surface = pygame.transform.scale(original_surface, (200, 150))

    # Salva a imagem reduzida
    reduced_path = "imagens/temp/imagem_reduzida.jpg"
    pygame.image.save(reduced_surface, reduced_path)

    return reduced_path

# -------------------------------
# FUNÇÃO PARA PERGUNTAR AO MODELO (EM THREAD)
# -------------------------------
def ask_ai_in_thread():
    global ai_target_x, ai_target_y, ai_busy
    ai_busy = True
    try:
        image_path = save_screenshot_reduced()  # Imagem reduzida!
        response: ChatResponse = chat(
            model='qwen3-vl:235b-cloud',
            messages=[
                {
                    'role': 'user',
                    'content': (
                        "Analise esta imagem do jogo e me diga EXATAMENTE para onde o jogador deve ir para se aproximar do tesouro e evitar os inimigos. "
                        "Responda APENAS com as coordenadas no formato: 'TARGET_X, TARGET_Y'. "
                        "Exemplo: '400, 300'. "                        
                        "Se houver inimigos próximos, priorize fugir deles. "
                        "Não explique, não dê contexto, só as coordenadas."
                    ),
                    'images': [image_path]
                }
            ]
        )
        action = response.message.content.strip()
        parts = action.split(',')
        if len(parts) == 2:
            x = int(parts[0].strip())
            y = int(parts[1].strip())
            ai_target_x = x
            ai_target_y = y
        else:
            print(f"[IA] Resposta inválida: {action}")
            ai_target_x = None
            ai_target_y = None
    except Exception as e:
        print(f"[ERRO IA] {e} — verifique se o modelo está rodando")
        ai_target_x = None
        ai_target_y = None
    finally:
        ai_busy = False

# -------------------------------
# FUNÇÃO PARA MOVER JOGADOR COM BASE NAS COORDENADAS
# -------------------------------
def move_player_towards(target_x, target_y):
    if target_x is None or target_y is None:
        return player_x, player_y

    dx = target_x - player_x
    dy = target_y - player_y
    dist = (dx**2 + dy**2)**0.5

    if dist > 0:
        dx /= dist
        dy /= dist
        new_x = player_x + dx * player_speed
        new_y = player_y + dy * player_speed
        new_x = max(0, min(WIDTH - player_size, new_x))
        new_y = max(0, min(HEIGHT - player_size, new_y))
        return int(new_x), int(new_y)
    return player_x, player_y

# -------------------------------
# LOOP PRINCIPAL
# -------------------------------
clock = pygame.time.Clock()
running = True

while running:
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------------------------------
    # ATUALIZAÇÃO DO JOGO
    # -------------------------------
    if not game_won and not game_over:
        # MOVIMENTO DOS INIMIGOS
        for enemy in enemies:
            enemy[0] += enemy[2]
            enemy[1] += enemy[3]
            if enemy[0] <= 0 or enemy[0] >= WIDTH - enemy_size:
                enemy[2] *= -1
            if enemy[1] <= 0 or enemy[1] >= HEIGHT - enemy_size:
                enemy[3] *= -1

        # VERIFICAÇÃO DE COLISÕES
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        treasure_rect = pygame.Rect(treasure_x, treasure_y, treasure_size, 
treasure_size)

        if player_rect.colliderect(treasure_rect):
            game_won = True

        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
            if player_rect.colliderect(enemy_rect):
                game_over = True

        # -------------------------------
        # INTEGRAÇÃO COM IA — A CADA 1.0s (EM THREAD)
        # -------------------------------
        if current_time - last_ai_action_time >= ai_action_interval and not ai_busy:
            last_ai_action_time = current_time
            thread = threading.Thread(target=ask_ai_in_thread)
            thread.start()

        # Move jogador com base no último alvo da IA
        if ai_target_x is not None and ai_target_y is not None:
            new_x, new_y = move_player_towards(ai_target_x, ai_target_y)
            player_x = new_x
            player_y = new_y
            last_target = (ai_target_x, ai_target_y)

    # -------------------------------
    # DESENHO NA TELA
    # -------------------------------
    screen.fill(BLACK)

    # Desenha jogador
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    # Desenha tesouro
    pygame.draw.rect(screen, GOLD, (treasure_x, treasure_y, treasure_size, 
treasure_size))

    # Desenha inimigos
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], enemy_size, enemy_size))

    # Desenha memória (posições visitadas)
    for pos in visited_positions:
        x, y = pos
        pygame.draw.circle(screen, GRAY, (x + player_size//2, y + player_size//2), 2)

    # Desenha seta para o alvo da IA (se existir)
    if last_target:
        tx, ty = last_target
        pygame.draw.line(screen, (255, 255, 0), (player_x + player_size//2, player_y       
+ player_size//2), (tx, ty), 2)
        pygame.draw.circle(screen, (255, 255, 0), (tx, ty), 5)

    # Mostra texto debug
    debug_text = debug_font.render(f"IA: {last_target if last_target else '...'}",
True, WHITE)
    screen.blit(debug_text, (10, 10))

    # Mostra distância do jogador ao tesouro
    dist_to_treasure = int(((player_x - treasure_x)**2 + (player_y - 
treasure_y)**2)**0.5)
    dist_text = debug_font.render(f"Distância ao tesouro: {dist_to_treasure}", True,       
WHITE)
    screen.blit(dist_text, (10, 30))

    # Mostra número de inimigos próximos
    close_enemies = 0
    for enemy in enemies:
        dist = ((player_x - enemy[0])**2 + (player_y - enemy[1])**2)**0.5
        if dist < 100:
            close_enemies += 1
    enemy_text = debug_font.render(f"Inimigos próximos: {close_enemies}", True, 
WHITE)
    screen.blit(enemy_text, (10, 50))

    # -------------------------------
    # TELA DE VITÓRIA OU GAME OVER
    # -------------------------------
    if game_won:
        win_text = font.render("🎉 VOCÊ ENCONTROU O TESOURO! 🎉", True, (0, 255, 0))
        restart_text = small_font.render("Aperte R para jogar de novo", True, WHITE)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2       
+ 50))

    elif game_over:
        lose_text = font.render("💀 GAME OVER — FUISTE PEGO!", True, RED)
        restart_text = small_font.render("Aperte R para tentar de novo", True, WHITE)
        screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2       
+ 50))

    # -------------------------------
    # REINICIAR COM 'R'
    # -------------------------------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r] and (game_won or game_over):
        game_won = False
        game_over = False
        treasure_x = random.randint(0, WIDTH - treasure_size)
        treasure_y = random.randint(0, HEIGHT - treasure_size)
        player_x = WIDTH // 2 - player_size // 2
        player_y = HEIGHT // 2 - player_size // 2

        enemies = []
        for _ in range(num_enemies):
            x = random.randint(0, WIDTH - enemy_size)
            y = random.randint(0, HEIGHT - enemy_size)
            dx = random.choice([-2, 2])
            dy = random.choice([-2, 2])
            enemies.append([x, y, dx, dy])

        visited_positions.clear()
        last_target = None
        ai_target_x = None
        ai_target_y = None

    pygame.display.flip()
    clock.tick(60)  # 60 FPS — suave!

pygame.quit()
sys.exit()