import pygame
from pygame import Surface, Clock, Font, Color, font
from pygame.rect import Rect
from pygame.transform import smoothscale_by

from animation import Animation
from button import Button
from game import Card, GameState, Phase, FaceSuit, Bid
from game.game_state import generate_deck
from game.move import Move
from utils import ease_out_cubic

pygame.init()

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

WIDTH = 1080
HEIGHT = 720

images: dict[Card, Surface] = {
    card: smoothscale_by(pygame.image.load(f"assets/cards/{card.get_filename()}"),
                         CARD_SCALE_FACTOR) for card in generate_deck()
}

HAND_X: int = WIDTH // 2
HAND_Y: int = HEIGHT - images[Card(FaceSuit.JOKER, 17, 1)].get_height() // 2 - CARD_SEPARATION

MOVE_BUTTON_WIDTH: int = 100
MOVE_BUTTON_HEIGHT: int = 50
MOVE_BUTTON_BORDER_RADIUS: int = 10
MOVE_BUTTON_POS: tuple[int, int] = (WIDTH // 2, HEIGHT // 2)

AUTO_MOVE_BUTTON_WIDTH: int = 100
AUTO_MOVE_BUTTON_HEIGHT: int = 50
AUTO_MOVE_BUTTON_BORDER_RADIUS: int = 10
AUTO_MOVE_BUTTON_POS: tuple[int, int] = (WIDTH // 2,
                                         HEIGHT // 2 + MOVE_BUTTON_HEIGHT + CARD_SEPARATION)

FONT: Font = font.SysFont("arial", 20)
AUTO_PASS_TIME: int = 100  # ms
AUTO_PLAY_TIME: int = 1000  # ms

hover_anim: dict[Card, Animation] = {card: Animation(HAND_Y, HAND_Y, HAND_Y, 0, ease_out_cubic)
                                     for card in generate_deck()}
card_selection: dict[Card, bool] = {card: False for card in generate_deck()}
selected_cards: set[Card] = set()
mouse_start_pressing_move_button: bool = False
move_rect: Rect = Rect(MOVE_BUTTON_POS[0] - MOVE_BUTTON_WIDTH // 2,
                       MOVE_BUTTON_POS[1] - MOVE_BUTTON_HEIGHT // 2,
                       MOVE_BUTTON_WIDTH, MOVE_BUTTON_HEIGHT)
move_button: Button = Button(move_rect, "", FONT, Color(255, 255, 255), Color(80, 80, 80),
                             Color(100, 100, 100), Color(120, 120, 120), MOVE_BUTTON_BORDER_RADIUS)
auto_move_rect: Rect = Rect(AUTO_MOVE_BUTTON_POS[0] - AUTO_MOVE_BUTTON_WIDTH // 2,
                            AUTO_MOVE_BUTTON_POS[1] - AUTO_MOVE_BUTTON_HEIGHT // 2,
                            AUTO_MOVE_BUTTON_WIDTH, AUTO_MOVE_BUTTON_HEIGHT)
auto_move_button: Button = Button(auto_move_rect, "", FONT,
                                  Color(255, 255, 255), Color(80, 80, 80),
                                  Color(100, 100, 100), Color(120, 120, 120),
                                  MOVE_BUTTON_BORDER_RADIUS)


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
                                start_x + i * CARD_SEPARATION + images[card].get_width() and
                                (i == len(hand) - 1 or hover_anim[hand[i + 1]].end > mouse_pos[1]))
        if mouse_clicked and hovering:
            card_selection[card] = not card_selection[card]
            if moves[0].type == Phase.BURYING and card_selection[card]:
                if len(selected_cards) < 8:
                    selected_cards.add(card)
                else:
                    card_selection[card] = False
            elif card_selection[card]:
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
        elif hovering and (any(card in move for move in moves) and
                           (moves[0].type != Phase.BURYING or len(selected_cards) < 8)):
            hover_anim[card].set_bounds(y - HEIGHT_INCREASE if
                                        hover_anim[card].current < y - PEAK_HEIGHT else y,
                                        y - PEAK_HEIGHT)
        else:
            hover_anim[card].set_bounds(y - HEIGHT_INCREASE, y)
        hover_anim[card].update(delta_time / 1000.0 / ANIMATION_TIME)
        screen.blit(images[card], (start_x + i * CARD_SEPARATION, hover_anim[card].current))


def display_move_button(screen: Surface, move: Move | None) -> bool:
    if move is None: return False
    text: str = "Play" if move.type == Phase.TRICK_TAKING else "Discard" \
        if move.type == Phase.BURYING else "Bid" \
        if isinstance(move.move, Bid) and not move.move.empty_bid else "Pass"
    move_button.set_text(text)
    return move_button.display(screen)


def display_auto_move_button(screen: Surface, automatic_pass: bool) -> bool:
    auto_move_button.set_text("Auto: On" if automatic_pass else "Auto: Off")
    return auto_move_button.display(screen)


def get_selected_move(moves: list[Move]) -> Move | None:
    if moves[0].type == Phase.BURYING:
        if len(selected_cards) == 8:
            return Move(list(selected_cards))
        return None
    for move in moves:
        if move.cards_match(list(selected_cards)):
            return move
    if moves[0].type == Phase.DRAWING:
        for move in moves:
            if isinstance(move.move, Bid) and move.move.empty_bid: return move
    return None


def display_info(screen: Surface, game_state: GameState, font: Font) -> None:
    text: str = (f"{game_state.phase} - Player {game_state.active_player} Turn\n"
                 f"Round Leader: Player {game_state.round_leader}\n" + (
                     f"Trick Leader: Player {game_state.trick_leader}\n"
                     if game_state.phase == Phase.TRICK_TAKING else "") +
                 (f"Bid: {game_state.bid} from Player {game_state.bid.owner}\n"
                  if not game_state.bid.empty_bid and game_state.phase == Phase.DRAWING else "") +
                 f"Dominant Rank: {game_state.dominant_rank}\n" + (
                     f"Trump Suit: {game_state.trump_suit.trump_str()}\n"
                     if game_state.phase != Phase.DRAWING else ""
                 ))
    text_surface: Surface = font.render(text, True, (255, 255, 255))
    info_rect: Rect = text_surface.get_rect(topleft=(25, 25))
    pygame.draw.rect(screen, (0, 0, 0), info_rect)
    screen.blit(text_surface, (25, 25))


def gui_game_loop() -> None:
    pygame.init()
    screen: Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    clock: Clock = pygame.time.Clock()
    game_state: GameState = GameState()
    # while game_state.phase == Phase.DRAWING:
    #     game_state.move(game_state.generate_moves()[0])
    moves: list[Move] = game_state.generate_moves()
    automatic_pass: bool = False
    last_move_time: float = pygame.time.get_ticks()
    while True:
        delta_time: float = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        screen.fill(0)
        display_hand(screen, game_state.get_active_player().cards, (HAND_X, HAND_Y),
                     pygame.mouse.get_pos(), delta_time, pygame.mouse.get_just_pressed()[0], moves)
        move_requested: bool = display_move_button(screen, get_selected_move(moves))
        display_info(screen, game_state, FONT)
        if display_auto_move_button(screen, automatic_pass):
            automatic_pass = not automatic_pass
        if move_requested or (automatic_pass and len(moves) == 1 and
                              pygame.time.get_ticks() - last_move_time > (
                                      AUTO_PASS_TIME if game_state.phase == Phase.DRAWING else
                                      AUTO_PLAY_TIME)):
            selected_move = get_selected_move(moves)
            if selected_move is not None:
                last_move_time = pygame.time.get_ticks()
                game_state.move(selected_move)
                moves = game_state.generate_moves()
                selected_cards.clear()
                y = HAND_Y - images[Card(FaceSuit.JOKER, 17, 1)].get_height() // 2
                for card in card_selection:
                    hover_anim[card].current = y
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
