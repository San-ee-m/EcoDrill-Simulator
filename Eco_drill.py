import pygame
import sys
import os
import json
from datetime import datetime

pygame.init()
pygame.mixer.init()

# ================== SCREEN ==================
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EcoDrill Simulator")
clock = pygame.time.Clock()

# ================== BASE PATH ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================== SOUNDS ==================
rig_idle_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "rig_idle.wav"))
rig_drill_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "rig_drill.wav"))

# ================== COLORS ==================
BLUE = (40, 120, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GRAY = (30, 30, 30)
DARK_OVERLAY = (80, 80, 80, 150)

# ================== FONT ==================
font = pygame.font.SysFont(None, 26)
bold_font = pygame.font.SysFont(None, 40, bold=True)
title_font = pygame.font.SysFont("Comic_Sans", 60, bold=True)
mono_font = pygame.font.SysFont("Consolas", 20, bold=True)

# ================== GAME VARIABLES ==================
oil = 0
money = 0
goal_money = 2000
pollution = 0
environment = 100
drilling = False
can_drill = True
cooldown_timer = 0
COOLDOWN_DURATION = 300  # 5 seconds at 60fps

upgrade_level = 0
drill_efficiency = 1.0
upgrade_base_cost = 50
upgrade_cost_increase = 10
oil_sell_rate = 2

# Leaderboard & player
player_name = "Player"
selected_difficulty = "Easy"
difficulty_goals = {"Easy": 1000, "Medium": 3000, "Hard": 10000, "Extreme": 50000}

# ================== GAME STATE ==================
game_over = False
goal_reached = False
end_timer = 0
END_DURATION = 300  # 5 seconds

# ================== LOAD FRAMES ==================
def load_frames(folder_name):
    frames = []
    base_folder = os.path.join(BASE_DIR, folder_name)
    if os.path.exists(base_folder):
        # loop over all subfolders
        for subfolder in sorted(os.listdir(base_folder)):
            sub_path = os.path.join(base_folder, subfolder)
            if os.path.isdir(sub_path):
                for f in sorted(os.listdir(sub_path)):
                    if f.endswith(".png"):
                        img = pygame.image.load(os.path.join(sub_path, f)).convert_alpha()
                        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                        frames.append(img)
    print(folder_name, "frames loaded:", len(frames))
    return frames

rig_frames = load_frames("RigFrames")
rig_drill_frames = load_frames("RigDrillFrames")
eff_rig_frames = load_frames("EffRigFrames")

# ================== FALLBACK FRAME ==================
fallback_frame = pygame.Surface((WIDTH, HEIGHT))
fallback_frame.fill((15, 15, 15))

frame_i = drill_i = eff_i = 0
tick = drill_tick = eff_tick = 0
FRAME_DELAY = 4

# ================== BUTTON CLASS ==================
class Button:
    def __init__(self, x, y, w, h, text, color, hover):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self):
        mouse = pygame.mouse.get_pos()
        c = self.hover if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=8)
        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, e):
        return e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos)

# ================== UI ==================
def draw_bar(x, y, value, max_value, color, label):
    w, h = 200, 16
    fill = max(0, min(w, (value / max_value) * w))
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2)
    pygame.draw.rect(screen, color, (x, y, fill, h))
    text = font.render(f"{label}: {int(value)}%", True, WHITE)
    screen.blit(text, (x + w + 10, y - 2))

# ================== BUTTONS ==================
drill_btn = Button(600, 180, 160, 45, "DRILL", (40,160,40), (70,190,70))
sell_btn  = Button(600, 240, 160, 45, "SELL OIL", (160,120,40), (190,150,70))
shop_btn  = Button(600, 300, 160, 45, "SHOP", (40,40,160), (70,70,200))
exit_btn  = Button(600, 360, 160, 45, "EXIT", (160,40,40), (200,70,70))

# ================== HELPERS ==================
def upgrade_cost():
    return upgrade_base_cost + upgrade_level * upgrade_cost_increase

