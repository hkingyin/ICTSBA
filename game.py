import random
import time
import sqlite3
import os

connect = sqlite3.connect("mastermind.db")
cur = connect.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS records(username VARCHAR(20), level VARCHAR(10), attempts INT, time_taken INT, score INT)")
cur.execute("CREATE TABLE IF NOT EXISTS register(username VARCHAR(20), password VARCHAR(20))")
connect.commit()
connect.close()
cheat = False
current_user = None
username = None
difficulty = None
time_used = None
score = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def register():
    clear_screen()
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()

    reg_username = input('''Enter a username (2-20 characters) or "menu" to return menu page:''')

    if reg_username == 'menu':
        return
    elif not (20 >= len(reg_username) >= 2):
        print('''
Username should be between 2-20 characters.''')
        print('''
Press enter to try again''')
        input()
        return register()

    registered = False
    while True:
        reg_password = input('''
Enter a password (8-20 characters) or "menu" to return menu page:''')
        
        if reg_password == 'menu':
            return
        elif 8 <= len(reg_password) <= 20:
            cur.execute("SELECT username FROM register WHERE username = ?", (reg_username,))
            existing_user = cur.fetchone()
            if existing_user:
                print('''
This username has already been taken.''')
                print('''
Press Enter to try again''')
                registered = True
                input()
                return register()
            else:
                cur.execute("INSERT INTO register VALUES(?,?);", (reg_username, reg_password))
                print('''
Registered successfully''')
                print('''
Press Enter to return menu page''')
                input()
                break 
        else:
            print('''
Password should be between 8-20 characters.''')
            print('''
Press Enter to try again''')
            input()
            clear_screen()
            print(f'''Enter a username (2-20 characters):{reg_username}''')
            continue

    connect.commit()
    connect.close()
    return

def login():
    clear_screen()
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()
    global current_user
    global username
    while True:
        username = input('''Username (enter 'menu' to return menu page):''')
        if username == 'menu':
            return
        password = input('''
Password (enter 'menu' to return menu page):''')
        if password == 'menu':
            return
        cur.execute("SELECT username, password FROM register")
        id = cur.fetchall()
        logged_in = False
        
        if username == "admin" and password == "admin":
            # Enable cheat mode
            global cheat
            cheat = True
            current_user = "admin"
            print('''
Cheat mode enabled.''')
            print('''
Press Enter to return menu page''')
            input()
            break
        else:
            for i in id:
                if i[0] == username and i[1] == password:
                    current_user = "guest"
                    logged_in = True
                    print('''
Logged in successfully.''')
                    print('''
Press Enter to return menu page''')
                    input()
                    return
            else:
                print('''
Invalid username or password.''')
                print('''
Press Enter to try again''')
                input()
                return login()
            
def reset_password():
    clear_screen()
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()

    while True:
        reset_username = input('''Username (enter 'menu' to return menu page):''')
        if reset_username == 'menu':
            return
        reset_pass = input('''
Old password (enter 'menu' to return menu page):''')
        if reset_pass == 'menu':
            return

        cur.execute("SELECT password FROM register WHERE username = ?", (reset_username,))
        match = cur.fetchone()

        if match is None or match[0] != reset_pass:
            print('''
Username not registered or invalid password.''')
            print('''
Press Enter to try again''')
            input()
            return reset_password()

        while True:
            new_password = input('''
New password (enter 'menu' to return menu page):''')
            if new_password == 'menu':
                return
            elif not 8 <= len(new_password) <= 20:
                print('''
Password should be between 8-20 characters.''')
                print('''
Press Enter to try again''')
                input()
                clear_screen()
                print(f'''Username:{reset_username}

Old password:{reset_pass}''')
                continue

            confirm_password = input('''
Confirm new password (enter 'menu' to return menu page):''')
            if confirm_password == 'menu':
                return
            if new_password != confirm_password:
                print('''
The confirm password must match your new password.''')
                print('''
Press Enter to try again''')
                input()
                clear_screen()
                print(f'''Username:{reset_username}

Old password:{reset_pass}''')
                continue

            if confirm_password == reset_pass:
                print('''
Please choose a new password that is different from your old one.''')
                print('''
Press Enter to try again''')
                input()
                clear_screen()
                print(f'''Username:{reset_username}

Old password:{reset_pass}''')
                continue

            cur.execute("UPDATE register SET password = ? WHERE username = ?;", (confirm_password, reset_username))
            print('''
Password reset successfully.''')
            print('''
Press Enter to return menu page''')
            input()
            connect.commit()
            connect.close()
            return

