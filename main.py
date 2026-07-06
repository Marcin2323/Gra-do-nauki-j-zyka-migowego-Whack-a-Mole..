import tempfile
import pygame
import random
import sys
import moviepy.editor as mp
import threading
import os
import sqlite3
from datetime import datetime
import mod.main_models_v3
import importlib.util
file_path = r"\python_mediapipe\RawData.py"
module_name = "RawData"

spec = importlib.util.spec_from_file_location(module_name, file_path)
RawData = importlib.util.module_from_spec(spec)
sys.modules[module_name] = RawData
spec.loader.exec_module(RawData)

def get_persistent_path(filename):
    """Zwraca ścieżkę do trwałego folderu aplikacji w katalogu użytkownika."""
    base_path = os.path.expanduser("~")  # Katalog domowy użytkownika
    app_folder = os.path.join(base_path, ".whack_a_mole")  # Folder aplikacji
    os.makedirs(app_folder, exist_ok=True)  # Tworzy folder, jeśli nie istnieje
    return os.path.join(app_folder, filename)


def resource_path(relative_path):
    """Uzyska absolutną ścieżkę zasobu, działa także w plikach .exe."""
    try:
        base_path = sys._MEIPASS  # Folder tymczasowy dla PyInstaller
    except Exception:
        base_path = os.path.abspath(".")  # Lokalna ścieżka podczas testów
    return os.path.join(base_path, relative_path)

# Inicjalizacja Pygame
pygame.init()

# Tworzenie połączenia z bazą danych
conn = sqlite3.connect(get_persistent_path('my_database.db'))
c = conn.cursor()

# Tworzenie tabeli, jeśli nie istnieje
c.execute('''
    CREATE TABLE IF NOT EXISTS rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        score INTEGER,
        date TEXT,
        difficulty TEXT,
        num_letters INTEGER
    )
''')

# Wstawianie przykładowego rekordu
player_name = 'Marcin'
score = 100
date = '2024-10-18'
difficulty = 'easy'
num_letters = 3

# Zatwierdzenie zmian
conn.commit()

# Pobieranie wyników z bazy
c.execute('SELECT player_name, score, date FROM rankings ORDER BY score DESC')
rows = c.fetchall()

# Wyświetlanie wyników

# Zamknięcie połączenia
conn.close()

# Ustawienia ekranu
width, height = 800, 600
display = pygame.display.set_mode((width, height))
pygame.display.set_caption("Whack a Mole Game")
selected_num_letters = 16
difficulty_lvl = "łatwy"
difficulty_base = "easy"

# Inicjalizacja modułu muzyki
pygame.mixer.init()
# Ścieżka do pliku muzycznego
music_path = resource_path("dist/assets/m4.mp3")
# Załaduj muzykę
pygame.mixer.music.load(music_path)
# Ustawienie głośności (opcjonalnie, od 0.0 do 1.0)
pygame.mixer.music.set_volume(0.5)

# Załaduj dźwięk zabicia kreta
kill_sound = pygame.mixer.Sound(resource_path("dist/assets/kill2.mp3"))
# Opcjonalnie ustaw głośność dźwięku (od 0.0 do 1.0)
kill_sound.set_volume(0.7)

start_sound = pygame.mixer.Sound(resource_path("dist/assets/start.mp3"))
# Opcjonalnie ustaw głośność dźwięku (od 0.0 do 1.0)
start_sound.set_volume(0.7)

over_sound = pygame.mixer.Sound(resource_path("dist/assets/over.mp3"))
# Opcjonalnie ustaw głośność dźwięku (od 0.0 do 1.0)
over_sound.set_volume(0.7)

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Załaduj grafikę tła
background_image = pygame.image.load(resource_path("assets/tlo1.png"))
background_image = pygame.transform.scale(background_image, (width, height))

# Załaduj animowany plik GIF
clip = mp.VideoFileClip(resource_path("assets/Whack A Mole.gif"))
fps = clip.fps
gif_duration = clip.duration
clip_duration = int(gif_duration * fps)
gif_frames = [clip.get_frame(i / fps / 2) for i in range(clip_duration)]

# Załaduj ikony dźwięku
sound_enable = pygame.image.load(resource_path("assets/sound_enable.png"))
sound_disable = pygame.image.load(resource_path("assets/sound_disable.png"))

# Zmiana rozmiaru ikony, jeśli jest potrzebna (opcjonalnie)
sound_enable = pygame.transform.scale(sound_enable, (50, 50))
sound_disable = pygame.transform.scale(sound_disable, (50, 50))

# Ustawienia gry
score = 0
font = pygame.font.Font(None, 36)
font_menu = pygame.font.Font(None, 50)
font_diff = pygame.font.Font(None, 25)
clock = pygame.time.Clock()
difficulty = "easy"
selected_letters = {'A': True, 'B': True, 'C': True, 'E': True, 'I': True, 'L': True, 'M': True, 'N': True, 'O': True, 'P': True, 'R': True, 'S': True, 'T': True, 'U': True, 'W': True, 'Y': True}
sound_enabled = 0
show_hints = True
mole_lifetime = 3000
active_letters = ['A']
active_moles_count = 0
available_positions = [
    (width - 140, height - 100),
    (width - 140, height - 210),
    (width - 375, height - 100),
    (width - 375, height - 210),
    (width - 615, height - 100),
    (width - 615, height - 210),
]
occupied_positions = set()

