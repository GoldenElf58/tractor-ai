from game import Card, Bid, Play, GameState, Phase


def main() -> None:
    game_state = GameState()
    auto: bool = False
    while game_state.is_in_progress():
        moves: list[Bid | Card | Play] = game_state.generate_moves()
        print(f"Player {game_state.active_player} move")
        print(f"Hand: {game_state.show_current_hand()}")
        if game_state.phase == Phase.TRICK_TAKING:
            print(f"Current Trick: {game_state.show_current_trick()}")
        print("Available moves:")
        print(''.join(f"{i} : {move}\n" for i, move in enumerate(moves)))
        move: int = 0
        while not auto or len(moves) > 1:
            move_str = input("Enter move index: ").lower()
            if move_str == "": break
            if move_str == "a" or move_str == "auto":
                auto = not auto
                print(f"Auto mode: {auto}")
                continue
            if move_str == "h" or move_str == "help":
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
            if move_str.isnumeric():
                move = int(move_str)
                if 0 <= move < len(moves): break
        game_state.move(moves[move])


if __name__ == '__main__':
    main()