def logout():
    clear_screen()
    global cheat
    global current_user
    cheat = False
    current_user = None
    print("Logged out successfully.")
    print('''
Press Enter to return menu page''')
    input()

def manage_account():
    while True:
        clear_screen()
        print('''- Register (1)
- Log In/Out (2)
- Reset Password (3)
          ''')
        account = input('''Please enter (1-3) or "menu" to return menu page:''')
        if account == '1':
            return register()
        elif account == '2':
            if current_user == None:
                return login()
            else:
                return logout()
        elif account == '3':
            return reset_password()
        elif account == 'menu':
            return
        else:
            print('''
Invalid input.''')
            print('''
Press Enter to try again''')
            input()

def history():
    clear_screen()
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()
    sort_input = input('''Sort by:
- Difficulty levels (1)
- Attempts (2)
- Time taken (3)
- Score (4)
                       
Please enter (1-4) or "menu" to return menu page:''')
    
    if sort_input == 'menu':
        main()
    
    sort_mapping = {
        '1': '''
            CASE level 
                WHEN 'EXPERT' THEN 1 
                WHEN 'NORMAL' THEN 2 
                WHEN 'BEGINNER' THEN 3 
                ELSE 4 
            END''',
        '2': 'attempts',
        '3': 'time_taken',
        '4': 'score DESC'
    }

    sort = sort_mapping.get(sort_input)
    
    if not sort:
        print('''
Invalid sort option.''')
        print('''
Press Enter to try again''')
        input()
        return history()
    
    sql = (f"SELECT * FROM records WHERE username = ? ORDER BY {sort}")
    cur.execute(sql,(username,))
    see_history = cur.fetchall()
    clear_screen()

    print('''
Game History:

     Username     | Difficulty level |     Attempts     |    Time taken    |      Score       |''')
    print("-" * 95)
    for i in see_history:
        print(f"{i[0]:17} | {i[1]:16} | {i[2]:16} | {i[3]:16} | {i[4]:16} |")
    connect.close()
    print('''
Press Enter to return menu page''')
    input()

def scoreboard():
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()
    cur.execute("SELECT username, level, attempts, time_taken, score as score FROM records ORDER BY score DESC LIMIT 10")
    see_scoreboard = cur.fetchall()
    print('''Scoreboard (Top 10):

     Username     | Difficulty level |     Attempts     |    Time taken    |      Score       |''')
    print("-" * 95)
    for i in see_scoreboard:
        print(f"{i[0]:17} | {i[1]:16} | {i[2]:16} | {i[3]:16} | {i[4]:16} |")
    connect.close()
    print('''
Press Enter to return menu page''')
    input()

# Start the timer and return the start time
def start_timer(duration):
    start_time = time.time()
    print(f'''You have {duration} seconds to guess the secret code.''')
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

# Set the custom difficulty settings
def set_custom_difficulty():
    clear_screen()
    DIFFICULTY_LEVELS['CUSTOM'] = {'NUM_COLORS': 0, 'MAX_ATTEMPTS': 0, 'TIME_LIMIT': 0}

    while True:
            num_colors = (input('''Enter the number of colors in the secret code (4-5) or "menu" to return menu page:'''))
            if num_colors.lower() == 'menu':
                return main()
            try:
                num_colors = int(num_colors)
                if 4 <= num_colors <= 5:
                    DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS'] = num_colors
                    break
                else:
                    print('''
Invalid range for secret code length. Input value should be between 4-5.''')
                    print('''
Press Enter to try again''')
                    input()
                    return set_custom_difficulty()
            
            except ValueError:
                print('''
Invalid input. Please enter a number.''')
                print('''
Press Enter to try again''')
                input()
                return set_custom_difficulty()

    while True:
        max_attempts = (input('''
Enter the maximum number of attempts (1-20) or "menu" to return menu page:'''))
        if max_attempts.lower() == 'menu':
                return main()
        try:
            max_attempts = int(max_attempts)
            if 1 <= max_attempts <= 20:
                DIFFICULTY_LEVELS['CUSTOM']['MAX_ATTEMPTS'] = max_attempts
                break
            else:
                print('''
Invalid range of maximum number of attempts. Input value should be between 1-20.''')
                print('''
Press Enter to try again''')
                input()
                clear_screen()
                print(f'''Enter the number of colors in the secret code (4-6):{DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS']}''')
        except ValueError:
            print('''
Invalid input. Please enter a number.''')
            print('''
Press Enter to try again''')
            input()
            clear_screen()
            print(f'''Enter the number of colors in the secret code (4-6):{DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS']}''')

    while True:
        time_limit = (input('''
Enter the time limit in seconds (30-300) or "menu" to return menu page:'''))
        if time_limit.lower() == 'menu':
                return main()
        try:
            time_limit = int(time_limit)
            if 30 <= time_limit <= 300:
                DIFFICULTY_LEVELS['CUSTOM']['TIME_LIMIT'] = time_limit
                break
            else:
                print('''
Invalid range of time limit. Input value should be between 30-300.''')
                print('''
Press Enter to try again''')
                input()
                clear_screen()
                print(f'''Enter the number of colors in the secret code (4-6):{DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS']}

Enter the maximum number of attempts (1-20):{DIFFICULTY_LEVELS['CUSTOM']['MAX_ATTEMPTS']}''')
        except ValueError:
            print('''
Invalid input. Please enter a number.''')
            print('''
Press Enter to try again''')
            input()
            clear_screen()
            print(f'''Enter the number of colors in the secret code (4-6):{DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS']}

Enter the maximum number of attempts (1-20):{DIFFICULTY_LEVELS['CUSTOM']['MAX_ATTEMPTS']}''')

    return 'CUSTOM'

