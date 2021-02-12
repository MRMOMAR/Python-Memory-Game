import pygame
import os.path
import sys
import random
import ctypes

IMAGES_NAME = ["card1", "card2", "card3", "card4", "card5", "card6"]

IMAGES_EXTENSION = ".png"

WINDOW_WIDTH = 950
WINDOW_HEIGHT = 700

# Card data basics
CARD_WIDTH =125
CARD_HEIGHT =150

MENU_WIDTH = 230
MENU_HEIGHT = WINDOW_HEIGHT

frames = []

card_backward_image = None
board = []

animations = []
current_pair = []
is_wrong = False
last_wrong_time = 0
how_many_pairs = 0

score = 0
match_time = 0
match_start_time = None
match_is_running = True
leave_button = None
restart_button = None
logo = None

# Sounds
score_sound = None
flip_sound = None
victory_sound = None
error_sound = None

class Card:
    card_name = ""
    card_image = ""
    card_rectangle = None
    is_backward = True

    def __init__(self, card_name, card_image, is_backward = True):
        self.card_name = card_name
        self.card_image = card_image
        self.is_backward = is_backward

    def set_rectangle(self, rect):
        self.card_rectangle = rect

    def flip_card(self):
        self.is_backward = not self.is_backward


class Animation:
    images = []
    frame_interval = 0
    current_index = 0
    last_time_called = 0
    rect = None

    def __init__(self, images, rect, frame_interval = 8):
        self.images = images
        self.frame_interval = frame_interval
        self.current_index = 0
        self.rect = rect

    def update(self, current_time):
        if current_time - self.last_time_called >= self.frame_interval and not self.finished():
            frame = self.images[self.current_index]
            self.last_time_called = current_time
            self.current_index += 1
            return frame
        else:
            return None
    
    def finished(self):
        return len(self.images) - 1 <= self.current_index


def draw_load_screen(progress):
    global logo
    logo = pygame.transform.scale(logo, (int(WINDOW_WIDTH * 0.3), int(WINDOW_WIDTH * 0.12)))
    rect = (int(WINDOW_WIDTH * 0.35), int(WINDOW_HEIGHT * 0.7) - int(WINDOW_WIDTH * 0.12) - 50, int(WINDOW_WIDTH * 0.3), int(WINDOW_WIDTH * 0.12))
    screen.blit(logo, rect)

    progress_bar_border = (int(WINDOW_WIDTH * 0.2), int(WINDOW_HEIGHT * 0.7), int(WINDOW_WIDTH * 0.6), 50)
    pygame.draw.rect(screen, (255,255,255), progress_bar_border)

    progress_bar = (int(WINDOW_WIDTH * 0.2 + 5), int(WINDOW_HEIGHT * 0.7 + 5), int( (WINDOW_WIDTH * 0.6 - 10) * progress), 40)
    pygame.draw.rect(screen, (31,187,218), progress_bar)
    pygame.display.flip()

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("DOOBY DOOO....")
pygame.display.set_icon(pygame.image.load(os.path.join("images", IMAGES_NAME[0] + IMAGES_EXTENSION)))

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
screen.fill((255,255,255))

score_sound = pygame.mixer.Sound(os.path.join("sounds", "point.wav"))
victory_sound = pygame.mixer.Sound(os.path.join("sounds", "victory.wav"))
error_sound = pygame.mixer.Sound(os.path.join("sounds", "error.wav"))
flip_sound = pygame.mixer.Sound(os.path.join("sounds", "flip.wav"))


logo = pygame.image.load(os.path.join("images", "logo.jpg"))
logo = pygame.transform.scale(logo, (500, 300))
draw_load_screen(0 / 280)

card_backward_image = pygame.image.load(os.path.join("images", "question.png"))
draw_load_screen(1 / 280)

current_progress = 2

# Load card's back frames (same for all cards => Reduce loading time)
cards_back_frames = []
for i in range(1, 31):
    frame_name = str(i).zfill(4) + IMAGES_EXTENSION
    cards_back_frames.append(pygame.image.load(os.path.join("animations", os.path.join(IMAGES_NAME[0], frame_name))))
    draw_load_screen(current_progress / 280)
    current_progress += 1

for i in IMAGES_NAME:
    frames.append(list(cards_back_frames))     
    draw_load_screen(current_progress / 280)
    current_progress += 1

index = 0
for card_name in IMAGES_NAME:
    card_image = pygame.image.load(os.path.join("images", card_name + IMAGES_EXTENSION))

    board.append(Card(card_name, card_image))
    board.append(Card(card_name, card_image))

    current_frames = []
    for i in range(31, 61):
        frame_name = str(i).zfill(4) + IMAGES_EXTENSION
        current_frames.append(pygame.image.load(os.path.join("animations", os.path.join(card_name, frame_name))))
        draw_load_screen(current_progress / 280)
        current_progress += 1

    frames[index] += current_frames
    index += 1

screen.fill((255, 255,255))
pygame.time.delay(100)


