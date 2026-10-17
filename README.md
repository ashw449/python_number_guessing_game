# Number Guessing Game

A web-based number guessing game built with **Python and Flask**. The application generates a random secret number, and the player must guess it within a limited number of attempts. Guess correctly to win; run out of attempts, and it's **Game Over!**

## Features

- **Configurable Guess Limit:** Set the number of allowed guesses, with a default of 5 attempts.
- **Configurable Number Range:** Customize the minimum and maximum values for the secret number, with a default range of 10 to 100.
- **Maximum Guess Cap:** Prevents players from exceeding the configured guess limit.
- **Graceful Invalid Input Handling:** Invalid entries do not count as attempts or penalize the player.
- **Game State Tracking:** Uses Flask cookies to persist game progress.
- **Restart Option:** Start a new game at any time.

## Technologies Used

- **Python 3** – Core game logic and random number generation.
- **Flask** – Web application framework and session management.
- **HTML** – Structures the game interface.
- **CSS** – Styles the user interface.

## Objective

Guess the secret number within the allowed number of attempts. Use the feedback provided by the game to guide your next guess and try to win before your attempts run out.
