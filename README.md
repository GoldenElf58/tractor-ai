# Tractor AI

## About Tractor

Tractor (AKA Upgrade/Shengji/升级) is a popular Chinese trick-taking card game. There are many
variants of the game, but the main rules are similar. Go to the
[Wikipedia article](https://en.wikipedia.org/wiki/Sheng_ji) for more information about the game's
rules.

## About This Project

This project is a Python implementation of the game Tractor. Currently, the primary game flow is
implemented, including single, pair, tractor, and consecutive pair trick types. Multi-combination
throws (甩牌) are not currently supported. The long-term goal is to train a machine learning
model to play Tractor.

## Features

* Interactive GUI
* Core game flow (drawing, bidding, kitty, trick-taking, scoring)
* Single, pair, tractor, and consecutive pair trick types
* Legal move generation
* Automatic pass mode (during drawing/bidding phase)
* Cross-platform builds (Windows, macOS, Linux)
* End-of-game scoring screen not yet implemented

![gameplay-recording.gif](gameplay-recording.gif)

## Installation

Follow the steps below to download and run the project on your operating system.

### Windows

Go to the [releases page](https://github.com/GoldenElf58/tractor-ai/releases). Download and run
`tractor-ai-windows.exe`. You're good to go!

### macOS

Go to the [releases page](https://github.com/GoldenElf58/tractor-ai/releases) and download
`tractor-ai-macos.zip`. Intel Macs are currently not supported. Extract the zip file and run
`tractor-ai-macos`. If you get a message that says "Apple could not verify “tractor-ai-macos” is
free of malware that may harm your Mac or compromise your privacy," click "Done". Go to System
Settings/Privacy & Security and scroll down to the Security section. Click "Open Anyway" next to
the message that says "tractor-ai-macos was blocked to protect your app". Click "Open Anyway" one
more time, then type in your password. You're good to go!

### Linux

Go to the [releases page](https://github.com/GoldenElf58/tractor-ai/releases) and download
`tractor-ai-linux.zip`. Extract the zip file and run `tractor-ai-linux`. You're good to go!

## How To Play

This is currently a pass-and-play style game, so after taking a turn, you can pass the computer to
the next player for them to take their turn. Note that after a player finishes their turn, the next
player's hand is shown immediately. If you're playing with others, be sure to hand the computer to
the next player before looking at the screen

### Drawing/Bidding Phase

On your turn, you can always select the "Pass" button to pass the bid. If you want to bid, select
the card in your hand you want to bid and press the "Bid" button. Since this phase has a lot of
passing turns, you can also press the "Auto" button to automatically pass the bid if that is your
only play.

### Burying/Kitty Phase

Select the eight cards from your hand you would like to bury and press the "Discard" button to
confirm.

### Trick-Taking Phase

Select the card or pair of cards you want to play and press the "Play" button.
