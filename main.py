import pygame
from pygame import Surface, Clock, Font
from pygame.transform import smoothscale_by
from pygame.rect import Rect

from animation import Animation
from game import Card, GameState, Phase, FaceSuit, Bid
from game.game_state import generate_deck
from game.move import Move
from utils import ease_out_cubic

HELP_TEXT: str = ("Commands:\n"
                  "'h' or 'help' - Views this help message.\n"
                  "'i' or 'info' - Views the current game state.\n"
                  "'q' or 'quit' - Quits the game.\n"
                  "'' - Makes the first move (typing nothing).\n"
                  "'a' or 'auto' - Toggles automatic move mode. This will "
                  "automatically make a move for you if there is only one possible move.\n"
                  )

ANIMATION_TIME: float = 0.3
CARD_SCALE_FACTOR: float = 0.17
CARD_SEPARATION: int = 25
PEAK_HEIGHT: int = 15
HEIGHT_INCREASE: int = 30

WIDTH = 720
HEIGHT = 480

MOVE_BUTTON_WIDTH: int = 100
MOVE_BUTTON_HEIGHT: int = 50
MOVE_BUTTON_BORDER_RADIUS: int = 10
MOVE_BUTTON_POS: tuple[int, int] = (WIDTH // 2, HEIGHT // 2)
MOVE_BUTTON_FONT_SIZE: int = 20

images: dict[Card, Surface] = {
    card: smoothscale_by(pygame.image.load(f"assets/cards/{card.get_filename()}"),
                         CARD_SCALE_FACTOR) for card in generate_deck()
}
hover_anim: dict[Card, Animation] = {card: Animation(539, 539, 539, 0, ease_out_cubic)
                                     for card in generate_deck()}
card_selection: dict[Card, bool] = {card: False for card in generate_deck()}
selected_cards: set[Card] = set()
mouse_start_pressing_move_button: bool = False


def display_hand(screen: Surface, hand: list[Card], center_pos: tuple[int, int],
                 mouse_pos: tuple[int, int], delta_time: float, mouse_clicked: bool,
                 moves: list[Move]) -> None:
    start_x = int(center_pos[0] - (len(hand) - 1) * (CARD_SEPARATION / 2)
                  - (images[Card(FaceSuit.JOKER, 17, 1)].get_width()) / 2)
    y = center_pos[1] - images[Card(FaceSuit.JOKER, 17, 1)].get_height() // 2
    for i, card in enumerate(hand):
        hovering: bool = (start_x + i * CARD_SEPARATION <= mouse_pos[0] <
                          start_x + i * CARD_SEPARATION +
                          (CARD_SEPARATION if i < len(hand) - 1 else images[card].get_width())
                          and hover_anim[card].end <= mouse_pos[1] < y + images[card].get_height())
        hovering = hovering or (hover_anim[card].end <= mouse_pos[1] < y and
                                start_x + i * CARD_SEPARATION <= mouse_pos[0] <
                                start_x + i * CARD_SEPARATION + images[card].get_width())
        if mouse_clicked and hovering:
            card_selection[card] = not card_selection[card]
            if card_selection[card]:
                selected_cards.add(card)
                possible_moves: list[Move] = [move for move in moves if card in move]
                for secondary_card in selected_cards:
                    present = False
                    for move in possible_moves:
                        if secondary_card in move:
                            present = True
                            break
                    if not present:
                        card_selection[secondary_card] = False
                for selected_card in card_selection:
                    present: bool = any(other.exact_card(selected_card) for other in selected_cards)
                    if present and not card_selection[selected_card]:
                        selected_cards.remove(selected_card)
            else:
                selected_cards.remove(card)
        if card_selection[card]:
            hover_anim[card].set_bounds(y - PEAK_HEIGHT if
                                        hover_anim[card].current == y - PEAK_HEIGHT else y,
                                        y - HEIGHT_INCREASE)
        elif hovering and any(card in move for move in moves):
            hover_anim[card].set_bounds(y - HEIGHT_INCREASE if
                                        hover_anim[card].current < y - PEAK_HEIGHT else y,
                                        y - PEAK_HEIGHT)
        else:
            hover_anim[card].set_bounds(y - HEIGHT_INCREASE, y)
        hover_anim[card].update(delta_time / 1000.0 / ANIMATION_TIME)
        screen.blit(images[card], (start_x + i * CARD_SEPARATION, hover_anim[card].current))


def display_move_button(screen: Surface, move_rect: Rect, move: Move, font: Font) -> bool:
    global mouse_start_pressing_move_button
    if move is None: return False
    mouse_x: int = pygame.mouse.get_pos()[0]
    mouse_y: int = pygame.mouse.get_pos()[1]
    mouse_down: bool = pygame.mouse.get_pressed()[0]
    hovering = move_rect.collidepoint(mouse_x, mouse_y)
    shade = 120 if mouse_down and hovering and mouse_start_pressing_move_button \
        else 100 if hovering else 80
    pygame.draw.rect(screen, (shade, shade, shade), move_rect,
                     border_radius=MOVE_BUTTON_BORDER_RADIUS)
    text: str = "Play" if move.type == Phase.TRICK_TAKING else "Discard" \
        if move.type == Phase.BURYING else "Bid" \
        if isinstance(move, Bid) and not move.empty_bid else "Pass"
    text_surface: Surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (move_rect.centerx - text_surface.get_width() // 2,
                               move_rect.centery - text_surface.get_height() // 2))
    if pygame.mouse.get_just_pressed()[0]:
        mouse_start_pressing_move_button = hovering
    return pygame.mouse.get_just_released()[0] and hovering and mouse_start_pressing_move_button


def get_selected_move(moves: list[Move]) -> Move | None:
    for move in moves:
        if move.cards_match(list(selected_cards)):
            return move
    return None


def gui_game_loop() -> None:
    pygame.init()
    screen: Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    clock: Clock = pygame.time.Clock()
    font: Font = pygame.font.SysFont("arial", MOVE_BUTTON_FONT_SIZE)
    game_state: GameState = GameState()
    while game_state.phase == Phase.DRAWING or game_state.phase == Phase.BURYING:
        game_state.move(game_state.generate_moves()[0])
    moves: list[Move] = game_state.generate_moves()
    move_rect: Rect = Rect(MOVE_BUTTON_POS[0] - MOVE_BUTTON_WIDTH // 2,
                           MOVE_BUTTON_POS[1] - MOVE_BUTTON_HEIGHT // 2,
                           MOVE_BUTTON_WIDTH, MOVE_BUTTON_HEIGHT)
    print(game_state.trump_suit)
    while True:
        delta_time: float = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        screen.fill(0)
        display_hand(screen, game_state.get_active_player().cards, (WIDTH // 2, 400),
                     pygame.mouse.get_pos(), delta_time, pygame.mouse.get_just_pressed()[0], moves)
        move_requested: bool = display_move_button(screen, move_rect, get_selected_move(moves),
                                                   font)
        if move_requested:
            selected_move = get_selected_move(moves)
            if selected_move is not None:
                game_state.move(selected_move)
                moves = game_state.generate_moves()
                selected_cards.clear()
                for card in card_selection:
                    card_selection[card] = False
        pygame.display.flip()


def game_loop() -> None:
    game_state = GameState()
    auto: bool = False
    while game_state.is_in_progress():
        moves: list[Move] = game_state.generate_moves()
        print(f"Player {game_state.active_player + 1} move")
        print(f"Hand: {game_state.show_current_hand()}")
        if game_state.phase == Phase.TRICK_TAKING:
            print(f"Current Trick: {game_state.show_current_trick()}")
        print("Available Moves:")
        print(''.join(f"{i + 1} : {move}\n" for i, move in enumerate(moves)))
        move: int = 0
        while not auto or len(moves) > 1:
            move_str = input("Enter move index or command: ").lower()
            if move_str == "": break
            if move_str == "h" or move_str == "help":
                print(HELP_TEXT)
                continue
            if move_str == "a" or move_str == "auto":
                auto = not auto
                print(f"Automatic Move Mode: {"Enabled" if auto else "Disabled"}")
                continue
            if move_str == "i" or move_str == "info":
                print(f"Game Phase: {game_state.phase}")
                print(f"Dominant Rank: {game_state.dominant_rank}")
                if game_state.phase == Phase.DRAWING:
                    print(f"Bid: {game_state.bid}")
                    print(f"Bid Owner: {game_state.bid.owner}")
                if game_state.phase == Phase.TRICK_TAKING or game_state.phase == Phase.BURYING:
                    print(f"Trump Suit: {game_state.trump_suit}")
                    print(f"Trick Leader: {game_state.trick_leader}")
                print()
                continue
            if move_str == "q" or move_str == "quit":
                if "y" == input("Are you sure you want to quit? [y/N] "): return
                continue
            if move_str.isnumeric():
                move = int(move_str) - 1
                if 0 <= move < len(moves): break
        game_state.move(moves[move])


def main() -> None:
    print("Welcome to Tractor!")
    print(HELP_TEXT)
    while True:
        start: str = input("Would you like to start a game? [Y/n] ").lower()
        if start == "n": break
        game_loop()


if __name__ == '__main__':
    gui_game_loop()
