import pygame

class Circle:
    def __init__(self, filled, x, y, letter):
        self.radius = 70
        self.x = x
        self.y = y
        self.filled = filled
        self.letter = letter
        self.last_spawn_time = pygame.time.get_ticks()

    def draw(self, display):
        image = pygame.image.load("assets/kret.png")
        image_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, self.radius)
        image = pygame.transform.scale(image, (120, 120))
        font = pygame.font.Font(None, 36)
        if self.filled:
            display.blit(image, image_rect)
            letter_surface = font.render(self.letter, True, (0, 0, 0))
            letter_rect = letter_surface.get_rect(center=(self.x, self.y - self.radius - 20))
            display.blit(letter_surface, letter_rect)
        else:
            display.blit(image, image_rect)
