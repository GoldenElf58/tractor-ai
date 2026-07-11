import pygame

from pygame import Rect, Font, Surface
from pygame.color import Color


class Button:
    def __init__(self, rect: Rect, text: str, font: Font, text_color: Color, btn_color: Color,
                 btn_hover_color: Color | None = None, btn_pressed_color: Color | None = None,
                 border_radius: int = 0):
        self.rect: Rect = rect
        self.text: str = text
        self.font: Font = font
        self.text_color: Color = text_color
        self.btn_color: Color = btn_color
        self.btn_hover_color: Color = btn_hover_color if btn_hover_color is not None else btn_color
        self.btn_pressed_color: Color = btn_pressed_color if btn_pressed_color is not None \
            else btn_color
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

    def display(self, screen: Surface) -> bool:
        mouse_down: bool = pygame.mouse.get_pressed()[0]
        hovering: bool = self.mouse_is_hovering()
        color: Color = self.btn_pressed_color if (mouse_down and hovering and
                                                  self.mouse_start_pressing_button) \
            else self.btn_hover_color if hovering else self.btn_color
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        text_surface: Surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2,
                                   self.rect.centery - text_surface.get_height() // 2))
        if pygame.mouse.get_just_pressed()[0]:
            self.mouse_start_pressing_button = hovering
        return pygame.mouse.get_just_released()[0] and hovering and self.mouse_start_pressing_button
