import pygame
from pygame import Font, Color
from pygame.rect import Rect
from pygame.surface import Surface


class Textbox:
    def __init__(self, font: Font, center_pos: tuple[int, int], width: int, height: int,
                 text_color: Color | None = None, bg_color: Color | None = None,
                 default_text_color: Color | None = None,
                 border_radius: int = 10, default_text: str = ""):
        self.default_text: str = default_text
        self.text: str = ""
        self.font: Font = font
        self.rect: Rect = Rect(center_pos[0] - width // 2, center_pos[1] - height // 2, width,
                               height)
        self.width = self.rect.width
        self.center = self.rect.center
        self.text_color: Color = text_color if text_color is not None else Color(255, 255, 255)
        self.default_text_color: Color = text_color if text_color is not None else (
            Color(150, 150, 150))
        self.bg_color: Color = bg_color if bg_color is not None else Color(40, 40, 40)
        self.border_radius: int = border_radius
        self.selected = False

    def set_text(self, text: str) -> None:
        self.text = text

    def get_output(self):
        return self.text if len(self.text) > 0 else self.default_text

    def mouse_is_hovering(self) -> bool:
        mouse_x: int = pygame.mouse.get_pos()[0]
        mouse_y: int = pygame.mouse.get_pos()[1]
        return self.rect.collidepoint(mouse_x, mouse_y)

    def display(self, screen: Surface) -> None:
        hovering: bool = self.mouse_is_hovering()
        if self.text == "":
            text_surface: Surface = self.font.render(self.default_text, True,
                                                     self.default_text_color)
        else:
            text_surface: Surface = self.font.render(self.text, True, self.text_color)
        self.rect.width = max(self.width, text_surface.width + 25)
        self.rect.center = self.center
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=self.border_radius)
        screen.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2,
                                   self.rect.centery - text_surface.get_height() // 2))
        if pygame.mouse.get_just_pressed()[0]:
            self.selected = hovering
        if self.selected:
            pygame.draw.rect(screen, (150, 150, 150), self.rect, border_radius=self.border_radius,
                             width=2)
