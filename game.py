import pygame
import random
from circle import Circle
from utils import load_image

class Game:
    def __init__(self, display, width, height, selected_letters):
        self.display = display
        self.width = width
        self.height = height
        self.selected_letters = selected_letters
        self.background_image = load_image("assets/tlo.png", (width, height))
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.start_time = None
        self.round_time = 120000
        self.mole_lifetime = 2000
        self.circles = [self.create_new_circle()]
        self.new_kret = False

    def create_new_circle(self):
        x = random.choice([self.width - 140, self.width - 375, self.width - 615])
        y = random.choice([self.height - 100, self.height - 210])
        letter = random.choice(list(self.selected_letters.keys()))
        return Circle(True, x, y, letter)

    def draw_timer(self, time_left):
        timer_text = self.font.render(f"Time left: {time_left//1000} seconds", True, (255, 255, 255))
        self.display.blit(timer_text, (400, 10))

    def handle_event(self, mouse_x, mouse_y):
        if self.start_time is not None:
            current_time = pygame.time.get_ticks()
            clicked_circle = None
            for circle in self.circles:
                distance = ((mouse_x - circle.x) ** 2 + (mouse_y - circle.y) ** 2) ** 0.5
                if distance <= circle.radius and circle.filled:
                    clicked_circle = circle
                    break
            if clicked_circle:
                if current_time - clicked_circle.last_spawn_time < self.mole_lifetime // 2:
                    self.score += 2
                elif current_time - clicked_circle.last_spawn_time < self.mole_lifetime:
                    self.score += 1
                else:
                    self.score -= 1
                self.circles.remove(clicked_circle)
                self.circles.append(self.create_new_circle())
                self.new_kret = True

    def update(self):
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()
        time_elapsed = pygame.time.get_ticks() - self.start_time
        time_left = self.round_time - time_elapsed
        if time_left <= 0:
            return 'menu'
        current_time = pygame.time.get_ticks()
        for circle in self.circles:
            if circle.filled and current_time - circle.last_spawn_time > self.mole_lifetime:
                self.circles.remove(circle)
                self.circles.append(self.create_new_circle())
                break

    def draw(self):
        self.display.blit(self.background_image, (0, 0))
        for circle in self.circles:
            circle.draw(self.display)
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.display.blit(score_text, (10, 10))
        time_left = self.round_time - (pygame.time.get_ticks() - self.start_time)
        self.draw_timer(time_left)