# Generate a random secret code
def generate_secret_code(num_colors):
    secret_code = random.sample(colors, num_colors)
    return secret_code

# Get the player's guess
def get_player_guess(num_colors):
    if DIFFICULTY_LEVELS['BEGINNER']['NUM_COLORS'] == num_colors or DIFFICULTY_LEVELS['NORMAL']['NUM_COLORS'] == num_colors:
        while True:
            guess = input(f'''
Enter your {num_colors}-color guess (e.g., RGBY) or 'menu' to quit:''').upper()
            if guess == 'MENU':
                return ['MENU']
            elif len(guess) == num_colors and all(color in colors for color in guess) and len(set(guess)) == len(guess):
                return list(guess)
            elif len(guess) == num_colors and all(color in colors for color in guess) and len(set(guess)) != len(guess):
                print('''
No duplicate colors is allowed.''')
            else:
                print('''
Invalid guess. Please try again.''')
    elif DIFFICULTY_LEVELS['EXPERT']['NUM_COLORS'] == num_colors:
        while True:
            guess = input(f'''
Enter your {num_colors}-color guess (e.g., RGBYP) or 'menu' to quit:''').upper()
            if guess == 'MENU':
                return ['MENU']
            elif len(guess) == num_colors and all(color in colors for color in guess) and len(set(guess)) == len(guess):
                return list(guess)
            elif len(guess) == num_colors and all(color in colors for color in guess) and len(set(guess)) != len(guess):
                print('''
No duplicate colors is allowed.''')
            else:
                print('''
Invalid guess. Please try again.''')


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

# Display the guess history table
def display_guess_history(guess_history):
    print("\nGuess History:")
    print("Round | Guess | Black Pins | White Pins |")
    print("-" * 41)
    for round_num, guess, black_pins, white_pins in guess_history:
        print(f"{round_num:5} | {guess:5} | {black_pins:10} | {white_pins:10} |")
    print()

# Choose the game difficulty level
def choose_difficulty():
    if current_user == "admin":
        return "CHEAT"
    else:
        while True:
            print('''Select the difficulty level:
- Beginner (1)
- Normal (2)
- Expert (3)
- Custom (4)
''')
            
            choice = input("Enter your choice (1-4) or 'menu' to return menu page: ")

            if choice == '1':
                return 'BEGINNER'
            elif choice == '2':
                return 'NORMAL'
            elif choice == '3':
                return 'EXPERT'
            elif choice == '4':
                return 'CUSTOM'
            elif choice == 'menu':
                return None
            elif cheat == True:
                return 'CHEAT'
            else:
                print('''
Invalid input.''')
                print('''
Press Enter to try again''')
                input()
                clear_screen()

