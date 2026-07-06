import pygame
from utils import load_gif_frames

class Settings:
    def __init__(self, display, width, height):
        self.display = display
        self.width = width
        self.height = height
        self.gif_frames, self.clip_duration = load_gif_frames("assets/Whack A Mole.gif")
        self.frame_index = 0
        self.font_menu = pygame.font.Font(None, 50)
        self.play_button_color = (50, 255, 100)
        self.selected_letters = {'A': True, 'B': True, 'C': True, 'E': True, 'I': True, 'L': True, 'M': True, 'N': True, 'O': True, 'P': True, 'R': True, 'S': True, 'T': True, 'U': True, 'W': True, 'Y': True}
        self.sound_enabled = True
        self.settings_rect = None

    def handle_event(self, mouse_x, mouse_y):
        if self.settings_rect.collidepoint(mouse_x, mouse_y):
            return 'menu'
        return 'settings'

    def update(self):
        self.frame_index = (self.frame_index + 1) % self.clip_duration

    def draw(self):
        surface = self.gif_frames[self.frame_index]
        self.display.blit(surface, (0, 0))
        settings_text = self.font_menu.render("Ustawienia", True, (0, 0, 0))
        play_text = self.font_menu.render("GRAJ", True, (255, 255, 255))

        button_width = 200
        button_height = 80

        self.settings_rect = pygame.Rect((self.width - button_width) // 2, self.height // 2, button_width, button_height)

        pygame.draw.rect(self.display, self.play_button_color, self.settings_rect, border_radius=10)
        pygame.draw.rect(self.display, (0, 0, 0), self.settings_rect, width=2, border_radius=10)

        settings_text_rect = settings_text.get_rect(center=self.settings_rect.center)
        self.display.blit(settings_text, settings_text_rect)
