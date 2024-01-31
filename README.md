# Yu-Gi-Oh! Solitaire Playtesting

## Overview

Welcome to the Yu-Gi-Oh! Solitaire Playtesting program, a Python project using pygame to create a playtesting environment for the card game Yu-Gi-Oh! This simulator allows players to test their decks, strategies, and skills in a virtual environment.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [How to Run](#how-to-run)
- [Controls](#controls)
- [Acknowledgements](#acknowledgements)

## Features

- **Card Game Simulation:** Simulate the Yu-Gi-Oh! card game with a user-friendly interface.
- **Deck Importing:** Import decks easily by dragging the .ydk file to the Decks/ directory.
    - Uses the ygoprodeck.com API to download card images by reading the .ydk file.

## Requirements

- Python 3.x
- pygame library (install via `pip install pygame`)

## How to Run

1. Clone the repository: `git clone https://github.com/your-username/yugioh-card-simulator.git`
2. Navigate to the project directory: `cd Yu-Gi-Oh`
3. Install dependencies.
4. Run the program: `./ playtest.py`

## Controls

- **Mouse Clicks:** Interact with cards, buttons, and game elements.
- **Keyboard Shortcuts:**
  - `Enter/Return:` Confirm actions.
  - `Esc:` Open/close in-game menus.
  - `H:` Add a card to the hand.
  - `F:` Send a card to the field.
  - `G:` Send a card to the graveyard.
  - `B:` Send a card to the banishment.
  - `D:` Send a card to the deck.
  - `R:` Rotate a selected card.

## Acknowledgements

- [pygame](https://www.pygame.org/): The library used for creating the graphical interface.
- [Yu-Gi-Oh! Official Website](https://www.yugioh-card.com/): For inspiration and reference on card game rules.
- [YGOPRODeck](https://ygoprodeck.com/): For the free API used to download card images.

