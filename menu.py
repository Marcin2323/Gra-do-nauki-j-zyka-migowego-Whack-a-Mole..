import pygame
from utils import load_gif_frames

class Menu:
    def __init__(self, display, width, height):
        self.display = display
        self.width = width
        self.height = height
        self.gif_frames, self.clip_duration = load_gif_frames("assets/Whack A Mole.gif")
        self.frame_index = 0
        self.font_menu = pygame.font.Font(None, 50)
        self.play_button_color = (50, 255, 100)
        self.settings_button_color = (50, 255, 100)
        self.rank_button_color = (50, 255, 100)
        self.play_rect = None
        self.settings_rect = None
        self.rank_rect = None

    def handle_event(self, mouse_x, mouse_y):
        if self.play_rect.collidepoint(mouse_x, mouse_y):
            return 'game'
        elif self.settings_rect.collidepoint(mouse_x, mouse_y):
            return 'settings'
        elif self.rank_rect.collidepoint(mouse_x, mouse_y):
            return 'rank'
        return 'menu'

    def update(self):
        self.frame_index = (self.frame_index + 1) % self.clip_duration
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.play_rect and self.play_rect.collidepoint(mouse_x, mouse_y):
            self.play_button_color = (100, 255, 150)
        else:
            self.play_button_color = (50, 255, 100)
        if self.settings_rect and self.settings_rect.collidepoint(mouse_x, mouse_y):
            self.settings_button_color = (100, 255, 150)
        else:
            self.settings_button_color = (50, 255, 100)
        if self.rank_rect and self.rank_rect.collidepoint(mouse_x, mouse_y):
            self.rank_button_color = (100, 255, 150)
        else:
            self.rank_button_color = (50, 255, 100)

    def draw(self):
        surface = self.gif_frames[self.frame_index]
        self.display.blit(surface, (0, 0))
        play_text = self.font_menu.render("GRAJ", True, (255, 255, 255))
        settings_text = self.font_menu.render("Ustawienia", True, (0, 0, 0))
        rank_text = self.font_menu.render("Wyniki", True, (0, 0, 0))

        button_width = 200
        button_height = 80

        self.play_rect = pygame.Rect((self.width - button_width) // 2, self.height // 3, button_width, button_height)
        self.settings_rect = pygame.Rect((self.width - button_width) // 2, self.height // 2, button_width, button_height)
        self.rank_rect = pygame.Rect((self.width - button_width) // 2, 2 * self.height // 3, button_width, button_height)

        pygame.draw.rect(self.display, self.play_button_color, self.play_rect, border_radius=10)
        pygame.draw.rect(self.display, (0, 0, 0), self.play_rect, width=2, border_radius=10)
        pygame.draw.rect(self.display, self.settings_button_color, self.settings_rect, border_radius=10)
        pygame.draw.rect(self.display, (0, 0, 0), self.settings_rect, width=2, border_radius=10)
        pygame.draw.rect(self.display, self.rank_button_color, self.rank_rect, border_radius=10)
        pygame.draw.rect(self.display, (0, 0, 0), self.rank_rect, width=2, border_radius=10)

        play_text_rect = play_text.get_rect(center=self.play_rect.center)
        self.display.blit(play_text, play_text_rect)
        settings_text_rect = settings_text.get_rect(center=self.settings_rect.center)
        self.display.blit(settings_text, settings_text_rect)
        rank_text_rect = rank_text.get_rect(center=self.rank_rect.center)
        self.display.blit(rank_text, rank_text_rect)
