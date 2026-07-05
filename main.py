from game import Card, Bid, Play, GameState, Phase

HELP_TEXT: str = ("Commands:\n"
                  "'h' or 'help' - Views this help message.\n"
                  "'i' or 'info' - Views the current game state.\n"
                  "'q' or 'quit' - Quits the game.\n"
                  "'' - Makes the first move (typing nothing).\n"
                  "'a' or 'auto' - Toggles automatic move mode. This will "
                  "automatically make a move for you if there is only one possible move.\n"
                  )


def game_loop() -> None:
    game_state = GameState()
    auto: bool = False
    while game_state.is_in_progress():
        moves: list[Bid | Card | Play] = game_state.generate_moves()
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
    main()
