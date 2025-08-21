try:
    # Works when executed as a module: python -m typing_game
    from . import TypingGame
except Exception:
    # Works when executed by pointing Python at the directory: python typing_game\
    from typing_game import TypingGame


def main() -> None:
    game = TypingGame()
    game.run()


if __name__ == "__main__":
    main()


