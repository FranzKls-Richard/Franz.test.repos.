import pygame
import sys
import random
import time

# --- CONFIG -----------------------------------------------------------------
WIDTH, HEIGHT = 1000, 600          # Window size
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 110
BALL_SIZE = 18
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_SPEED = 7
BALL_SPEED = 6
BALL_MAX_SPEED = 12   # cap speed growth

# Ability settings
ABILITY_KEY_LEFT  = pygame.K_q     # Taste für linken Spieler
ABILITY_KEY_RIGHT = pygame.K_p     # Taste für rechten Spieler
ABILITY_DURATION  = 5              # Sekunden aktive Verstärkung
ABILITY_COOLDOWN  = 12             # Sekunden bis erneute Nutzung
PADDLE_BUFF_SIZE  = 170            # Höhe während Ability

# --- INIT -------------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong++ – jetzt mit Score & Superkräften!")
clock = pygame.time.Clock()

font_score  = pygame.font.SysFont("Arial", 48, bold=True)
font_small  = pygame.font.SysFont("Arial", 24)

# Paddles --------------------------------------------------------------------
left_paddle = pygame.Rect(40, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 40 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

left_default_h  = PADDLE_HEIGHT
right_default_h = PADDLE_HEIGHT

# Ball -----------------------------------------------------------------------
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
ball_vel = pygame.Vector2(random.choice((BALL_SPEED, -BALL_SPEED)), random.choice((BALL_SPEED, -BALL_SPEED)))

def reset_ball():
    global ball_vel
    ball.center = (WIDTH//2, HEIGHT//2)
    speed = BALL_SPEED
    ball_vel = pygame.Vector2(random.choice((speed, -speed)), random.choice((speed, -speed)))

# Score ----------------------------------------------------------------------
left_score  = 0
right_score = 0

# Ability state --------------------------------------------------------------
left_ability_ready_time  = 0   # Zeitstempel, wann Ability wieder nutzbar
right_ability_ready_time = 0
left_ability_end   = 0
right_ability_end  = 0

def activate_ability(side):
    global left_paddle, right_paddle, left_ability_ready_time, right_ability_ready_time, left_ability_end, right_ability_end
    now = time.time()
    if side == "left" and now >= left_ability_ready_time:
        left_paddle.height = PADDLE_BUFF_SIZE
        # keep paddle centered
        left_paddle.centery = max(min(left_paddle.centery, HEIGHT - left_paddle.height//2), left_paddle.height//2)
        left_ability_end = now + ABILITY_DURATION
        left_ability_ready_time = now + ABILITY_COOLDOWN
    elif side == "right" and now >= right_ability_ready_time:
        right_paddle.height = PADDLE_BUFF_SIZE
        right_paddle.centery = max(min(right_paddle.centery, HEIGHT - right_paddle.height//2), right_paddle.height//2)
        right_ability_end = now + ABILITY_DURATION
        right_ability_ready_time = now + ABILITY_COOLDOWN

def update_abilities():
    now = time.time()
    if left_paddle.height > left_default_h and now >= left_ability_end:
        left_paddle.height = left_default_h
    if right_paddle.height > right_default_h and now >= right_ability_end:
        right_paddle.height = right_default_h

def move_paddles(keys):
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED

def move_ball():
    global ball_vel, left_score, right_score
    ball.x += int(ball_vel.x)
    ball.y += int(ball_vel.y)

    # Bounce off top/bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_vel.y *= -1

    collision = None
    # Bounce off paddles
    if ball.colliderect(left_paddle) and ball_vel.x < 0:
        collision = "left"
    elif ball.colliderect(right_paddle) and ball_vel.x > 0:
        collision = "right"

    if collision:
        ball_vel.x *= -1
        # Gradual speed increase, capped
        if abs(ball_vel.x) < BALL_MAX_SPEED:
            ball_vel.x *= 1.05
            ball_vel.y *= 1.05

    # Score check
    if ball.left <= 0:
        right_score += 1
        reset_ball()
    elif ball.right >= WIDTH:
        left_score += 1
        reset_ball()

def draw():
    screen.fill(BLACK)

    # Middle dashed line
    for y in range(0, HEIGHT, 30):
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 2, y+5, 4, 20))

    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Scores
    score_text = font_score.render(f"{left_score}   {right_score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH//2, 50))
    screen.blit(score_text, score_rect)

    # Ability status bars
    now = time.time()
    # left
    left_ready = max(0, left_ability_ready_time - now)
    left_width = int(200 * (1 - left_ready/ABILITY_COOLDOWN)) if left_ready > 0 else 200
    pygame.draw.rect(screen, WHITE, (50, 10, left_width, 8))
    # right
    right_ready = max(0, right_ability_ready_time - now)
    right_width = int(200 * (1 - right_ready/ABILITY_COOLDOWN)) if right_ready > 0 else 200
    pygame.draw.rect(screen, WHITE, (WIDTH-250, 10, right_width, 8))

    # Ability labels
    screen.blit(font_small.render("Q = Fähigkeit", True, WHITE), (50, 22))
    screen.blit(font_small.render("P = Fähigkeit", True, WHITE), (WIDTH-250, 22))

    pygame.display.flip()

# --- MAIN LOOP --------------------------------------------------------------
reset_ball()
running = True
while running:
    clock.tick(FPS)
    update_abilities()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == ABILITY_KEY_LEFT:
                activate_ability("left")
            elif event.key == ABILITY_KEY_RIGHT:
                activate_ability("right")

    keys = pygame.key.get_pressed()
    move_paddles(keys)
    move_ball()
    draw()

pygame.quit()
sys.exit()