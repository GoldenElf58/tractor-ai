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
from textbox import Textbox
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
TEXT_COLOR: Color | tuple[int, int, int] = (255, 255, 255)
FONT: Font = pygame.font.SysFont("arial", 20)
HEADING_FONT: Font = pygame.font.SysFont("arial", 40)
TITLE_FONT: Font = pygame.font.SysFont("arial", 60)

WIDTH = 1080
HEIGHT = 720
MIN_WIDTH = 1000
MIN_HEIGHT = 660

images: dict[Card, Surface] = {
    card: smoothscale_by(pygame.image.load(f"assets/cards/{card.get_filename()}"),
                         CARD_SCALE_FACTOR) for card in generate_deck()
}

CARD_WIDTH: int = images[Card(FaceSuit.JOKER, 17, 1)].get_width()
CARD_HEIGHT: int = images[Card(FaceSuit.JOKER, 17, 1)].get_height()

HAND_X: int = WIDTH // 2
HAND_Y: int = HEIGHT - CARD_HEIGHT - PADDING // 2

BUTTON_WIDTH: int = 100
BUTTON_HEIGHT: int = 50

TEXTBOX_WIDTH: int = 100
TEXTBOX_MAX_WIDTH: int = 275
TEXTBOX_HEIGHT: int = 50