def draw_menu():
    # Reset:
    menu_rect = pygame.Rect(0, 0, MENU_WIDTH, MENU_HEIGHT)
    pygame.draw.rect(screen, (242,246,116), menu_rect)

    # Logo:
    global logo
    logo = pygame.transform.scale(logo, (260, 100))
    rect = pygame.Rect(0, 0, MENU_WIDTH, 100)
    screen.blit(logo, rect)
    write_game_data()


    # Buttons to leave and restart:
    f = pygame.font.Font(os.path.join("fonts", "PG_Roof Runners_active.ttf"), 40)
    button_text = f.render("Restart", 1, (255,0,0))
    global restart_button
    restart_button = screen.blit(button_text, (20, 150))

    button_text = f.render("Quit Game", 1, (255,0,0))
    global leave_button
    leave_button = screen.blit(button_text, (20, 600))


def start_match():
    random.shuffle(board)

    for card in board:
        card.is_backward = True

    draw_menu()
    create_board()

    global score, match_start_time
    score = 0
    match_start_time = pygame.time.get_ticks()

    global how_many_pairs, match_time, match_is_running
    how_many_pairs = 0
    match_time = 0
    match_is_running = True


def write_game_data():
    f = pygame.font.Font(os.path.join("fonts", "PG_Roof Runners_active.ttf"), 40)
    text = f.render("Score: " + str(score), 1, (0, 0, 0))
    screen.blit(text, (20, 250, 30, 210))

    text = f.render("Time: " + str(match_time) + "s", 1, (0, 0, 0))
    screen.blit(text, (20, 350, 30, 210))


def create_board():
    current_index = 0
    for card in board:
        x = 300 + CARD_WIDTH * (current_index % 4) + 40 * (current_index % 4)
        y = 80 + CARD_HEIGHT * (current_index // 4) + 40 * (current_index // 4)
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

        card.set_rectangle(rect)
        cards_back = pygame.transform.scale(card_backward_image, (CARD_WIDTH, CARD_HEIGHT))
        screen.blit(cards_back, card.card_rectangle)
        current_index += 1


def click_handler(mouse_x, mouse_y):
    if leave_button.collidepoint(mouse_x, mouse_y):
        sys.exit()
    elif restart_button.collidepoint(mouse_x, mouse_y):
        start_match()
    else:
        for card in board:
            if card.card_rectangle.collidepoint(mouse_x, mouse_y) and card.is_backward:
                card.flip_card()

                animations.append(Animation(get_frames(card.card_name), card.card_rectangle))

                pygame.mixer.stop()
                flip_sound.play()

                current_pair.append(card)
                global is_wrong, score
                if len(current_pair) == 2:
                    if current_pair[0].card_name != current_pair[1].card_name:
                        global last_wrong_time
                        last_wrong_time = pygame.time.get_ticks()
                        is_wrong = True
                        score -= 5  
                    else: 
                        pygame.mixer.stop()
                        score_sound.play()
                        global how_many_pairs
                        is_wrong = False
                        score += 20
                        how_many_pairs += 1
                        current_pair.clear()
                        
                break

def get_frames(card_name):
    for i in range(0, len(IMAGES_NAME)):
        if card_name == IMAGES_NAME[i]:
            return frames[i]
    return None


def wrong_pair():
    pygame.mixer.stop()
    error_sound.play()

    card1 = current_pair[0]
    card2 = current_pair[1]

    current_pair[0].flip_card()
    current_pair[1].flip_card()

    animations.append(Animation(list(reversed(get_frames(card1.card_name))), card1.card_rectangle))
    animations.append(Animation(list(reversed(get_frames(card2.card_name))), card2.card_rectangle))

    current_pair.clear()
    global is_wrong, last_wrong_time
    is_wrong = False
    last_wrong_time = 0


def check_win():
    if how_many_pairs == 6:
        pygame.mixer.stop()
        victory_sound.play()
        global match_is_running
        match_is_running = False
        ctypes.windll.user32.MessageBoxW(0, "Congratulations! You won the game by making " + str(score) + " Point!", "Game End!", 1)


clock = pygame.time.Clock()
def run():
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not is_wrong and len(animations) < 2:
                clicked_x, clicked_y = pygame.mouse.get_pos()
                click_handler(clicked_x, clicked_y)
            
        time_now = pygame.time.get_ticks()

        clock.tick()
        global fps
        fps = int(clock.get_fps())
        draw_menu()

        if is_wrong and time_now - last_wrong_time >= 1000:
            wrong_pair()

        if match_is_running:
            global match_time
            match_time = (time_now - match_start_time) // 1000
            draw_menu()
        
        for anim in animations:
            new_frame = anim.update(time_now)
            if new_frame is not None:
                pygame.draw.rect(screen, (255, 255, 255), anim.rect)
                new_frame = pygame.transform.scale(new_frame, (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(new_frame, anim.rect)

            if anim.finished():
                animations.remove(anim)

        pygame.display.flip()

        if match_is_running:
            check_win()


start_match()
run()

