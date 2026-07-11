import pygame
from pygame import Surface, Clock, Font, Color
from pygame.rect import Rect
from pygame.transform import smoothscale_by

from animation import Animation
from button import Button
from game import Card, GameState, Phase, FaceSuit, Bid, Play
from game.game_state import generate_deck
from game.move import Move
from menu import Menu
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
PADDING: int = 25
PEAK_HEIGHT: int = 15
HEIGHT_INCREASE: int = 30
BACKGROUND_COLOR: Color | tuple[int, int, int] = (12, 12, 12)
TITLE_FONT: Font = pygame.font.SysFont("arial", 60)

WIDTH = 1080
HEIGHT = 720
MIN_WIDTH = 920
MIN_HEIGHT = 660

images: dict[Card, Surface] = {
    card: smoothscale_by(pygame.image.load(f"assets/cards/{card.get_filename()}"),
                         CARD_SCALE_FACTOR) for card in generate_deck()
}

CARD_WIDTH: int = images[Card(FaceSuit.JOKER, 17, 1)].get_width()
CARD_HEIGHT: int = images[Card(FaceSuit.JOKER, 17, 1)].get_height()

HAND_X: int = WIDTH // 2
HAND_Y: int = HEIGHT - CARD_HEIGHT - PADDING // 2

