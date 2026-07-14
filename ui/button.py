import pygame

from pygame import Rect, Font, Surface
from pygame.color import Color


class Button:
    def __init__(self, text: str, centerpos: tuple[int, int], width: int, height: int,
                 font: Font, text_color: Color | None = None,
                 btn_color: Color | None = None, btn_hover_color: Color | None = None,
                 btn_pressed_color: Color | None = None, border_radius: int = 10):
        self._rect: Rect = Rect(centerpos[0] - width // 2, centerpos[1] - height // 2, width, height)
        self.width = self.rect.width
        self.center: tuple[int, int] = self.rect.center
        self.text: str = text
        self.font: Font = font
        self.text_color: Color = text_color if text_color is not None else Color(255, 255, 255)
        self.btn_color: Color = btn_color if btn_color is not None else Color(80, 80, 80)
        self.btn_hover_color: Color = btn_hover_color if btn_hover_color is not None else (
            Color(self.btn_color.r + 20, self.btn_color.g + 20, self.btn_color.b + 20))
        self.btn_pressed_color: Color = btn_pressed_color if btn_pressed_color is not None \
            else Color(self.btn_color.r + 40, self.btn_color.g + 40, self.btn_color.b + 40)
        self.border_radius: int = border_radius
        self.mouse_start_pressing_button: bool = False

    def set_text(self, text: str) -> None:
        self.text = text

    def mouse_is_hovering(self) -> bool:
        mouse_x: int = pygame.mouse.get_pos()[0]
        mouse_y: int = pygame.mouse.get_pos()[1]
        return self.rect.collidepoint(mouse_x, mouse_y)

    def set_centery(self, y: int) -> None:
        self.rect.centery = y
        self.center = (self.center[0], y)

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, value: Rect):
        self._rect = value
        self.center = self._rect.center

    def set_center(self, center: tuple[int, int]):
        self.center = center
        self.rect.center = center

    def display(self, screen: Surface) -> bool:
        mouse_down: bool = pygame.mouse.get_pressed()[0]
        hovering: bool = self.mouse_is_hovering()
        color: Color = self.btn_pressed_color if (mouse_down and hovering and
                                                  self.mouse_start_pressing_button) \
            else self.btn_hover_color if hovering else self.btn_color
        text_surface: Surface = self.font.render(self.text, True, (255, 255, 255))
        self.rect.width = max(self.width, text_surface.width + 25)
        self.rect.center = self.center
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        screen.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2,
                                   self.rect.centery - text_surface.get_height() // 2))
        if pygame.mouse.get_just_pressed()[0]:
            self.mouse_start_pressing_button = hovering
        return pygame.mouse.get_just_released()[0] and hovering and self.mouse_start_pressing_button