save_score_mode = False
player_nickname = ""
end_time_score = 0
def load_settings_from_file(filename=get_persistent_path("settings.txt")):
    global difficulty, selected_letters, sound_enabled, mole_lifetime, show_hints

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split('=')

                if key == 'difficulty':
                    difficulty = value
                elif key == 'sound_enabled':
                    sound_enabled = int(value)
                elif key == 'show_hints':
                    show_hints = int(value)
                elif key == 'letters':
                    letter_pairs = value.split(',')
                    selected_letters = {}
                    for pair in letter_pairs:
                        letter, is_selected = pair.split('/')
                        selected_letters[letter] = is_selected == 'True'  # Ustawiamy stan litery
                if difficulty == 'easy':
                    mole_lifetime = 3000  # 3 seconds in milliseconds
                elif difficulty == 'medium':
                    mole_lifetime = 2000
                elif difficulty == 'hard':
                    mole_lifetime = 1000

    except FileNotFoundError:
        pass

def save_settings_to_file(filename=get_persistent_path("settings.txt")):
    with open(filename, 'w') as file:
        file.write(f'difficulty={difficulty}\n')
        if sound_enabled:
            file.write(f'sound_enabled=1\n')
        else:
            file.write(f'sound_enabled=0\n')
        file.write(f'show_hints={"1" if show_hints else "0"}\n')
        letters = ','.join([f'{letter}/{selected}' for letter, selected in selected_letters.items()])
        file.write(f'letters={letters}\n')


if difficulty == 'easy':
    mole_lifetime = 3000  # 3 seconds in milliseconds
elif difficulty == 'medium':
    mole_lifetime = 2000
elif difficulty == 'hard':
    mole_lifetime = 1000

# Klasa Circle reprezentująca kreta
class Circle:
    def __init__(self, filled, x, y, letter, is_gold=False):
        self.radius = 70
        self.x = x
        self.y = y
        self.filled = filled
        self.letter = letter
        self.is_gold = is_gold  # Flaga dla złotego kreta
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_time = pygame.time.get_ticks()

        # Wczytanie obrazków animacji jako lista
        base_path = "dist/assets/kret_zloty" if self.is_gold else "dist/assets/kret"
        self.frames = [
            pygame.image.load(resource_path(f"{base_path}{i}.png")) for i in range(1, 5)
        ]
        self.current_frame = 0  # Indeks bieżącej klatki
        self.frame_timer = pygame.time.get_ticks()  # Czas ostatniej zmiany klatki
        self.animation_finished = False  # Flaga końca animacji

    def draw(self):
        # Aktualizacja klatki animacji, jeśli animacja nie jest zakończona
        if not self.animation_finished:
            current_time = pygame.time.get_ticks()
            if current_time - self.frame_timer >= 50:  # Zmień klatkę co 200 ms
                self.current_frame += 1
                self.frame_timer = current_time

                # Sprawdzenie, czy animacja się zakończyła
                if self.current_frame >= len(self.frames):
                    self.current_frame = len(self.frames) - 1  # Zatrzymaj na ostatniej klatce
                    self.animation_finished = True

        # Pobranie bieżącej klatki
        frame = self.frames[self.current_frame]

        # Skalowanie obrazu
        frame = pygame.transform.scale(frame, (120, 120))

        # Rysowanie animacji
        image_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)
        display.blit(frame, image_rect)

        # Rysowanie litery nad kretem
        if self.filled:
            letter_path = pygame.image.load(resource_path(f"dist/assets/letters/{self.letter}.png"))
            letter_path = pygame.transform.scale(letter_path, (40, 40))
            letter_rect = letter_path.get_rect(center=(self.x - 10, self.y - self.radius - 20))
            display.blit(letter_path, letter_rect)

class Hammer:
    def __init__(self, x, y):
        self.frames = [
            pygame.image.load(resource_path(f"dist/assets/mlot{i}k.png")) for i in range(1, 5)
        ]
        self.current_frame = 0
        self.x = x
        self.y = y
        self.frame_timer = pygame.time.get_ticks()
        self.animation_finished = False

    def draw(self):
        # Jeśli animacja się zakończyła, nie rysujemy młotka
        if self.animation_finished:
            return

        # Wyświetl bieżącą klatkę
        frame = self.frames[self.current_frame]
        frame = pygame.transform.scale(frame, (150, 180))  # Skaluj klatkę, jeśli to konieczne
        display.blit(frame, (self.x, self.y))

        # Zmieniaj klatki animacji co 100 ms
        current_time = pygame.time.get_ticks()
        if current_time - self.frame_timer >= 50:  # 100 ms na klatkę
            self.current_frame += 1
            self.frame_timer = current_time

            # Jeśli to ostatnia klatka, oznacz animację jako zakończoną
            if self.current_frame >= len(self.frames):
                self.animation_finished = True


# Funkcja tworząca nowego kreta
def create_new_circle(active_letters, is_gold=False):
    global active_moles_count, available_positions, occupied_positions

    if active_moles_count >= 3 or not available_positions:  # Maksymalnie 3 krety i sprawdzenie dostępnych pozycji
        return None

    # Losowanie pozycji spośród dostępnych
    position = random.choice(available_positions)
    available_positions.remove(position)  # Usuń wybraną pozycję z listy dostępnych
    occupied_positions.add(position)  # Dodaj pozycję do zajętych

    x, y = position
    letter = random.choice(active_letters)
    is_gold = random.random() < 0.1  # 10% szans na złotego kreta
    active_moles_count += 1  # Zwiększ licznik aktywnych kretów
    return Circle(True, x, y, letter, is_gold)


# Lista liter dla krety
letters = ['A', 'B', 'C', 'E', 'I', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'Y']
circles = []
hammers = []  # Lista młotków
circles.append(create_new_circle(active_letters))


# Funkcja konwertująca klatkę na obiekt Surface
def frame_to_surface(frame):
    return pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")


def remove_circle(circle):
    global active_moles_count, available_positions, occupied_positions
    if circle:
        position = (circle.x, circle.y)
        if position in occupied_positions:
            occupied_positions.remove(position)  # Usuń pozycję z zajętych
            available_positions.append(position)  # Dodaj pozycję z powrotem do dostępnych
        circles.remove(circle)  # Usuń kreta z listy
        active_moles_count -= 1  # Zmniejsz licznik aktywnych kretów

