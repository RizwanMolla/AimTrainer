import math
import pygame
import random
import time

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 80

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 500
TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 50
BG_COLOR = (0, 25, 40)
LIVES = 5
TOP_BAR_HEIGHT = 40

MAX_TARGETS = 5  # Limit number of targets on screen
LABEL_FONT = pygame.font.SysFont("monospaced", 28)
HEADING_FONT = pygame.font.SysFont("sansserif", 64, bold=True)
END_FONT = pygame.font.SysFont("sansserif", 32, bold=True)

# Sound effects
hit_sound = pygame.mixer.Sound(r"D:\Projects\Project 1\hit.wav")
miss_sound = pygame.mixer.Sound(r"D:\Projects\Project 1\miss.wav")

# Difficulty settings
DIFFICULTY = {
    'easy': {'size': 40, 'growth_rate': 0.2},
    'medium': {'size': 30, 'growth_rate': 0.3},
    'hard': {'size': 25, 'growth_rate': 0.4}
}

def draw_gradient_background(win, color1, color2):
    """Create a gradient background from color1 to color2."""
    for i in range(HEIGHT):
        blend_color = [
            color1[j] + (color2[j] - color1[j]) * i // HEIGHT for j in range(3)
        ]
        pygame.draw.line(win, blend_color, (0, i), (WIDTH, i))

class Target:
    def __init__(self, x, y, size, growth_rate):
        self.x = x
        self.y = y
        self.size = 0
        self.max_size = size
        self.growth_rate = growth_rate
        self.grow = True

    def update(self):
        if self.size + self.growth_rate >= self.max_size:
            self.grow = False

        if self.grow:
            self.size += self.growth_rate
        else:
            self.size -= self.growth_rate

    def draw(self, win):
        pygame.draw.circle(win, "red", (self.x, self.y), self.size)
        pygame.draw.circle(win, "white", (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, "red", (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, "white", (self.x, self.y), self.size * 0.4)
        pygame.draw.circle(win, "red", (self.x, self.y), self.size * 0.2)

    def collide(self, x, y):
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance <= self.size

def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"

def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    pygame.draw.rect(win, "aqua", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(f"Time : {format_time(elapsed_time)}", 1, "black")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")

    win.blit(time_label, (5, 10))
    win.blit(speed_label, (250, 10))
    win.blit(hits_label, (500, 10))
    win.blit(lives_label, (700, 10))

def draw(win, targets):
    draw_gradient_background(win, (0, 25, 40), (0, 0, 80))  # Gradient background
    for target in targets:
        target.draw(win)

def end_screen(win, elapsed_time, targets_pressed, clicks):
    draw_gradient_background(win, (0, 25, 40), (0, 0, 80))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")
    accuracy = round(targets_pressed / clicks * 100, 1) if clicks > 0 else 0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")

    restart_label = END_FONT.render(f"Press R to Restart or Press Q to Quit", 1, "white")

    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 175))
    win.blit(hits_label, (get_middle(hits_label), 250))
    win.blit(accuracy_label, (get_middle(accuracy_label), 325))
    win.blit(restart_label, (get_middle(restart_label), 500))

    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main_menu(win)  # Restart
                if event.key == pygame.K_q:
                    quit()  # Quit

def get_middle(surface):
    return WIDTH / 2 - surface.get_width() / 2

def main_menu(win):
    draw_gradient_background(win, (0, 25, 40), (0, 0, 80))  # Gradient background
    title_label = HEADING_FONT.render("Aim Trainer", 1, (0, 255, 255))
    instructions_label = LABEL_FONT.render("Press [E] for Easy, [M] for Medium, [H] for Hard", 1, "white")
    
    win.blit(title_label, (get_middle(title_label), 150))
    win.blit(instructions_label, (get_middle(instructions_label), 300))
    
    pygame.display.update()

    difficulty = None
    while difficulty is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    difficulty = 'easy'
                elif event.key == pygame.K_m:
                    difficulty = 'medium'
                elif event.key == pygame.K_h:
                    difficulty = 'hard'
    
    main(difficulty)

def main(difficulty):
    run = True
    targets = []
    clock = pygame.time.Clock()

    clicks = 0
    targets_pressed = 0
    misses = 0
    start_time = time.time()

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(FPS)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == TARGET_EVENT:
                if len(targets) < MAX_TARGETS:
                    x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                    y = random.randint(TARGET_PADDING, HEIGHT - TARGET_PADDING)
                    size = DIFFICULTY[difficulty]['size']
                    growth_rate = DIFFICULTY[difficulty]['growth_rate']
                    target = Target(x, y, size, growth_rate)
                    targets.append(target)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        for target in targets:
            target.update()
            if target.size <= 0:
                targets.remove(target)
                misses += 1
                miss_sound.play()
            if click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_pressed += 1
                hit_sound.play()

        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks)  # End game

        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main_menu(WIN)