MOVE_BUTTON_POS: tuple[int, int] = (WIDTH // 2, HEIGHT // 2 - CARD_HEIGHT // 2)
AUTO_MOVE_BUTTON_POS: tuple[int, int] = (BUTTON_WIDTH // 2 + PADDING,
                                         HEIGHT - BUTTON_HEIGHT // 2 - PADDING)
PLAY_BUTTON_POS: tuple[int, int] = (WIDTH // 2, HEIGHT // 2)
CONFIRM_END_ROUND_BUTTON_POS: tuple[int, int] = (WIDTH // 2, HEIGHT * 3 // 4)

AUTO_PASS_TIME: int = 100  # ms
AUTO_PLAY_TIME: int = 1000  # ms

CARD_POSITIONS: list[tuple[int, int]] = [
    (PADDING * 2, HEIGHT // 2 - CARD_HEIGHT // 2),
    (WIDTH // 2 - CARD_WIDTH // 2, PADDING * 2),
    (WIDTH - PADDING * 2 - CARD_WIDTH, HEIGHT // 2 - CARD_HEIGHT // 2),
    (WIDTH // 2 - CARD_WIDTH // 2, HEIGHT - CARD_HEIGHT * 5 // 2 - PADDING * 3 // 2)
]

NAME_TEXTBOX_POSITIONS: list[tuple[int, int]] = [
    (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * -1),
    (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 0),
    (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 1),
    (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 2),
]

CONFIRM_NAMES_BUTTON_POS: tuple[int, int] = (WIDTH // 2,
                                             HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 3)

MAX_NAME_LENGTH: int = 15

textboxes: list[Textbox] = \
    [Textbox(FONT, pos, TEXTBOX_WIDTH, TEXTBOX_HEIGHT, default_text=f"Player {i + 1}") for i, pos in
     enumerate(NAME_TEXTBOX_POSITIONS)]

hover_anim: dict[Card, Animation] = {card: Animation(HAND_Y, HAND_Y, HAND_Y, 0, ease_out_cubic)
                                     for card in generate_deck()}
card_selection: dict[Card, bool] = {card: False for card in generate_deck()}
selected_cards: set[Card] = set()
mouse_start_pressing_move_button: bool = False
play_button: Button = Button("Play", PLAY_BUTTON_POS, BUTTON_WIDTH, BUTTON_HEIGHT, FONT)
confirm_names_button: Button = Button("Confirm", CONFIRM_NAMES_BUTTON_POS, BUTTON_WIDTH,
                                      BUTTON_HEIGHT, FONT)
move_button: Button = Button("", MOVE_BUTTON_POS, BUTTON_WIDTH, BUTTON_HEIGHT, FONT)
auto_move_button: Button = Button("", AUTO_MOVE_BUTTON_POS, BUTTON_WIDTH, BUTTON_HEIGHT, FONT)
confirm_end_round_game_button: Button = Button("Continue", CONFIRM_END_ROUND_BUTTON_POS,
                                               BUTTON_WIDTH, BUTTON_HEIGHT, FONT)


def update_positions(screen: Surface) -> None:
    global WIDTH
    global HEIGHT
    global CARD_POSITIONS
    global NAME_TEXTBOX_POSITIONS
    global CONFIRM_NAMES_BUTTON_POS
    global PLAY_BUTTON_POS
    global MOVE_BUTTON_POS
    global CONFIRM_END_ROUND_BUTTON_POS
    global AUTO_MOVE_BUTTON_POS
    global HAND_X, HAND_Y

    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    PLAY_BUTTON_POS = (WIDTH // 2, HEIGHT // 2)
    MOVE_BUTTON_POS = (WIDTH // 2, min(HEIGHT - CARD_HEIGHT * 5 // 2 - PADDING * 5 // 2 -
                                       BUTTON_HEIGHT, HEIGHT // 2))
    AUTO_MOVE_BUTTON_POS = (BUTTON_WIDTH // 2 + PADDING, HEIGHT - BUTTON_HEIGHT // 2 - PADDING)
    CONFIRM_END_ROUND_BUTTON_POS = (WIDTH // 2, HEIGHT * 3 // 4)

    play_button.rect.center = PLAY_BUTTON_POS
    confirm_names_button.rect.center = CONFIRM_NAMES_BUTTON_POS
    move_button.rect.center = MOVE_BUTTON_POS
    auto_move_button.rect.center = AUTO_MOVE_BUTTON_POS
    confirm_end_round_game_button.rect.center = CONFIRM_END_ROUND_BUTTON_POS

    CARD_POSITIONS = [
        (PADDING * 2, HEIGHT // 2 - CARD_HEIGHT // 2),
        (WIDTH // 2 - CARD_WIDTH // 2, PADDING * 2),
        (WIDTH - PADDING * 2 - CARD_WIDTH, HEIGHT // 2 - CARD_HEIGHT // 2),
        (WIDTH // 2 - CARD_WIDTH // 2, HEIGHT - CARD_HEIGHT * 5 // 2 - PADDING * 3 // 2)
    ]

    NAME_TEXTBOX_POSITIONS = [
        (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * -1),
        (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 0),
        (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 1),
        (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 2),
    ]

    CONFIRM_NAMES_BUTTON_POS = (WIDTH // 2, HEIGHT // 2 + (TEXTBOX_HEIGHT + PADDING) * 3)
    for i, textbox in enumerate(textboxes):
        textbox.rect.center = NAME_TEXTBOX_POSITIONS[i]

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
                                     BUTTON_HEIGHT, HEIGHT // 2))
    return move_button.display(screen)


def display_auto_move_button(screen: Surface, automatic_pass: bool) -> bool:
    auto_move_button.set_text("Auto: On" if automatic_pass else "Auto: Off")
    return auto_move_button.display(screen)


def display_player_name(screen: Surface, name: str, position: tuple[int, int],
                        attr: str = "center") -> None:
    player_surface = FONT.render(name, True, TEXT_COLOR)
    player_rect = player_surface.get_rect()
    player_rect.__setattr__(attr, position)
    if player_rect.left - PADDING // 2 < 0: player_rect.left = PADDING // 2
    if player_rect.right + PADDING // 2 > WIDTH: player_rect.right = WIDTH - PADDING // 2
    if player_rect.top - PADDING // 2 < 0: player_rect.top = PADDING // 2
    if player_rect.bottom + PADDING // 2 > HEIGHT: player_rect.bottom = HEIGHT - PADDING // 2
    pygame.draw.rect(screen, BACKGROUND_COLOR, player_rect)
    screen.blit(player_surface, player_rect)


def display_player_names(screen: Surface, game_state: GameState, player_ids: list[int]):
    for player_id in player_ids:
        x, y = CARD_POSITIONS[(game_state.active_player - player_id - 1) % 4]
        display_player_name(screen, game_state.get_player_name(player_id),
                            (x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))


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
                display_player_name(screen, game_state.get_player_name(bid.owner),
                                    position=(x + CARD_WIDTH // 2, y + CARD_HEIGHT + PADDING // 2),
                                    attr="midtop")
        display_player_names(screen, game_state, players_remaining)
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
        display_player_name(screen, game_state.get_player_name(play.owner),
                            (name_x, y + CARD_HEIGHT + PADDING // 2), "midtop")
    display_player_names(screen, game_state, players_remaining)


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
                 f"Round Leader: {game_state.get_player_name(game_state.round_leader)}\n" + (
                     f"Trick Leader: {game_state.get_player_name(game_state.trick_leader)}\n"
                     if game_state.phase == Phase.TRICK_TAKING else "") +
                 f"Dominant Rank: {game_state.dominant_rank}\n" + (
                     f"Trump Suit: {game_state.trump_suit.trump_str()}\n"
                     if game_state.phase != Phase.DRAWING else "") +
                 (f"Offense Points: {game_state.offense_points}\n"
                  f"Defense Points: {game_state.defense_points}\n"
                  if game_state.phase == Phase.TRICK_TAKING or
                     game_state.phase == Phase.GAME_END else "")
                 )
    text_surface: Surface = font.render(text, True, TEXT_COLOR)
    info_rect: Rect = text_surface.get_rect(topleft=(25, 25))
    pygame.draw.rect(screen, BACKGROUND_COLOR, info_rect)
    screen.blit(text_surface, (25, 25))
    text_surface = font.render(game_state.get_active_player_name(), True, TEXT_COLOR)
    text_rect: Rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - PADDING * 1.5))
    pygame.draw.rect(screen, BACKGROUND_COLOR, text_rect)
    screen.blit(text_surface, text_rect)


def display_centered_info_text(screen: Surface, text: str, centerx: int, centery: int):
    text_surface = FONT.render(text, True, TEXT_COLOR)
    height = text_surface.get_height()
    width = text_surface.get_width()
    top = text_surface.get_rect(centery=centery).top
    lines = [line.split('\t') for line in text.split('\n')]
    left_len: float = sum(len(line[0]) for line in lines if len(line) == 2) / len(lines) + 2
    right_len: float = sum(len(line[1]) for line in lines if len(line) == 2) / len(lines) + 2
    middle = centerx + (left_len / (left_len + right_len) * width) * 0
    for i, line in enumerate(lines):
        if len(line) != 2:
            text_surface = FONT.render(line[0], True, TEXT_COLOR)
            text_rect = text_surface.get_rect(right=middle, top=top + (i / len(lines)) * height)
            screen.blit(text_surface, text_rect)
            continue
        left = line[0] + ': '
        right = " " + line[1]
        left_surface = FONT.render(left, True, TEXT_COLOR)
        right_surface = FONT.render(right, True, TEXT_COLOR)
        left_rect = left_surface.get_rect(right=middle, top=top + (i / len(lines)) * height)
        right_rect = right_surface.get_rect(left=middle, top=top + (i / len(lines)) * height)
        pygame.draw.rect(screen, BACKGROUND_COLOR, left_rect)
        pygame.draw.rect(screen, BACKGROUND_COLOR, right_rect)
        screen.blit(left_surface, left_rect)
        screen.blit(right_surface, right_rect)


def display_round_summary(screen: Surface, game_state: GameState) -> None:
    text_surface: Surface = HEADING_FONT.render("Round Summary", True, TEXT_COLOR)
    text_rect: Rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    pygame.draw.rect(screen, BACKGROUND_COLOR, text_rect)
    screen.blit(text_surface, text_rect)
    game_state.score_points(game_state.active_player)
    text: str = (
        f"Offense Points\t{game_state.offense_points}\n"
        f"Defense Points\t{game_state.defense_points}\n"
        f"Trump Suit\t{game_state.trump_suit.trump_str()}\n"
        f"Dominant Rank\t{game_state.dominant_rank} → {game_state.get_next_dominant_rank()}\n"
        f"Round Leader\t{game_state.get_player_name(game_state.round_leader)} → "
        f"{game_state.get_player_name(game_state.get_next_round_leader())}\n"
        f"{game_state.get_player_name(0)} and {game_state.get_player_name(2)} Level\t"
        f"{game_state.team_levels[0]} → {game_state.get_next_team_levels()[0]}\n"
        f"{game_state.get_player_name(1)} and {game_state.get_player_name(3)} Level\t"
        f"{game_state.team_levels[1]} → {game_state.get_next_team_levels()[1]}"
    )
    display_centered_info_text(screen, text, WIDTH // 2, HEIGHT // 2)


def display_name_players(screen: Surface) -> None:
    text_surface: Surface = HEADING_FONT.render("Name Players", True, TEXT_COLOR)
    text_rect: Rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    pygame.draw.rect(screen, BACKGROUND_COLOR, text_rect)
    screen.blit(text_surface, text_rect)
    for i, textbox in enumerate(textboxes):
        textbox.display(screen)


def get_player_names() -> list[str]:
    return [textbox.get_output() for textbox in textboxes]


def display_game_end(screen: Surface, game_state: GameState) -> None:
    text_surface: Surface = TITLE_FONT.render("Game Over", True, TEXT_COLOR)
    text_rect: Rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    pygame.draw.rect(screen, BACKGROUND_COLOR, text_rect)
    screen.blit(text_surface, text_rect)
    winning_team: int = game_state.get_winning_team()
    text = (
        f"Winners\t{game_state.get_player_name(winning_team)} and "
        f"{game_state.get_player_name(winning_team + 2)}\n"
        f"{game_state.get_player_name(0)} and {game_state.get_player_name(2)} Level\t"
        f"{min(14, game_state.team_levels[0])}\n"
        f"{game_state.get_player_name(1)} and {game_state.get_player_name(3)} Level\t"
        f"{min(14, game_state.team_levels[1])}\n "
    )
    display_centered_info_text(screen, text, WIDTH // 2, HEIGHT // 2)


def gui_loop() -> None:
    global WIDTH
    global HEIGHT
    pygame.init()
    pygame.key.set_repeat(500, 50)
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
                if menu == Menu.NAME_PLAYERS:
                    for i, textbox in enumerate(textboxes):
                        if textbox.selected:
                            if event.key == pygame.K_BACKSPACE:
                                if event.mod & pygame.KMOD_ALT or event.mod & pygame.KMOD_CTRL:
                                    text: list[str] = textbox.text.split(" ")
                                    while len(text) > 0 and text.pop() == "":
                                        pass
                                    new_text: str = " ".join(text)
                                    textbox.set_text(new_text)
                                elif event.mod & pygame.KMOD_META:
                                    textbox.set_text("")
                                else:
                                    textbox.text = textbox.text[:-1]
                            elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                                textbox.selected = False
                                if event.mod & pygame.KMOD_SHIFT:
                                    if i > 0:
                                        textboxes[i - 1].selected = True
                                elif i < len(textboxes) - 1:
                                    textboxes[i + 1].selected = True
                            elif event.key == pygame.K_UP:
                                if i > 0:
                                    textbox.selected = False
                                    textboxes[i - 1].selected = True
                            elif event.key == pygame.K_DOWN:
                                if i < len(textboxes) - 1:
                                    textbox.selected = False
                                    textboxes[i + 1].selected = True
                            elif event.key == pygame.K_ESCAPE:
                                textbox.selected = False
                            elif len(textbox.text) < MAX_NAME_LENGTH and not (
                                    event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                                textbox.text += event.unicode
                            break
                if event.key == pygame.K_SPACE and menu == Menu.GAME:
                    automatic_pass = not automatic_pass and game_state.phase == Phase.DRAWING
                # elif event.key == pygame.K_m:
                #     game_state.generate_moves()
                # elif event.key == pygame.K_RETURN:
                #     print(''.join(f"{i + 1} : {repr(move)}\n" for i, move in enumerate(moves)))
            elif event.type == pygame.VIDEORESIZE:
                new_w, new_h = event.size
                WIDTH, HEIGHT = max(MIN_WIDTH, new_w), max(MIN_HEIGHT, new_h)
                if new_w != WIDTH or new_h != HEIGHT:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                update_positions(screen)

        screen.fill(BACKGROUND_COLOR)
        match menu:
            case Menu.TITLE:
                text_surface = TITLE_FONT.render("Tractor", True, TEXT_COLOR)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
                screen.blit(text_surface, text_rect)
                if play_button.display(screen):
                    menu = Menu.NAME_PLAYERS
                    game_state: GameState = GameState()
                    moves: list[Move] = game_state.generate_moves()
                    # while game_state.phase != Phase.TRANSITION_ROUNDS:
                    #     if len(moves) == 0:
                    #         game_state.move(Move(Bid(True, None, 0, -1)))
                    #     else:
                    #         game_state.move(moves[random.randint(0, len(moves) - 1)])
                    #     moves = game_state.generate_moves()
                    automatic_pass: bool = False
                    last_move_time: float = pygame.time.get_ticks()
                pygame.display.flip()
                continue
            case Menu.NAME_PLAYERS:
                display_name_players(screen)
                player_names: list[str] = get_player_names()
                if all(len(name) > 0 for name in player_names) and \
                        confirm_names_button.display(screen):
                    game_state.set_player_names(player_names)
                    menu = Menu.GAME
                    if game_state.phase == Phase.TRANSITION_ROUNDS:
                        menu = Menu.ROUND_SUMMARY
                    elif game_state.phase == Phase.GAME_END:
                        menu = Menu.GAME_END
                pygame.display.flip()
                continue
            case Menu.ROUND_SUMMARY:
                display_round_summary(screen, game_state)
                if confirm_end_round_game_button.display(screen):
                    game_state.move(Move(Bid(True, None, 0, -1)))
                    menu = Menu.GAME
                    moves = game_state.generate_moves()
                pygame.display.flip()
                continue
            case Menu.GAME_END:
                display_game_end(screen, game_state)
                if confirm_end_round_game_button.display(screen):
                    menu = Menu.TITLE
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
                        if game_state.phase == Phase.TRANSITION_ROUNDS:
                            menu = Menu.ROUND_SUMMARY
                        elif game_state.phase == Phase.GAME_END:
                            menu = Menu.GAME_END
                pygame.display.flip()


def main() -> None:
    gui_loop()


if __name__ == '__main__':
    main()