MOVE_BUTTON_WIDTH: int = 100
MOVE_BUTTON_HEIGHT: int = 50
MOVE_BUTTON_BORDER_RADIUS: int = 10
MOVE_BUTTON_POS: tuple[int, int] = (WIDTH // 2, HEIGHT // 2 - CARD_HEIGHT // 2)

AUTO_MOVE_BUTTON_WIDTH: int = 100
AUTO_MOVE_BUTTON_HEIGHT: int = 50
AUTO_MOVE_BUTTON_BORDER_RADIUS: int = 10
AUTO_MOVE_BUTTON_POS: tuple[int, int] = (AUTO_MOVE_BUTTON_WIDTH // 2 + PADDING * 2,
                                         HEIGHT - AUTO_MOVE_BUTTON_HEIGHT // 2 - PADDING)

PLAY_BUTTON_WIDTH: int = 100
PLAY_BUTTON_HEIGHT: int = 50
PLAY_BUTTON_BORDER_RADIUS: int = 10
PLAY_BUTTON_POS: tuple[int, int] = (WIDTH // 2, HEIGHT // 2)

FONT: Font = pygame.font.SysFont("arial", 20)
AUTO_PASS_TIME: int = 100  # ms
AUTO_PLAY_TIME: int = 1000  # ms

CARD_POSITIONS: list[tuple[int, int]] = [
    (PADDING * 2, HEIGHT // 2 - CARD_HEIGHT // 2),
    (WIDTH // 2 - CARD_WIDTH // 2, PADDING * 2),
    (WIDTH - PADDING * 2 - CARD_WIDTH, HEIGHT // 2 - CARD_HEIGHT // 2),
    (WIDTH // 2 - CARD_WIDTH // 2, HEIGHT - CARD_HEIGHT * 5 // 2 - PADDING * 3 // 2)
]

hover_anim: dict[Card, Animation] = {card: Animation(HAND_Y, HAND_Y, HAND_Y, 0, ease_out_cubic)
                                     for card in generate_deck()}
card_selection: dict[Card, bool] = {card: False for card in generate_deck()}
selected_cards: set[Card] = set()
mouse_start_pressing_move_button: bool = False
play_rect: Rect = Rect(PLAY_BUTTON_POS[0] - PLAY_BUTTON_WIDTH // 2,
                       PLAY_BUTTON_POS[1] - PLAY_BUTTON_HEIGHT // 2,
                       PLAY_BUTTON_WIDTH, PLAY_BUTTON_HEIGHT)
play_button: Button = Button(play_rect, "Play", FONT, Color(255, 255, 255), Color(80, 80, 80),
                             Color(100, 100, 100), Color(120, 120, 120), PLAY_BUTTON_BORDER_RADIUS)
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


def update_positions(screen: Surface) -> None:
    global WIDTH
    global HEIGHT
    global CARD_POSITIONS
    global PLAY_BUTTON_POS
    global MOVE_BUTTON_POS
    global AUTO_MOVE_BUTTON_POS
    global HAND_X, HAND_Y
    global move_rect
    global auto_move_rect
    global play_rect
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    PLAY_BUTTON_POS = (WIDTH // 2, HEIGHT // 2)
    play_rect = Rect(PLAY_BUTTON_POS[0] - PLAY_BUTTON_WIDTH // 2,
                     PLAY_BUTTON_POS[1] - PLAY_BUTTON_HEIGHT // 2,
                     PLAY_BUTTON_WIDTH, PLAY_BUTTON_HEIGHT)
    play_button.rect = play_rect
    MOVE_BUTTON_POS = (WIDTH // 2, min(HEIGHT - CARD_HEIGHT * 5 // 2 - PADDING * 5 // 2 -
                                       MOVE_BUTTON_HEIGHT, HEIGHT // 2))
    move_rect = Rect(MOVE_BUTTON_POS[0] - MOVE_BUTTON_WIDTH // 2,
                     MOVE_BUTTON_POS[1] - MOVE_BUTTON_HEIGHT // 2,
                     MOVE_BUTTON_WIDTH, MOVE_BUTTON_HEIGHT)
    move_button.rect = move_rect
    AUTO_MOVE_BUTTON_POS = (AUTO_MOVE_BUTTON_WIDTH // 2 + PADDING * 2,
                            HEIGHT - AUTO_MOVE_BUTTON_HEIGHT // 2 - PADDING)
    auto_move_rect = Rect(AUTO_MOVE_BUTTON_POS[0] - AUTO_MOVE_BUTTON_WIDTH // 2,
                          AUTO_MOVE_BUTTON_POS[1] - AUTO_MOVE_BUTTON_HEIGHT // 2,
                          AUTO_MOVE_BUTTON_WIDTH, AUTO_MOVE_BUTTON_HEIGHT)
    auto_move_button.rect = auto_move_rect

    CARD_POSITIONS = [
        (PADDING * 2, HEIGHT // 2 - CARD_HEIGHT // 2),
        (WIDTH // 2 - CARD_WIDTH // 2, PADDING * 2),
        (WIDTH - PADDING * 2 - CARD_WIDTH, HEIGHT // 2 - CARD_HEIGHT // 2),
        (WIDTH // 2 - CARD_WIDTH // 2, HEIGHT - CARD_HEIGHT * 5 // 2 - PADDING * 3 // 2)
    ]
    HAND_X = WIDTH // 2
    HAND_Y = HEIGHT - CARD_HEIGHT - PADDING // 2


def display_hand(screen: Surface, hand: list[Card], center_pos: tuple[int, int],
                 mouse_pos: tuple[int, int], delta_time: float, mouse_clicked: bool,
                 moves: list[Move]) -> None:
    start_x = int(center_pos[0] - (len(hand) - 1) * (PADDING / 2) - CARD_WIDTH / 2)
    y = center_pos[1] - CARD_HEIGHT // 2
    for i, card in enumerate(hand):
        hovering: bool = (start_x + i * PADDING <= mouse_pos[0] <
                          start_x + i * PADDING +
                          (PADDING if i < len(hand) - 1 else images[card].get_width())
                          and hover_anim[card].end <= mouse_pos[1] < y + images[card].get_height())
        hovering = hovering or (hover_anim[card].end <= mouse_pos[1] < y and
                                start_x + i * PADDING <= mouse_pos[0] <
                                start_x + i * PADDING + images[card].get_width() and
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
        screen.blit(images[card], (start_x + i * PADDING, hover_anim[card].current))


def display_move_button(screen: Surface, move: Move | None, game_state: GameState) -> bool:
    if move is None: return False
    text: str = "Play" if move.type == Phase.TRICK_TAKING else "Discard" \
        if move.type == Phase.BURYING else "Bid" \
        if isinstance(move.move, Bid) and not move.move.empty_bid else "Pass"
    move_button.set_text(text)
    move_button.set_centery(HEIGHT // 2 if game_state.phase != Phase.DRAWING or
                                           game_state.bid.owner != game_state.active_player
                            else min(HEIGHT - CARD_HEIGHT * 5 // 2 - PADDING * 3 // 2 -
                                     MOVE_BUTTON_HEIGHT, HEIGHT // 2))
    return move_button.display(screen)


def display_auto_move_button(screen: Surface, automatic_pass: bool) -> bool:
    auto_move_button.set_text("Auto: On" if automatic_pass else "Auto: Off")
    return auto_move_button.display(screen)


def display_player_name(screen: Surface, player_id: int, position: tuple[int, int],
                        attr: str = "center") -> None:
    player_text = f"Player {player_id + 1}"
    player_surface = FONT.render(player_text, True, (255, 255, 255))
    player_rect = player_surface.get_rect()
    player_rect.__setattr__(attr, position)
    pygame.draw.rect(screen, BACKGROUND_COLOR, player_rect)
    screen.blit(player_surface, player_rect)


def display_player_names(screen: Surface, active_player_id: int, player_ids: list[int]):
    for player_id in player_ids:
        x, y = CARD_POSITIONS[(active_player_id - player_id - 1) % 4]
        display_player_name(screen, player_id, (x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))


def display_current_trick(screen: Surface, game_state: GameState) -> None:
    players_remaining: list[int] = [i for i in range(4) if i != game_state.active_player]
    if game_state.phase == Phase.DRAWING:
        if (bid := game_state.bid).card is not None and not bid.empty_bid:
            position: int = (game_state.active_player - bid.owner) % 4 - 1
            x, y = CARD_POSITIONS[position]
            screen.blit(images[bid.card],
                        (x, y) if bid.quantity == 1 else (x - PADDING // 2, y))
            if bid.quantity == 2:
                screen.blit(images[bid.card], (x + PADDING // 2, y))
            if game_state.active_player != bid.owner:
                players_remaining.remove(bid.owner)
                display_player_name(screen, bid.owner,
                                    position=(x + CARD_WIDTH // 2, y + CARD_HEIGHT + PADDING // 2),
                                    attr="midtop")
        display_player_names(screen, game_state.active_player, players_remaining)
        return
    if game_state.phase != Phase.TRICK_TAKING: return
    current_trick: list[Play] = game_state.curr_trick
    for i, play in enumerate(reversed(current_trick)):
        x, y = CARD_POSITIONS[i]
        card_x = x if play.quantity == 1 else x - PADDING // 2 if i == 0 else \
            x - (play.quantity - 1) * PADDING // 2 if i % 2 == 1 else \
                x + PADDING // 2 - (play.quantity - 1) * PADDING
        screen.blit(images[play.cards[0]], (card_x, y))
        if play.quantity > 1:
            for j, card in enumerate(play.cards):
                if j == 0: continue
                screen.blit(images[card], (card_x + PADDING * j, y))
        name_x = x + CARD_WIDTH // 2
        if i == 0:
            name_x += PADDING // 2 * max(0, play.quantity - 2)
        if i == 2:
            name_x -= PADDING // 2 * max(0, play.quantity - 2)
        players_remaining.remove(play.owner)
        display_player_name(screen, play.owner,
                            (name_x, y + CARD_HEIGHT + PADDING // 2), "midtop")
    display_player_names(screen, game_state.active_player, players_remaining)


def get_selected_move(moves: list[Move]) -> Move | None:
    if len(moves) == 0:
        return None
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
    text: str = (f"{game_state.phase}\n"
                 f"Round Leader: Player {game_state.round_leader + 1}\n" + (
                     f"Trick Leader: Player {game_state.trick_leader + 1}\n"
                     if game_state.phase == Phase.TRICK_TAKING else "") +
                 f"Dominant Rank: {game_state.dominant_rank}\n" + (
                     f"Trump Suit: {game_state.trump_suit.trump_str()}\n"
                     if game_state.phase != Phase.DRAWING else "") +
                 (f"Offense Points: {game_state.offense_points}\n"
                  f"Defense Points: {game_state.defense_points}\n"
                  if game_state.phase == Phase.TRICK_TAKING or
                     game_state.phase == Phase.GAME_END else "")
                 )
    text_surface: Surface = font.render(text, True, (255, 255, 255))
    info_rect: Rect = text_surface.get_rect(topleft=(25, 25))
    pygame.draw.rect(screen, BACKGROUND_COLOR, info_rect)
    screen.blit(text_surface, (25, 25))
    text_surface = font.render(f"Player {game_state.active_player + 1}", True, (255, 255, 255))
    text_rect: Rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - PADDING * 1.5))
    pygame.draw.rect(screen, BACKGROUND_COLOR, text_rect)
    screen.blit(text_surface, text_rect)


def gui_loop() -> None:
    global WIDTH
    global HEIGHT
    pygame.init()
    screen: Surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    clock: Clock = pygame.time.Clock()
    menu: Menu = Menu.TITLE
    game_state: GameState = GameState()
    moves: list[Move] = game_state.generate_moves()
    # while game_state.phase != Phase.BURYING:
    #     game_state.move(moves[0])
    #     moves = game_state.generate_moves()
    automatic_pass: bool = False
    last_move_time: float = pygame.time.get_ticks()
    while True:
        delta_time: float = clock.tick(60)
        update_positions(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and menu == Menu.GAME:
                    automatic_pass = not automatic_pass and game_state.phase == Phase.DRAWING
                # elif event.key == pygame.K_m:
                #     game_state.generate_moves()
                # elif event.key == pygame.K_RETURN:
                #     print(''.join(f"{i + 1} : {repr(move)}\n" for i, move in enumerate(moves)))
            elif event.type == pygame.VIDEORESIZE:
                new_w, new_h = event.size
                WIDTH, HEIGHT = max(MIN_WIDTH, new_w), max(MIN_HEIGHT, new_h)
                print(WIDTH, HEIGHT)
                if new_w != WIDTH or new_h != HEIGHT:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                update_positions(screen)

        screen.fill(BACKGROUND_COLOR)
        match menu:
            case Menu.TITLE:
                text_surface = TITLE_FONT.render("Tractor", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
                screen.blit(text_surface, text_rect)
                if play_button.display(screen):
                    menu = Menu.GAME
                    game_state: GameState = GameState()
                    moves: list[Move] = game_state.generate_moves()
                    # while game_state.phase != Phase.BURYING:
                    #     game_state.move(moves[0])
                    #     moves = game_state.generate_moves()
                    automatic_pass: bool = False
                    last_move_time: float = pygame.time.get_ticks()
                pygame.display.flip()
                continue
            case Menu.GAME:
                display_hand(screen, game_state.get_active_player().cards, (HAND_X, HAND_Y),
                             pygame.mouse.get_pos(), delta_time, pygame.mouse.get_just_pressed()[0],
                             moves)
                move_requested: bool = display_move_button(screen, get_selected_move(moves),
                                                           game_state)
                display_info(screen, game_state, FONT)
                display_current_trick(screen, game_state)
                if game_state.phase == Phase.DRAWING and display_auto_move_button(screen,
                                                                                  automatic_pass):
                    automatic_pass = not automatic_pass
                elif automatic_pass and game_state.phase != Phase.DRAWING:
                    automatic_pass = False
                if move_requested or (automatic_pass and len(moves) == 1 and
                                      pygame.time.get_ticks() - last_move_time > (
                                              AUTO_PASS_TIME if game_state.phase == Phase.DRAWING
                                              else AUTO_PLAY_TIME)):
                    selected_move = get_selected_move(moves)
                    if selected_move is not None:
                        last_move_time = pygame.time.get_ticks()
                        game_state.move(selected_move)
                        game_state.score_points(-1)
                        moves = game_state.generate_moves()
                        selected_cards.clear()
                        y = HAND_Y - CARD_HEIGHT // 2
                        for card in card_selection:
                            hover_anim[card].current = y
                            card_selection[card] = False
                pygame.display.flip()


def terminal_game_loop() -> None:
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
    gui_loop()


if __name__ == '__main__':
    main()