def reset_game():
    global oil, money, pollution, environment, drill_efficiency, upgrade_level
    global game_over, goal_reached, end_timer, can_drill, cooldown_timer
    oil = money = pollution = 0
    environment = 100
    drill_efficiency = 1.0
    upgrade_level = 0
    game_over = goal_reached = False
    can_drill = True
    cooldown_timer = 0
    end_timer = 0

# ================== SHOP ==================
def shop_menu():
    global money, upgrade_level, drill_efficiency
    buy = Button(300, 300, 200, 50, "BUY UPGRADE", (40,160,40), (70,190,70))
    back = Button(300, 370, 200, 50, "BACK", (160,40,40), (200,70,70))
    running = True
    while running:
        screen.fill(GRAY)
        screen.blit(font.render(f"Money: ${int(money)}",True,WHITE),(30,30))
        screen.blit(title_font.render("Upgrade Shop", True, WHITE), (230, 100))
        screen.blit(font.render(f"Upgrade Cost: {upgrade_cost()} money", True, WHITE), (300, 190))
        screen.blit(font.render(f"Level: {upgrade_level}", True, WHITE), (300, 220))
        screen.blit(mono_font.render(f"Efficiency: x{drill_efficiency:.1f}", True, WHITE), (300, 250))
        buy.draw()
        back.draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if buy.clicked(e) and money >= upgrade_cost():
                money -= upgrade_cost()
                upgrade_level += 1
                drill_efficiency = 1.0 + upgrade_level * 0.3
            if back.clicked(e):
                running = False
        pygame.display.flip()
        clock.tick(60)

# ================== MENUS ==================
def main_menu():
    start_btn = Button(300, 250, 200, 50, "START", (50,160,50), (80,190,80))
    quit_btn = Button(300, 390, 200, 50, "EXIT", (160,40,40), (200,70,70))
    leader_btn = Button(300,320,200,50,"LEADERBOARD",(40,40,160),(70,70,200))
    while True:
        screen.fill(BLUE)
        title = title_font.render("EcoDrill Simulator", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))
        start_btn.draw()
        quit_btn.draw()
        leader_btn.draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if start_btn.clicked(e):
                return "start"
            if quit_btn.clicked(e):
                pygame.quit(); sys.exit()
            if leader_btn.clicked(e):
                leaderboard_screen()
        pygame.display.flip()
        clock.tick(60)