# Funkcja rysująca menu z przyjemniejszym wyglądem przycisku "GRAJ"
def draw_menu(frame_index, play_button_color, settings_button_color, rank_button_color):
    surface = frame_to_surface(gif_frames[frame_index])
    display.blit(surface, (0, 0))

    # Tekst przycisków
    if camera_ready:
        play_text = font_menu.render("GRAJ", True, WHITE)
    else:
        play_text = font_diff.render("ŁĄCZENIE Z KAMERĄ", True, WHITE)

    settings_text = font_menu.render("Ustawienia", True, BLACK)
    rank_text = font_menu.render("Wyniki", True, BLACK)

    # Nowa wielkość przycisków
    button_width = 200
    button_height = 80

    # Nowe położenie przycisków
    play_rect = pygame.Rect((width - button_width) // 2, height // 3, button_width, button_height)
    settings_rect = pygame.Rect((width - button_width) // 2, height // 2, button_width, button_height)
    rank_rect = pygame.Rect((width - button_width) // 2, 2 * height // 3, button_width, button_height)

    if camera_ready:
        noplay_button_color = play_button_color
    else:
        noplay_button_color = (200, 200, 200)
    # Rysowanie przycisków z efektami
    pygame.draw.rect(display, noplay_button_color, play_rect, border_radius=10)  # Prostokąt z zaokrąglonymi narożnikami
    pygame.draw.rect(display, BLACK, play_rect, width=2, border_radius=10)  # Obramowanie
    pygame.draw.rect(display, settings_button_color, settings_rect, border_radius=10)  # Prostokąt z zaokrąglonymi narożnikami
    pygame.draw.rect(display, BLACK, settings_rect, width=2, border_radius=10)  # Obramowanie
    pygame.draw.rect(display, rank_button_color, rank_rect, border_radius=10)  # Prostokąt z zaokrąglonymi narożnikami
    pygame.draw.rect(display, BLACK, rank_rect, width=2, border_radius=10)  # Obramowanie

    # Wyśrodkowanie tekstu "GRAJ"
    play_text_rect = play_text.get_rect(center=play_rect.center)
    display.blit(play_text, play_text_rect)

    settings_text_rect = settings_text.get_rect(center=settings_rect.center)
    display.blit(settings_text, settings_text_rect)

    rank_text_rect = rank_text.get_rect(center=rank_rect.center)
    display.blit(rank_text, rank_text_rect)

    return play_rect, settings_rect, rank_rect   # Zwracamy prostokąt obszaru "GRAJ"


def draw_save_score_window():
    display.fill(WHITE)  # Tło okna
    save_font = pygame.font.Font(None, 50)
    input_font = pygame.font.Font(None, 36)

    # Tytuł
    title_text = save_font.render("Zapisz swój wynik!", True, BLACK)
    title_rect = title_text.get_rect(center=(width // 2, 100))
    display.blit(title_text, title_rect)

    # Pole wprowadzania nicku
    nickname_prompt = input_font.render("Twój nick:", True, BLACK)
    nickname_prompt_rect = nickname_prompt.get_rect(topleft=(width // 4, 200))
    display.blit(nickname_prompt, nickname_prompt_rect)

    nickname_input = input_font.render(player_nickname, True, BLACK)
    input_rect = pygame.Rect(width // 4 + 150, 200, 300, 40)
    pygame.draw.rect(display, BLACK, input_rect, 2)
    display.blit(nickname_input, input_rect.topleft)

    # Przycisk zapisu
    save_button = pygame.Rect((width - 200) // 2, 300, 200, 50)
    pygame.draw.rect(display, (50, 255, 100), save_button, border_radius=10)
    pygame.draw.rect(display, BLACK, save_button, width=2, border_radius=10)

    save_text = save_font.render("Zapisz", True, WHITE)
    save_text_rect = save_text.get_rect(center=save_button.center)
    display.blit(save_text, save_text_rect)

    return save_button, input_rect


def draw_settings_mode(frame_index, play_button_color, difficulty, selected_letters, sound_enabled, show_hints):
    surface = frame_to_surface(gif_frames[frame_index])
    display.blit(surface, (0, 0))

    # Tekst przycisków
    settings_text = font_menu.render("Ustawienia", True, BLACK)
    difficulty_text = font_menu.render("Poziom trudności:", True, BLACK)
    letters_text = font_menu.render("Wybierz litery:", True, BLACK)
    sound_text = font_menu.render("Dźwięk:", True, BLACK)
    menu_text = font_menu.render("Menu", True, WHITE)

    # Nowa wielkość przycisków
    button_width = 200
    button_height = 80

    # Nowe położenie przycisków
    settings_rect = pygame.Rect((width - button_width) // 2, height - 550, button_width, button_height)
    easy_rect = pygame.Rect((width-250 - button_width) // 4, height - 450, button_width, button_height)
    medium_rect = pygame.Rect((width - button_width) // 2, height - 450, button_width, button_height)
    hard_rect = pygame.Rect((width - button_width)-90, height - 450, button_width, button_height)
    sound_checkbox_rect = pygame.Rect((width - button_width)-184, height -170, 60, 60)
    menu_rect = pygame.Rect((width - button_width)-20, height-200, button_width, button_height)

    # Rysowanie przycisków z efektami
    pygame.draw.rect(display, play_button_color, settings_rect, border_radius=10)  # Prostokąt z zaokrąglonymi narożnikami
    pygame.draw.rect(display, BLACK, settings_rect, width=2, border_radius=10)  # Obramowanie
    pygame.draw.rect(display, play_button_color, menu_rect,border_radius=10)  # Prostokąt z zaokrąglonymi narożnikami
    pygame.draw.rect(display, BLACK, menu_rect, width=2, border_radius=10)
    pygame.draw.rect(display, BLACK, easy_rect, 2, border_radius=10)
    pygame.draw.rect(display, BLACK, medium_rect, 2, border_radius=10)
    pygame.draw.rect(display, BLACK, hard_rect, 2, border_radius=10)
    pygame.draw.rect(display, BLACK, sound_checkbox_rect, 2, border_radius=10)

    # Wyśrodkowanie tekstu "Ustawienia"
    settings_text_rect = settings_text.get_rect(center=settings_rect.center)
    display.blit(settings_text, settings_text_rect)

    mouse_x, mouse_y = pygame.mouse.get_pos()


    # Wybór poziomu trudności
    if difficulty == "easy":
        easy_color = BLACK
    elif easy_rect.collidepoint(mouse_x, mouse_y):
        easy_color = (100, 255, 150)
    else:
        easy_color = (100, 100, 100)
    if difficulty == "medium":
        medium_color = BLACK
    elif medium_rect.collidepoint(mouse_x, mouse_y):
        medium_color = (100, 255, 150)
    else:
        medium_color = (100, 100, 100)
    if difficulty == "hard":
        hard_color = BLACK
    elif hard_rect.collidepoint(mouse_x, mouse_y):
        hard_color = (100, 255, 150)
    else:
        hard_color = (100, 100, 100)

    # Renderowanie tekstu z odpowiednim kolorem dla każdego poziomu trudności
    easy_text = font_menu.render("Łatwy", True, easy_color)
    easy_text_rect = easy_text.get_rect(center=easy_rect.center)
    display.blit(easy_text, easy_text_rect)

    medium_text = font_menu.render("Średni", True, medium_color)
    medium_text_rect = medium_text.get_rect(center=medium_rect.center)
    display.blit(medium_text, medium_text_rect)

    hard_text = font_menu.render("Trudny", True, hard_color)
    hard_text_rect = hard_text.get_rect(center=hard_rect.center)
    display.blit(hard_text, hard_text_rect)

    font_letters_setting = pygame.font.Font(None, 30)
    # Wybór liter
    y_offset = (height-20) // 2
    x_offset = (width - button_width*2) // 2  # Początkowy odstęp od lewej krawędzi
    checkbox_rects = {}
    for letter, selected in selected_letters.items():
        if letter == 'O':  # Po literze 'L' zmień kolumnę
            x_offset += 50
            y_offset = (height-20) // 2  # Resetowanie y_offset do początku nowej kolumny

        checkbox_rect = pygame.Rect(x_offset, y_offset, 25, 25)
        checkbox_rects[letter] = checkbox_rect
        pygame.draw.rect(display, BLACK, checkbox_rect, 3, border_radius=3)

        if selected:
            pygame.draw.rect(display, BLACK, checkbox_rect.inflate(-10, -10))

        checkbox_text = font_letters_setting.render(letter, True, WHITE,)
        checkbox_text_rect = checkbox_text.get_rect(center=checkbox_rect.center)
        display.blit(checkbox_text, checkbox_text_rect)

        y_offset += button_height - 50  # Przesuwaj się w dół



    # Dźwięk
    sound_checkbox_text = display.blit(sound_enable, sound_checkbox_rect) if sound_enabled else display.blit(sound_disable, sound_checkbox_rect)

    # Menu
    menu_text_rect = font_menu.render("MENU", True, BLACK)
    menu_rect = menu_text_rect.get_rect(center=menu_rect.center)
    display.blit(menu_text_rect, menu_rect)

    # Tekst "Podpowiedzi"


    # Przyciski
    hints_rect = pygame.Rect(width // 2, height - 290, button_width / 2, button_height / 2)
    pygame.draw.rect(display, (50, 255, 100) if show_hints else (200, 100, 100), hints_rect, border_radius=10)
    pygame.draw.rect(display, BLACK, hints_rect, width=2, border_radius=10)

    hints_label_text = font_diff.render("Podpowiedzi", True, BLACK)
    hints_label_rect = hints_label_text.get_rect(
        center=(hints_rect.centerx, hints_rect.top - 20))  # Pozycja nad przyciskiem
    display.blit(hints_label_text, hints_label_rect)

    # Status przycisku
    hints_status_text = font_diff.render("Włączone" if show_hints else "Wyłączone", True, WHITE)
    hints_status_rect = hints_status_text.get_rect(center=hints_rect.center)
    display.blit(hints_status_text, hints_status_rect)

    return settings_rect, easy_rect, medium_rect, hard_rect, sound_checkbox_rect, menu_rect, checkbox_rects, hints_status_rect


def spawn_additional_moles(circles, active_letters):
    if len(circles) < 3:
        # Losowanie kolejnego kreta
        if len(circles) == 1 and random.random() < 0.5:  # 50% szans na drugiego
            pygame.time.set_timer(pygame.USEREVENT + 1, random.randint(500, 1500))
        elif len(circles) == 2 and random.random() < 0.3:  # 30% szans na trzeciego
            pygame.time.set_timer(pygame.USEREVENT + 1, random.randint(500, 1500))

def draw_rank_mode(frame_index, selected_num_letters):
    surface = frame_to_surface(gif_frames[frame_index])
    display.blit(surface, (0, 0))

    display.fill(WHITE)  # Tło dla trybu rankingu

    # Nagłówek
    title_text = font_menu.render("Tabela wyników", True, BLACK)
    title_rect = title_text.get_rect(center=(width // 2, 50))
    display.blit(title_text, title_rect)

    # Wyświetlanie liczby liter z przyciskami strzałek
    arrow_font = pygame.font.Font(None, 30)
    num_letters_text = font.render("Liczba liter", True, BLACK)
    num_letters_text_rect = num_letters_text.get_rect(topleft=(10, 10))
    display.blit(num_letters_text, num_letters_text_rect)

    # Przycisk strzałki w lewo
    arrow_left_rect = pygame.Rect(150, 10, 30, 30)
    pygame.draw.rect(display, (50, 255, 100), arrow_left_rect, border_radius=10)
    arrow_left_text = arrow_font.render("<", True, WHITE)
    arrow_left_text_rect = arrow_left_text.get_rect(center=arrow_left_rect.center)
    pygame.draw.rect(display, BLACK, arrow_left_rect, width=2, border_radius=10)
    display.blit(arrow_left_text, arrow_left_text_rect)

    # Wyświetlanie liczby liter
    num_letters_value_text = font_diff.render(str(selected_num_letters), True, BLACK)
    num_letters_value_rect = num_letters_value_text.get_rect(center=(200, 25))
    display.blit(num_letters_value_text, num_letters_value_rect)

    # Przycisk strzałki w prawo
    arrow_right_rect = pygame.Rect(220, 10, 30, 30)
    pygame.draw.rect(display, (50, 255, 100), arrow_right_rect, border_radius=10)
    arrow_right_text = arrow_font.render(">", True, WHITE)
    arrow_right_text_rect = arrow_right_text.get_rect(center=arrow_right_rect.center)
    pygame.draw.rect(display, BLACK, arrow_right_rect, width=2, border_radius=10)
    display.blit(arrow_right_text, arrow_right_text_rect)

    difficulty_lvl_text = font.render("Trudność", True, BLACK)
    difficulty_lvl_text_rect = difficulty_lvl_text.get_rect(topleft=(10, 50))
    display.blit(difficulty_lvl_text, difficulty_lvl_text_rect)

    # Przycisk strzałki w lewo
    arrow_left_rect2 = pygame.Rect(140, 50, 30, 30)
    pygame.draw.rect(display, (50, 255, 100), arrow_left_rect2, border_radius=10)
    arrow_left_text2 = arrow_font.render("<", True, WHITE)
    arrow_left_text_rect2 = arrow_left_text2.get_rect(center=arrow_left_rect2.center)
    pygame.draw.rect(display, BLACK, arrow_left_rect2, width=2, border_radius=10)
    display.blit(arrow_left_text2, arrow_left_text_rect2)

    difficulty_lvl_value_text = font_diff.render(str(difficulty_lvl), True, BLACK)
    difficulty_lvl_value_rect = difficulty_lvl_value_text.get_rect(center=(200, 65))
    display.blit(difficulty_lvl_value_text, difficulty_lvl_value_rect)

    # Przycisk strzałki w prawo
    arrow_right_rect2 = pygame.Rect(230, 50, 30, 30)
    pygame.draw.rect(display, (50, 255, 100), arrow_right_rect2, border_radius=10)
    arrow_right_text2 = arrow_font.render(">", True, WHITE)
    arrow_right_text_rect2 = arrow_right_text2.get_rect(center=arrow_right_rect2.center)
    pygame.draw.rect(display, BLACK, arrow_right_rect2, width=2, border_radius=10)
    display.blit(arrow_right_text2, arrow_right_text_rect2)

    # Połączenie z bazą danych i pobranie wyników dla wybranej liczby liter
    conn = sqlite3.connect(get_persistent_path("my_database.db"))
    c = conn.cursor()
    c.execute(
        'SELECT player_name, score, date FROM rankings WHERE num_letters = ? AND difficulty = ? ORDER BY score DESC',
        (selected_num_letters, difficulty_base)
    )
    rows = c.fetchall()
    conn.close()

    # Wyświetlanie wyników w tabeli
    header_font = pygame.font.Font(None, 36)
    row_font = pygame.font.Font(None, 28)
    headers = ["Gracz", "Wynik", "Data"]
    x_offsets = [150, 400, 600]
    y_start = 100
    y_offset = 40

    # Wyświetlanie nagłówków kolumn
    for i, header in enumerate(headers):
        header_text = header_font.render(header, True, BLACK)
        display.blit(header_text, (x_offsets[i], y_start))

    # Wyświetlanie wierszy z wynikami
    for idx, row in enumerate(rows[:9]):  # Wyświetl maksymalnie 10 wyników
        for i, value in enumerate(row):
            row_text = row_font.render(str(value), True, BLACK)
            display.blit(row_text, (x_offsets[i], y_start + y_offset * (idx + 1)))

    # Przycisk powrotu do menu
    menu_button_color = (50, 255, 100)
    button_width, button_height = 200, 60
    menu_rect = pygame.Rect((width - button_width) // 2, height - 100, button_width, button_height)
    pygame.draw.rect(display, menu_button_color, menu_rect, border_radius=10)
    pygame.draw.rect(display, BLACK, menu_rect, width=2, border_radius=10)

    # Tekst przycisku "Menu"
    menu_text = font_menu.render("Menu", True, WHITE)
    menu_text_rect = menu_text.get_rect(center=menu_rect.center)
    display.blit(menu_text, menu_text_rect)

    # Zwracanie prostokątów przycisków
    return menu_rect, arrow_left_rect, arrow_right_rect, arrow_left_rect2, arrow_right_rect2


# Funkcja rysująca czas na górze ekranu
def draw_timer(time_left):
    timer_text = font.render(f"Czas: {time_left//1000} sek", True, WHITE)
    display.blit(timer_text, (620, 10))


def read_predicted_label():
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'predicted_label.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if lines:
            predicted_label = lines[0].strip()  # Read the last line
            camera_ready = int(lines[1].strip())  # Drugi wiersz
            return predicted_label
    except FileNotFoundError:
        pass
    return None


process_b = None


def reset_game():
    global active_moles_count, available_positions, occupied_positions, circles
    active_moles_count = 0
    occupied_positions.clear()
    available_positions = [
        (width - 140, height - 100),
        (width - 140, height - 210),
        (width - 375, height - 100),
        (width - 375, height - 210),
        (width - 615, height - 100),
        (width - 615, height - 210),
    ]
    circles = []
    circles.append(create_new_circle(active_letters))


def uruchom_project_b():
    global process_b
    #project_path = os.path.dirname(os.path.abspath(__file__))

    # Tworzenie pełnej ścieżki do pliku 'main_models_v3.py'
    #script_path = os.path.join(project_path, 'python_mediapipe', 'main_models_v3.py')

    # Uruchamianie skryptu przy pomocy subprocess
    #process_b = subprocess.Popen(["python", script_path])
    process_b = mod.main_models_v3.runRealTime()



def check_camera():
    global camera_ready
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'predicted_label.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if lines:
            camera_ready = int(lines[1].strip())  # Drugi wiersz
    except FileNotFoundError:
        pass

def camera_off():
    global camera_ready
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'predicted_label.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n0")
        camera_ready = 0

import psutil

def terminate_process(process):
    """Zamyka proces główny i wszystkie procesy potomne."""
    try:
        if process and psutil.pid_exists(process.pid):
            proc = psutil.Process(process.pid)
            for child in proc.children(recursive=True):  # Zamknij procesy potomne
                child.terminate()
            proc.terminate()  # Zamknij proces główny
            proc.wait(timeout=3)
        else:
            pass
    except psutil.NoSuchProcess:
        pass
    except Exception as e:
        pass

# Pętla główna gry
menu_mode = True
game_mode = False
settings_mode = False
rank_mode = False
frame_index = 0
camera_ready = 0
camera_off()
# Kolor przycisku "GRAJ"
play_button_color = (50, 255, 100)
noplay_button_color = (200, 200, 200)
settings_button_color = (50, 255, 100)
rank_button_color = (50, 255, 100)

play_rect = draw_menu(frame_index, play_button_color, settings_button_color, rank_button_color)  # Pobieramy prostokąt obszaru "GRAJ"
settings_rect = draw_settings_mode(frame_index, play_button_color, difficulty, selected_letters, sound_enabled, show_hints)
rank_rect = draw_rank_mode(frame_index, selected_num_letters)

# Inicjalizacja zmiennej start_time
start_time = None
new_kret = False
round_time = 120000  # 2 minuty w milisekundach
NEW_MOLE_EVENT = pygame.USEREVENT + 1

perfect_image = pygame.image.load(resource_path(f"assets/perfect.png")).convert_alpha()
perfect_image = pygame.transform.scale(perfect_image, (227, 93))
perfect_image_rect = perfect_image.get_rect()
perfect_image_rect.topleft = (280, 80)

great_image = pygame.image.load(resource_path(f"assets/great.png")).convert_alpha()
great_image = pygame.transform.scale(great_image, (227, 93))
great_image_rect = great_image.get_rect()
great_image_rect.topleft = (280, 80)


perfect_image_start_time = None
great_image_start_time = None
image_display_duration = 2000  # 2 sekundy

spawn1 = False
spawn2 = False


if __name__ == '__main__':
    # Uruchomienie procesu do projektu B
    t = threading.Thread(target=uruchom_project_b)
    t.daemon = True
    t.start()
    load_settings_from_file()
    active_letters = [letter for letter, is_selected in selected_letters.items() if is_selected]
    if sound_enabled:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()
    while True:
        check_camera()
        # Obsługa zdarzeń Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate_process(process_b)
                process_b = None
                pygame.quit()
                camera_off()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_mode:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if play_rect[0].collidepoint(mouse_x, mouse_y) and camera_ready:
                        start_sound.play()
                        menu_mode = False
                        game_mode = True
                        start_time = pygame.time.get_ticks()  # Inicjalizuj start_time tutaj
                    elif play_rect[1].collidepoint(mouse_x, mouse_y):
                        menu_mode = False
                        settings_mode = True
                        if settings_rect[5].collidepoint(mouse_x, mouse_y):
                            menu_mode = True
                            settings_mode= False
                    elif play_rect[2].collidepoint(mouse_x, mouse_y):
                        menu_mode = False
                        rank_mode = True
                # Obsługa interakcji w grze
                elif game_mode:
                    if start_time is not None:
                        elapsed_time = pygame.time.get_ticks() - start_time
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        clicked_circle = None
                        for circle in circles:
                            distance = ((mouse_x - circle.x) ** 2 + (mouse_y - circle.y) ** 2) ** 0.5
                            if distance <= circle.radius and circle.filled:
                                clicked_circle = circle
                                break
                        if clicked_circle:
                            hammers.append(
                                Hammer(clicked_circle.x - 70, clicked_circle.y- 134))  # Dopasuj pozycję młotka
                            kill_sound.play()
                            available_positions.append((clicked_circle.x, clicked_circle.y))
                            remove_circle(clicked_circle)
                            if clicked_circle.is_gold:
                                if current_time - circle.last_spawn_time < mole_lifetime // 2:
                                    score += 6
                                else:
                                    score += 3
                            else:
                                if current_time - circle.last_spawn_time < mole_lifetime // 2:
                                    score += 2
                                else:
                                    score += 1
                            if active_moles_count == 0 and available_positions:  # Dodaj nowego kreta tylko, gdy są dostępne pozycje
                                new_circle = create_new_circle(active_letters)
                                circles.append(new_circle)
                                if active_moles_count == 1 and random.random() < 0.3:
                                    spawn1 = True
                            if spawn1 is True:
                                spawn1 = False
                                new_circle = create_new_circle(active_letters)
                                circles.append(new_circle)
                                if active_moles_count == 2 and random.random() < 0.1:
                                    spawn2 = True
                            if spawn2 is True:
                                spawn2 = False
                                new_circle = create_new_circle(active_letters)
                                circles.append(new_circle)
                elif settings_mode:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if settings_rect[1].collidepoint(mouse_x, mouse_y):
                        difficulty = 'easy'
                    elif settings_rect[2].collidepoint(mouse_x, mouse_y):
                        difficulty = 'medium'
                    elif settings_rect[3].collidepoint(mouse_x, mouse_y):
                        difficulty = 'hard'
                    elif settings_rect[4].collidepoint(mouse_x, mouse_y):
                        sound_enabled = not sound_enabled
                        if sound_enabled:
                            pygame.mixer.music.play(-1)
                        else:
                            pygame.mixer.music.stop()
                    elif settings_rect[7].collidepoint(mouse_x, mouse_y):
                        show_hints = not show_hints
                    elif settings_rect[5].collidepoint(mouse_x, mouse_y):
                        if len(active_letters) >= 3:
                            save_settings_to_file()
                            load_settings_from_file()
                            menu_mode = True
                            settings_mode = False
                    for letter, checkbox_rect in settings_rect[6].items():
                        if checkbox_rect.collidepoint(mouse_x, mouse_y):
                            # Zmieniamy stan litery z True na False i odwrotnie
                            selected_letters[letter] = not selected_letters[letter]
                            active_letters = [letter for letter, is_selected in selected_letters.items() if is_selected]
                elif rank_mode:
                    if rank_mode:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if rank_rect[0].collidepoint(mouse_x, mouse_y):
                            rank_mode = False
                            menu_mode = True
                        elif rank_rect[1].collidepoint(mouse_x, mouse_y):  # Strzałka w lewo
                            selected_num_letters = max(3, selected_num_letters - 1)  # Minimalna liczba liter to 1
                        elif rank_rect[2].collidepoint(mouse_x, mouse_y):  # Strzałka w prawo
                            selected_num_letters = min(16, selected_num_letters + 1)  # Zwiększ liczbę liter
                        elif rank_rect[3].collidepoint(mouse_x, mouse_y):  # Strzałka w lewo
                            if difficulty_lvl == "średni":
                                difficulty_lvl = "łatwy"
                                difficulty_base ="easy"
                            elif difficulty_lvl == "trudny":
                                difficulty_lvl = "średni"
                                difficulty_base = "mid"
                        elif rank_rect[4].collidepoint(mouse_x, mouse_y):  # Strzałka w prawo
                            if difficulty_lvl == "łatwy":
                                difficulty_lvl = "średni"
                                difficulty_base = "mid"
                            elif difficulty_lvl == "średni":
                                difficulty_lvl = "trudny"
                                difficulty_base = "hard"
                elif save_score_mode:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if save_button.collidepoint(mouse_x, mouse_y):
                        # Zapisujemy wynik do bazy danych

                        current_date = datetime.now().strftime('%Y-%m-%d')

                        conn = sqlite3.connect(get_persistent_path('my_database.db'))
                        c = conn.cursor()
                        c.execute(
                            'INSERT INTO rankings (player_name, score, date, difficulty, num_letters) VALUES (?, ?, ?, ?, ?)',
                            (player_nickname, end_time_score, current_date, difficulty, len(active_letters)))
                        conn.commit()
                        conn.close()

                        # Resetujemy zmienne i wracamy do menu
                        player_nickname = ""
                        score = 0
                        save_score_mode = False
                        menu_mode = True
            elif event.type == pygame.KEYDOWN:
                if save_score_mode:
                    if event.key == pygame.K_BACKSPACE:
                        player_nickname = player_nickname[:-1]  # Usuń ostatni znak
                    else:
                        player_nickname += event.unicode  # Dodaj znak
                elif game_mode:
                    if event.key == pygame.K_ESCAPE:
                        reset_game()
                        menu_mode = True
                        game_mode = False
                        score = 0
            elif event.type == pygame.USEREVENT + 1:  # Zdarzenie dla nowego kreta
                circles.append(create_new_circle(active_letters))
                spawn_additional_moles(circles, active_letters)
            elif event.type == NEW_MOLE_EVENT:
                if active_moles_count < 3 and available_positions:  # Dodaj nowego kreta tylko, gdy są dostępne pozycje
                    new_circle = create_new_circle(active_letters)
                    if new_circle:
                        circles.append(new_circle)

                # Ustaw losowe opóźnienie dla kolejnego zdarzenia
                pygame.time.set_timer(NEW_MOLE_EVENT, random.randint(1000, 2000))  # 1–2 sekundy

        if menu_mode:
            frame_index = (frame_index + 1) % clip_duration  # Przechodź do następnej klatki animacji

            # Zmiana koloru przycisku "GRAJ" i "Ustawienia" w zależności od położenia myszki
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if play_rect[0].collidepoint(mouse_x, mouse_y):
                # Myszka nad przyciskiem "GRAJ"
                play_button_color = (100, 255, 150)  # Nowy kolor przycisku "GRAJ"
            else:
                # Myszka poza przyciskiem "GRAJ"
                play_button_color = (50, 255, 100)  # Kolor przycisku "GRAJ" po najechaniu myszką

            if play_rect[1].collidepoint(mouse_x, mouse_y):
                # Myszka nad przyciskiem "Ustawienia"
                settings_button_color = (100, 255, 150)  # Nowy kolor przycisku "Ustawienia"
            else:
                # Myszka poza przyciskiem "Ustawienia"
                settings_button_color = (50, 255, 100)  # Kolor przycisku "Ustawienia" po najechaniu myszką
            if play_rect[2].collidepoint(mouse_x, mouse_y):
                # Myszka nad przyciskiem "Wyniki"
                rank_button_color = (100, 255, 150)  # Nowy kolor przycisku "Wyniki"
            else:
                # Myszka poza przyciskiem "Wyniki"
                rank_button_color = (50, 255, 100)  # Kolor przycisku "Wyniki" po najechaniu myszką
            play_rect = draw_menu(frame_index, play_button_color, settings_button_color, rank_button_color)  # Rysujemy menu

        elif game_mode:

            display.blit(background_image, (0, 0))  # Umieść grafikę tła na powierzchni okna

            for circle in circles:
                circle.draw()
            for hammer in hammers[:]:
                hammer.draw()
                if hammer.animation_finished:
                    hammers.remove(hammer)
            score_text = font.render(f"Punkty: {score}", True, WHITE)
            # Punkty programu
            display.blit(score_text, (10, 10))
            if show_hints:
                letter_image = pygame.image.load(resource_path(f"assets/gesty/{circle.letter}.png")).convert_alpha()
                letter_image_rect = letter_image.get_rect()
                letter_image_rect.topleft = (10, 55)  # Pozycja podpowiedzi
                display.blit(letter_image, letter_image_rect)
            # Odliczanie czasu
            if start_time is not None:
                time_elapsed = pygame.time.get_ticks() - start_time
                time_left = round_time - time_elapsed
                if perfect_image_start_time and pygame.time.get_ticks() - perfect_image_start_time < image_display_duration:
                    display.blit(perfect_image, perfect_image_rect)
                elif great_image_start_time and pygame.time.get_ticks() - great_image_start_time < image_display_duration:
                    display.blit(great_image, great_image_rect)
                if time_left <= 0:
                    # Koniec czasu, wróć do menu głównego
                    end_time_score = score
                    reset_game()
                    save_score_mode = True
                    game_mode = False
                    over_sound.play()
                else:
                    draw_timer(time_left)
                    # Check if any mole has been on screen for more than mole_lifetime
                    current_time = pygame.time.get_ticks()
                    for circle in circles:

                        if circle.filled and current_time - circle.last_spawn_time > mole_lifetime:
                            # Mole has been on screen for too long, create a new one
                            remove_circle(circle)
                            if active_moles_count == 0 and available_positions:  # Dodaj nowego kreta tylko, gdy są dostępne pozycje
                                new_circle = create_new_circle(active_letters)
                                circles.append(new_circle)
                                if active_moles_count == 1 and random.random() < 0.3:
                                    spawn1 = True
                            if spawn1 is True:
                                spawn1 = False
                                new_circle = create_new_circle(active_letters)
                                circles.append(new_circle)
                                if active_moles_count == 2 and random.random() < 0.1:
                                    spawn2 = True
                            if spawn2 is True:
                                spawn2 = False
                                new_circle = create_new_circle(active_letters)
                                circles.append(new_circle)
                            break
            # Sprawdzenie, czy w pliku jest nowa litera
            predicted_label = read_predicted_label()

            if predicted_label:
                for circle in circles:
                    if circle.filled and circle.letter == predicted_label:
                        current_time = pygame.time.get_ticks()
                        time_since_spawn = current_time - circle.spawn_time
                        hammers.append(Hammer(circle.x - 70, circle.y - 134))  # Dopasuj pozycję młotka
                        kill_sound.play()
                        if circle.is_gold:
                            if current_time - circle.spawn_time < mole_lifetime // 2:
                                score += 6
                                perfect_image_start_time = pygame.time.get_ticks()  # Rozpocznij wyświetlanie perfect_image
                                great_image_start_time = None
                            else:
                                score += 3
                                great_image_start_time = pygame.time.get_ticks()  # Rozpocznij wyświetlanie great_image
                                perfect_image_start_time = None
                        else:
                            if current_time - circle.last_spawn_time < mole_lifetime // 2:
                                score += 2
                                perfect_image_start_time = pygame.time.get_ticks()  # Rozpocznij wyświetlanie perfect_image
                                great_image_start_time = None
                            else:
                                score += 1
                                great_image_start_time = pygame.time.get_ticks()  # Rozpocznij wyświetlanie great_image
                                perfect_image_start_time = None
                        remove_circle(circle)
                        last_letter = circle.letter
                        active_letters.remove(circle.letter)
                        if active_moles_count == 0 and available_positions:  # Dodaj nowego kreta tylko, gdy są dostępne pozycje
                            new_circle = create_new_circle(active_letters)
                            circles.append(new_circle)
                            if active_moles_count == 1 and random.random() < 0.3:
                                spawn1 = True
                        if spawn1 is True:
                            spawn1 = False
                            new_circle = create_new_circle(active_letters)
                            circles.append(new_circle)
                            if active_moles_count == 2 and random.random() < 0.1:
                                spawn2 = True
                        if spawn2 is True:
                            spawn2 = False
                            new_circle = create_new_circle(active_letters)
                            circles.append(new_circle)
                        active_letters.append(last_letter)
                        break
        elif settings_mode:
            frame_index = (frame_index + 1) % clip_duration  # Przechodź do następnej klatki animacji

            # Zmiana koloru przycisku "GRAJ" w zależności od położenia myszki
            mouse_x, mouse_y = pygame.mouse.get_pos()
            settings_rect = draw_settings_mode(frame_index, play_button_color, difficulty, selected_letters, sound_enabled, show_hints)  # Rysujemy menu
        elif rank_mode:
            frame_index = (frame_index + 1) % clip_duration  # Przechodź do następnej klatki animacji
            rank_rect = draw_rank_mode(frame_index, selected_num_letters)
        elif save_score_mode:
            save_button, input_rect = draw_save_score_window()
        # Sprawdź czy gra się zakończyła
        # Aktualizacja ekranu
        pygame.display.flip()

        # Ustawienie liczby klatek na sekundę
        clock.tick(60)