# Get the player's guess
def play_game():
    difficulty = choose_difficulty()
    if difficulty is None:
        return
    if difficulty == 'CUSTOM':
        custom_difficulty_result = set_custom_difficulty()
        if custom_difficulty_result == 'MENU':
            return  # Exit if the user chooses to go back to menu

        if custom_difficulty_result is not None:
            difficulty = custom_difficulty_result  # Update the difficulty if set successfully
    clear_screen()
    
    max_attempts = DIFFICULTY_LEVELS[difficulty]['MAX_ATTEMPTS']
    secret_code = generate_secret_code(DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'])
    attempts = 0
    guess_history = []
    start_time = start_timer(DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT'])
    print(f"You have {max_attempts} attempts to guess the secret code.")
    print(f"colors code available : R, G, B, Y, O, P ")
    if cheat:
        print(f"The secret code is: {secret_code}")

    while attempts < max_attempts and not check_time_limit(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']):
        guess = get_player_guess(DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'])
        
        if guess == ['MENU']:
            return

        black_pins, white_pins = evaluate_guess(secret_code, guess)
        guess_history.append((attempts + 1, ''.join(guess), black_pins, white_pins))
        
        clear_screen()
        
        remaining_attempts = max_attempts - (attempts + 1)
        
        if not cheat:
            print(f"Time remaining: {int(time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))} seconds")
            print(f"Attempts left: {remaining_attempts}")

        if cheat:
            print(f"The secret code is: {secret_code}")
        
        if black_pins != DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'] :
            display_guess_history(guess_history)
            print(f"colors code available : R, G, B, Y, O, P ")

        if difficulty == 'BEGINNER':
            level_score = 0.5
        elif difficulty == 'NORMAL':
            level_score = 1
        elif difficulty == 'EXPERT':
            level_score = 2
        
        if not cheat and black_pins == DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'] and difficulty != 'CUSTOM' and current_user == "guest":
            score = int((100 + remaining_attempts * 10 + time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))) * level_score
            display_guess_history(guess_history)
            print(f'''Congratulations! You cracked the secret code.
Your score = {score}''')
            time_taken = int(DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT'] - time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))
            record_game(username, difficulty, attempts + 1, time_taken, score)
            print('''
Game history recorded''')
            print('''
Press Enter to return menu page''')
            input()
            return
        
        if not cheat and black_pins == DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'] and difficulty != 'CUSTOM' and current_user == None:
            score = int((100 + remaining_attempts * 10 + time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))) * level_score
            display_guess_history(guess_history)
            print(f'''Congratulations! You cracked the secret code.
Your score = {score}''')
            print('''
Press Enter to return menu page''')
            input()
            return

        if difficulty == 'CUSTOM' and black_pins == DIFFICULTY_LEVELS[difficulty]['NUM_COLORS']:
            display_guess_history(guess_history)
            print('''
Congratulations! You cracked the secret code.''')
            print('''
Press Enter to return menu page''')
            input()
            return
        
        if cheat and black_pins == 5:
            display_guess_history(guess_history)
            print('''
Congratulations! You cracked the secret code.''')
            print('''
Press Enter to return menu page''')
            input()
            return
        

        attempts += 1

    if check_time_limit(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']):
        print(f'''
Sorry, you ran out of time. The secret code was {''.join(secret_code)}''')
        print('''
Press Enter to return menu page''')
        input()
        return
    else:
        print(f'''
Sorry, you ran out of attempts. The secret code was {''.join(secret_code)}''')
        print('''
Press Enter to return menu page''')
        input()
        return

def record_game(username, difficulty, attempts, time_taken, score):
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()
    cur.execute("INSERT INTO records VALUES(?,?,?,?,?)", (username, difficulty, attempts, time_taken, score))
    connect.commit()
    connect.close()

def print_game_rules():
    print('''Welcome to Mastermind! Here are the rules you need to know:
          
[Difficulty Levels]
          
Beginner:
Secret code: 4 colored beads from 6 available colors
Maximum attempts: 10
Time limit: 2 minutes
          
Normal:
Secret code: 4 colored beads from 6 available colors
Maximum attempts: 8
Time limit: 1.5 minutes
          
Expert:
Secret code: 5 colored beads from 6 available colors
Maximum attempts: 6
Time limit: 1 minute
          
[Gameplay]
          
After each guess, you will receive feedback:
- Black Bead: A color is correct and in the correct position.
- White Bead: A color is correct but in the wrong position.
          
[Objective]
          
Your goal is to guess the secret code within the allowed attempts and time. Good luck!
    
Press Enter to return menu page''')
    input()

# Main function to run the Mastermind game
def main():
    while True:
        clear_screen()
        print('''Welcome to the Mastermind game!
              
- Play Game (1)
- Game Rules (2)
- Manage Your Account (3)
- History (4)
- Scoreboard (5)
- Exit Game (6)
          ''')

        user_input = input("Please enter (1-6): ")
        clear_screen()

        if user_input == '1':
            play_game()
        elif user_input == '2':
            print_game_rules()
        elif user_input == '3':
            manage_account()
        elif user_input == '4':
            if current_user == None:
                print('''
You must log in to see history. Press Enter to return menu page''')
                input()
            elif current_user == "admin":
                print('''
Please log in as "guest" to see history. Press Enter to return menu page''')
                input()
            else:
                history()
        elif user_input == '5':
            scoreboard()
        elif user_input == '6':
            print("Goodbye!")
            break
        else:
            print('''Invalid input.''')
            print('''
Press Enter to try again''')
            input()

if __name__ == "__main__":
    main()