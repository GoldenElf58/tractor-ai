# Tractor AI

## About Tractor

Tractor (AKA Upgrade/Shengji/升级) is a popular Chinese trick-taking card game. There are many
variants of the game, but the main rules are similar. Go to the
[Wikipedia article](https://en.wikipedia.org/wiki/Sheng_ji) for more information about the game's
rules.

## About This Project

This project is a Python implementation of the game Tractor. The project is still under development.
As of now, the core game implementation is complete, but edge cases are still being tested.
In the future, I will use this project to train a machine learning model to play tractor.

## Features

- Full implementation of Tractor (note that the game is complete, but not fully tested)
- Supports 4 players
- Command-line interface
- Legal move generation

## Installation

Follow the steps below to download and run the project on your operating system.

### Windows

Go to the [releases page](https://github.com/GoldenElf58/tractor-ai/releases). Download and run
`tractor-ai-windows.exe`. You're good to go!

### macOS

Go to the [releases page](https://github.com/GoldenElf58/tractor-ai/releases) and download
`tractor-ai-macos.zip`. Intel macs are currently not supported. Extract the zip file and run
`tractor-ai-macos`. If you get a message that says "Apple could not verify “tractor-ai-macos” is
free of malware that may harm your Mac or compromise your privacy," click "Done". Go to System
Settings/Privacy & Security and scroll down to the Security section. Click "Open Anyway" next to
the message that says "tractor-ai-macos was blocked to protect your app". Click "Open Anyway" one
more time, then type in your password. You're good to go!

### Linux

Go to the [releases page](https://github.com/GoldenElf58/tractor-ai/releases) and download
`tractor-ai-linux.zip`. Extract the zip file and run `tractor-ai-linux`. You're good to go!

## How To Play

Once you start the game, each player will be prompted to make a move. For example:

```
Player 1 move
Hand: Jack of Spades, 3 of Hearts, 5 of Hearts, Queen of Hearts, 7 of Diamonds, 8 of Diamonds, Queen of Diamonds, Ace of Diamonds, Queen of Clubs, Little Joker, Little Joker
Available Moves:
1 : Pass
2 : Pair of Little Joker

Enter move index or command:
```

Then, simply enter the index of the move you want to make. If you want more information about the
game you can type "i" or "info" to view that information. For example:

```
Enter move index or command: info
Game Phase: Drawing Phase
Dominant Rank: 2
Bid: 2 of Hearts
Bid Owner: 3

Enter move index or command:
```

If you want information about other commands available, you can type "h" or "help".

```
Enter move index or command: help
Commands:
'h' or 'help' - Views this help message.
'q' or 'quit' - Quits the game.
'i' or 'info' - Views the current game state.
'' - Makes the first move (typing nothing).
'a' or 'auto' - Toggles automatic move mode. This will automatically make a move for you if there is only one possible move.
```