# ================== OBJECTIVES / TUTORIAL ==================
def objective_screen():
    start_btn = Button(300, 300, 200, 50, "START", (50,160,50), (80,190,80))
    back_btn = Button(300, 370, 200, 50, "BACK", (160,40,40), (200,70,70))
    while True:
        screen.fill(GRAY)
        header = title_font.render("How to Play", True, WHITE)
        screen.blit(header, header.get_rect(center=(WIDTH//2, 100)))
        lines = [
            "- Drill oil to reach your goal money",
            "- Sell oil to get money",
            "- Upgrade your drill for efficiency",
            "- Monitor pollution and environment",
            "- Environment collapse ends the game",
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, WHITE), (70, 160 + i*30))
        start_btn.draw()
        back_btn.draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if start_btn.clicked(e):
                return "start"
            if back_btn.clicked(e):
                return "back"
        pygame.display.flip()
        clock.tick(60)

# ================== DIFFICULTY ==================
def difficulty_menu():
    global goal_money, selected_difficulty
    easy = Button(100, 200, 150, 50, "Easy", (40,160,40), (70,190,70))
    medium = Button(300, 200, 150, 50, "Medium", (200,160,40), (230,190,70))
    hard = Button(500, 200, 150, 50, "Hard", (200,50,50), (230,80,80))
    extreme = Button(280, 280, 200, 50, "Extreme", (80,0,160), (110,30,200))
    while True:
        screen.fill(GRAY)
        screen.blit(title_font.render("Select Difficulty", True, WHITE), (150, 100))
        for b in [easy, medium, hard, extreme]:
            b.draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if easy.clicked(e):
                selected_difficulty = "Easy"
                goal_money = difficulty_goals[selected_difficulty]
                return
            if medium.clicked(e):
                selected_difficulty = "Medium"
                goal_money = difficulty_goals[selected_difficulty]
                return
            if hard.clicked(e):
                selected_difficulty = "Hard"
                goal_money = difficulty_goals[selected_difficulty]
                return
            if extreme.clicked(e):
                selected_difficulty = "Extreme"
                goal_money = difficulty_goals[selected_difficulty]
                return
        pygame.display.flip()
        clock.tick(60)

# ================== NAME INPUT ==================
def name_input_screen():
    global player_name
    input_box = pygame.Rect(250, 220, 300, 45)
    color_inactive = (100, 100, 100)
    color_active = (50, 200, 50)
    color = color_inactive
    active = False
    text = ""
    done = False
    while not done:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(e.pos)
                color = color_active if active else color_inactive
            if e.type == pygame.KEYDOWN and active:
                if e.key == pygame.K_RETURN:
                    player_name = text.strip() if text.strip() else "Player"
                    done = True
                elif e.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 12:
                        text += e.unicode
        screen.fill(GRAY)
        screen.blit(title_font.render("Enter Your Name", True, WHITE), (150, 130))
        pygame.draw.rect(screen, color, input_box, 2)
        screen.blit(font.render(text, True, WHITE), (input_box.x+5, input_box.y+8))
        pygame.display.flip()
        clock.tick(60)

# ================== LEADERBOARD ==================
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_to_leaderboard(time_taken):
    data = load_leaderboard()
    data.append({
        "name": player_name,
        "difficulty": selected_difficulty,
        "time": round(time_taken, 2),
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    data = sorted(data, key=lambda x: x["time"])[:10]
    save_leaderboard(data)

def leaderboard_screen():
    data = load_leaderboard()
    back = Button(300, 420, 200, 50, "BACK", (160,40,40), (200,70,70))
    while True:
        screen.fill(GRAY)
        screen.blit(title_font.render("Leaderboard", True, WHITE), (200, 80))
        for i, entry in enumerate(data):
            screen.blit(font.render(f"{i+1}. {entry['name']} | {entry['difficulty']} | {entry['time']}s | {entry['date']}", True, WHITE), (80, 160 + i*30))
        back.draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if back.clicked(e):
                return
        pygame.display.flip()
        clock.tick(60)

# ================== END SCREEN ==================
def show_end_screen(msg, time_taken=None):
    local_end_timer = 0

    if time_taken is not None:
        add_to_leaderboard(time_taken)

    # Pre-render text (do this once, not every frame)
    title_surf = bold_font.render(msg, True, WHITE)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))

    if time_taken is not None:
        time_surf = font.render(f"Time: {round(time_taken, 2)}s", True, WHITE)
        time_rect = time_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

    while local_end_timer < END_DURATION:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)

        screen.blit(title_surf, title_rect)

        if time_taken is not None:
            screen.blit(time_surf, time_rect)

        pygame.display.flip()
        clock.tick(60)
        local_end_timer += 1

    rig_idle_sound.stop()
    rig_drill_sound.stop()
    reset_game()
    leaderboard_screen()


# ================== GAME LOOP ==================
def run_game_loop():
    global oil, money, pollution, environment, drilling, can_drill, cooldown_timer, drill_efficiency, goal_money
    oil = money = pollution = 0
    environment = 100
    drilling = False
    can_drill = True
    cooldown_timer = 0
    frame_i = drill_i = tick = drill_tick = 0
    current_sound_local = None
    game_over = False
    goal_reached = False
    import time
    start_time = time.time()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if not game_over and can_drill:
                if drill_btn.clicked(e):
                    drilling = True
            if e.type == pygame.MOUSEBUTTONUP and drilling:
                drilling = False
                can_drill = False
                cooldown_timer = 0
            if sell_btn.clicked(e) and oil>0:
                money += oil*oil_sell_rate
                oil = 0
            if shop_btn.clicked(e):
                shop_menu()
            if exit_btn.clicked(e):
                rig_idle_sound.stop(); rig_drill_sound.stop(); return
        # Logic
        if drilling and can_drill and not game_over:
            oil += 0.3*drill_efficiency
            pollution += 0.5/drill_efficiency
            environment -= 0.4/drill_efficiency
        elif not can_drill:
            cooldown_timer +=1
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(GRAY)
            screen.blit(overlay,(0,0))
            if cooldown_timer>=COOLDOWN_DURATION:
                can_drill=True
        else:
            pollution=max(0,pollution-0.25)
            environment=min(100, environment+0.15)
        if environment<=0: game_over=True
        if money>=goal_money and not goal_reached: goal_reached=True
        # Draw rig
        frame=fallback_frame
        if drilling and rig_drill_frames:
            current_drill_frames = eff_rig_frames if drill_efficiency>=5 else rig_drill_frames
            drill_tick+=1
            if drill_tick>=FRAME_DELAY:
                drill_tick=0
                drill_i=(drill_i+1)%len(current_drill_frames)
            frame=current_drill_frames[drill_i]
        elif rig_frames:
            tick+=1
            if tick>=FRAME_DELAY:
                tick=0
                frame_i=(frame_i+1)%len(rig_frames)
            frame=rig_frames[frame_i]
        screen.blit(frame,(0,0))
        # Sound
        if drilling:
            if current_sound_local!="drill":
                rig_drill_sound.set_volume(1.0); rig_drill_sound.play(-1)
                rig_idle_sound.set_volume(0.25)
                if rig_idle_sound.get_num_channels()==0: rig_idle_sound.play(-1)
                current_sound_local="drill"
        else:
            if current_sound_local!="idle":
                rig_drill_sound.stop()
                rig_idle_sound.set_volume(0.8); rig_idle_sound.play(-1)
                current_sound_local="idle"
        # UI
        elapsed = time.time()-start_time
        panel = pygame.Surface((WIDTH,120)); panel.set_alpha(190); panel.fill(GRAY); screen.blit(panel,(0,0))
        screen.blit(font.render(f"Money: ${int(money)}/ ${goal_money}", True, WHITE), (20,20))
        screen.blit(font.render(f"Oil Stored: {int(oil)}", True, WHITE), (20,45))
        screen.blit(mono_font.render(f"Efficiency: x{drill_efficiency:.1f}", True, WHITE), (20,70))
        screen.blit(font.render(f"Time: {elapsed:.2f}s",True,WHITE),(200,20))
        draw_bar(WIDTH-370,20,pollution,100,RED,"Pollution")
        draw_bar(WIDTH-370,50,environment,100,GREEN,"Environment")
        drill_btn.draw()
        if not can_drill:
            overlay = pygame.Surface((drill_btn.rect.w, drill_btn.rect.h)); overlay.set_alpha(120); overlay.fill(GRAY); screen.blit(overlay,(drill_btn.rect.x, drill_btn.rect.y))
            remaining=max(0,COOLDOWN_DURATION-cooldown_timer)//60+1
            timer_text=font.render(str(remaining), True, WHITE)
            screen.blit(timer_text,timer_text.get_rect(center=drill_btn.rect.center))
        sell_btn.draw(); shop_btn.draw(); exit_btn.draw()
        if environment<=20 and drilling:
            warn=pygame.Surface((WIDTH,HEIGHT)); warn.set_alpha(130); warn.fill(RED); screen.blit(warn,(0,0))
            screen.blit(bold_font.render("ENVIRONMENT CRITICAL", True, WHITE), (WIDTH//2-150,220))
        pygame.display.flip()
        clock.tick(60)
        # End conditions
        if game_over:
            rig_idle_sound.stop(); rig_drill_sound.stop(); current_sound_local=None
            show_end_screen("ENVIRONMENTAL COLLAPSE")
            return
        elif goal_reached:
            rig_idle_sound.stop(); rig_drill_sound.stop(); current_sound_local=None
            show_end_screen("GOAL ACHIEVED!", elapsed)
            return

# ================== MAIN LOOP ==================
while True:
    main_menu()
    res = objective_screen()
    if res=="back": continue
    elif res=="start":
        difficulty_menu()
        name_input_screen()
        reset_game()
        run_game_loop()


