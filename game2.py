import random
import time

# Start the timer and return the start time
def start_timer(duration):
    start_time = time.time()
    print(f"You have {duration} seconds to guess the secret code.")
    return start_time

# Calculate the remaining time
def time_remaining(start_time, duration):
    elapsed_time = time.time() - start_time
    return max(0, duration - elapsed_time)

# Check if the time limit has been reached
def check_time_limit(start_time, duration):
    return time_remaining(start_time, duration) <= 0

# Define the available colors
colors = ['R', 'G', 'B', 'Y', 'P', 'O']

# Define the difficulty levels
DIFFICULTY_LEVELS = {
    'BEGINNER': {'NUM_COLORS': 4, 'MAX_ATTEMPTS': 10, 'TIME_LIMIT': 120},
    'NORMAL': {'NUM_COLORS': 4, 'MAX_ATTEMPTS': 8, 'TIME_LIMIT': 90},
    'EXPERT': {'NUM_COLORS': 5, 'MAX_ATTEMPTS': 6, 'TIME_LIMIT': 60},
    'CHEAT': {'NUM_COLORS': 5, 'MAX_ATTEMPTS': float('inf'), 'TIME_LIMIT': float('inf')}
}

# Generate a random secret code
def generate_secret_code(num_colors):
    secret_code = random.sample(colors, num_colors)
    return secret_code

# Get the player's guess
def get_player_guess(num_colors):
    if DIFFICULTY_LEVELS['BEGINNER']['NUM_COLORS'] == num_colors or DIFFICULTY_LEVELS['NORMAL']['NUM_COLORS'] == num_colors:
        while True:
            guess = input(f"Enter your {num_colors}-color guess (e.g., RGBY) or 'exit' to quit: ").upper()
            if guess == 'EXIT':
                return ['EXIT']
            elif len(guess) == num_colors and all(color in colors for color in guess):
                return list(guess)
            else:
                print("Invalid guess. Please try again.")
    elif DIFFICULTY_LEVELS['EXPERT']['NUM_COLORS'] == num_colors:
        while True:
            guess = input(f"Enter your {num_colors}-color guess (e.g., RGBYP) or 'exit' to quit: ").upper()
            if guess == 'EXIT':
                return ['EXIT']
            elif len(guess) == num_colors and all(color in colors for color in guess):
                return list(guess)
            else:
                print("Invalid guess. Please try again.")


# Evaluate the player's guess and return the feedback
def evaluate_guess(secret_code, guess):
    black_pins = 0
    white_pins = 0
    remaining_secret = secret_code[:]
    remaining_guess = guess[:]

    # Count the number of correct colors in the correct position
    for i in range(len(secret_code)):
        if guess[i] == secret_code[i]:
            black_pins += 1
            remaining_secret[i] = None
            remaining_guess[i] = None

    # Count the number of correct colors in the wrong position
    for color in remaining_guess:
        if color in remaining_secret:
            white_pins += 1
            remaining_secret[remaining_secret.index(color)] = None
    white_pins = white_pins - black_pins
    return black_pins, white_pins

# Get the player's guess
def play_game():
    difficulty = choose_difficulty()
    secret_code = generate_secret_code(DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'])
    attempts = 0
    guess_history = []
    start_time = start_timer(DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT'])

    while attempts < DIFFICULTY_LEVELS[difficulty]['MAX_ATTEMPTS'] and not check_time_limit(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']):
        guess = get_player_guess(DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'])
        
        # Check if the player wants to exit the game
        if guess == ['EXIT']:
            print("Exiting the game...")
            return

        black_pins, white_pins = evaluate_guess(secret_code, guess)
        guess_history.append((attempts + 1, ''.join(guess), black_pins, white_pins))
        
        print(f"Your guess: {''.join(guess)}")
        print(f"Feedback: {black_pins} black pin(s), {white_pins} white pin(s)")
        print(f"Time remaining: {int(time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))} seconds")

        display_guess_history(guess_history)

        if black_pins == DIFFICULTY_LEVELS[difficulty]['NUM_COLORS']:
            print("Congratulations! You cracked the secret code.")
            return

        attempts += 1

    if check_time_limit(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']):
        print(f"Sorry, you ran out of time. The secret code was {''.join(secret_code)}.")
    else:
        print(f"Sorry, you ran out of attempts. The secret code was {''.join(secret_code)}.")

    display_guess_history(guess_history)

# Choose the game difficulty level
def choose_difficulty():
    while True:
        print("Select the difficulty level:")
        print("1. Beginner")
        print("2. Normal")
        print("3. Expert")
        print("4. Cheat")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            return 'BEGINNER'
        elif choice == '2':
            return 'NORMAL'
        elif choice == '3':
            return 'EXPERT'
        elif choice == '4':
            return 'CHEAT'
        else:
            print("Invalid input. Please try again.")

# Display the guess history table
def display_guess_history(guess_history):
    print("\nGuess History:")
    print("Round | Guess | Black Pins | White Pins |")
    print("-" * 41)
    for round_num, guess, black_pins, white_pins in guess_history:
        print(f"{round_num:5} | {guess:5} | {black_pins:10} | {white_pins:10} |")
    print()

# Main function to run the Mastermind game
def main():
    while True:
        print('''
    Welcome to the Mastermind game!
    - Start Game (1)
    - Game Rules (2)
    - Exit Game (3)
          ''')

        user_input = input("Please enter (1-3): ")

        if user_input == '1':
            play_game()
        elif user_input == '2':
            print_game_rules()
        elif user_input == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid input. Please try again.")

def print_game_rules():
    print('''
    There are four difficulty levels in the Mastermind game:

    Beginner:
    - The secret code consists of 4 colored beads out of 6 available colors.
    - You have a maximum of 10 attempts to guess the secret code.
    - You have a maximum of 2 minutes to guess the secret code.

    Normal:
    - The secret code consists of 4 colored beads out of 6 available colors.
    - You have a maximum of 8 attempts to guess the secret code.
    - You have a maximum of 1.5 minutes to guess the secret code.

    Expert:
    - The secret code consists of 5 colored beads out of 6 available colors.
    - You have a maximum of 6 attempts to guess the secret code.
    - You have a maximum of 1 minute to guess the secret code.

    Cheat:
    - The secret code is revealed to you(for testing).
    - You have an unlimited number of attempts and no time limit.

    After each guess, you will receive immediate feedback using black and white hint beads:
    - A black bead indicates that a color in the player's guess is correct and in the correct position.
    - A white bead indicates that a color in the player's guess is correct but in the wrong position.
    ''')

if __name__ == "__main__":
    main()