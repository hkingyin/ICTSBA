import random
import time
import sqlite3
import os
import colorama
from colorama import Fore, Style
colorama.init(autoreset=True)

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
ORANGE = "\033[38;5;214m"

RAINBOW_COLORS = [
    Fore.RED,
    Fore.YELLOW,
    Fore.GREEN,
    Fore.CYAN,
    Fore.MAGENTA
]

def print_rainbow_text(text):
    rainbow_text = ""
    color_index = 0
    for char in text:
        rainbow_text += RAINBOW_COLORS[color_index] + char
        color_index = (color_index + 1) % len(RAINBOW_COLORS)
    print(rainbow_text + Style.RESET_ALL)


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
        print(Fore.RED + '''
Username should be between 2-20 characters.''' + Style.RESET_ALL)
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
                print(Fore.RED + '''
This username has already been taken.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
                registered = True
                input()
                return register()
            else:
                cur.execute("INSERT INTO register VALUES(?,?);", (reg_username, reg_password))
                print(Fore.GREEN + '''
Registered successfully''' + Style.RESET_ALL)
                break 
        else:
            print(Fore.RED + '''
Password should be between 8-20 characters.''' + Style.RESET_ALL)
            print('''
Press enter to try again''')
            input()
            clear_screen()
            print(f'''Enter a username (2-20 characters) or "menu" to return menu page:{reg_username}''')
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
            global cheat
            cheat = True
            current_user = "admin"
            print(Fore.GREEN + '''
Cheat mode enabled.''' + Style.RESET_ALL)
            print('''
Press enter to return menu page''')
            input()
            break
        else:
            for i in id:
                if i[0] == username and i[1] == password:
                    current_user = "guest"
                    logged_in = True
                    print(Fore.GREEN + '''
Logged in successfully.''' + Style.RESET_ALL)
                    print('''
Press enter to return menu page''')
                    input()
                    return
                else:
                    print(Fore.RED + '''
    Invalid username or password.''' + Style.RESET_ALL)
                    print('''
    Press enter to try again''')
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
            print(Fore.RED + '''
Username not registered or invalid password.''' + Style.RESET_ALL)
            print('''
Press enter to try again''')
            input()
            return reset_password()

        while True:
            new_password = input('''
New password (enter 'menu' to return menu page):''')
            if new_password == 'menu':
                return
            elif not 8 <= len(new_password) <= 20:
                print(Fore.RED + '''
Password should be between 8-20 characters.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
                input()
                clear_screen()
                print(f'''Username (enter 'menu' to return menu page):{reset_username}

Old password (enter 'menu' to return menu page):{reset_pass}''')
                continue

            confirm_password = input('''
Confirm new password (enter 'menu' to return menu page):''')
            if confirm_password == 'menu':
                return
            if new_password != confirm_password:
                print(Fore.RED + '''
The confirm password must match your new password.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
                input()
                clear_screen()
                print(f'''Username (enter 'menu' to return menu page):{reset_username}

Old password (enter 'menu' to return menu page):{reset_pass}''')
                continue

            if confirm_password == reset_pass:
                print(Fore.RED + '''
Please choose a new password that is different from your old one.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
                input()
                clear_screen()
                print(f'''Username (enter 'menu' to return menu page):{reset_username}

Old password (enter 'menu' to return menu page):{reset_pass}''')
                continue

            cur.execute("UPDATE register SET password = ? WHERE username = ?;", (confirm_password, reset_username))
            print(Fore.GREEN + '''
Password reset successfully.''' + Style.RESET_ALL)
            print('''
Press enter to return menu page''')
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
    print(Fore.GREEN + "Logged out successfully." + Style.RESET_ALL)
    print('''
Press enter to return menu page''')
    input()

def manage_account():
    while True:
        clear_screen()
        print('''- Register (1)
- Log in/out (2)
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
            print(Fore.RED + '''
Invalid input.''' + Style.RESET_ALL)
            print('''
Press enter to try again''')
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
        print(Fore.RED + '''
Invalid sort option.''' + Style.RESET_ALL)
        print('''
Press enter to try again''')
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
Press enter to return menu page''')
    input()

def scoreboard():
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()
    cur.execute("SELECT username, level, attempts, time_taken, score as score FROM records ORDER BY score DESC LIMIT 10")
    see_scoreboard = cur.fetchall()
    print('''
Scoreboard (Top 10):

     Username     | Difficulty level |     Attempts     |    Time taken    |      Score       |''')
    print("-" * 95)
    for i in see_scoreboard:
        print(f"{i[0]:17} | {i[1]:16} | {i[2]:16} | {i[3]:16} | {i[4]:16} |")
    connect.close()
    print('''
Press enter to return menu page''')
    input()

def start_timer(duration):
    start_time = time.time()
    print(f'''You have {Fore.CYAN}{duration}{Style.RESET_ALL} seconds to guess the secret code.''')
    return start_time

def time_remaining(start_time, duration):
    elapsed_time = time.time() - start_time
    return max(0, duration - elapsed_time)

def check_time_limit(start_time, duration):
    return time_remaining(start_time, duration) <= 0

colors = ['R', 'G', 'B', 'Y', 'P', 'O']

DIFFICULTY_LEVELS = {
    'BEGINNER': {'NUM_COLORS': 4, 'MAX_ATTEMPTS': 10, 'TIME_LIMIT': 120},
    'NORMAL': {'NUM_COLORS': 4, 'MAX_ATTEMPTS': 8, 'TIME_LIMIT': 90},
    'EXPERT': {'NUM_COLORS': 5, 'MAX_ATTEMPTS': 6, 'TIME_LIMIT': 60},
    'CHEAT': {'NUM_COLORS': 5, 'MAX_ATTEMPTS': float('inf'), 'TIME_LIMIT': float('inf')}
}

def set_custom_difficulty():
    clear_screen()
    DIFFICULTY_LEVELS['CUSTOM'] = {'NUM_COLORS': 0, 'MAX_ATTEMPTS': 0, 'TIME_LIMIT': 0}

    while True:
            num_colors = (input('''Enter the number of colors in the secret code (4-6) or "menu" to return menu page:'''))
            if num_colors.lower() == 'menu':
                return main()
            try:
                num_colors = int(num_colors)
                if 4 <= num_colors <= 6:
                    DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS'] = num_colors
                    break
                else:
                    print(Fore.RED + '''
Invalid number of colors.''' + Style.RESET_ALL)
                    print('''
Press enter to try again''')
                    input()
                    return set_custom_difficulty()
            
            except ValueError:
                print(Fore.RED + '''
Invalid input. Please enter a number.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
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
                print(Fore.RED + '''
Invalid number of attempts.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
                input()
                clear_screen()
                print(f'''Enter the number of colors in the secret code (4-6):{DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS']}''')
        except ValueError:
            print(Fore.RED + '''
Invalid input. Please enter a number.''' + Style.RESET_ALL)
            print('''
Press enter to try again''')
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
                print(Fore.RED + '''
Invalid time limit.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
                input()
                clear_screen()
                print(f'''Enter the number of colors in the secret code (4-6):{DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS']}

Enter the maximum number of attempts (1-20):{DIFFICULTY_LEVELS['CUSTOM']['MAX_ATTEMPTS']}''')
        except ValueError:
            print(Fore.RED + '''
Invalid input. Please enter a number.''' + Style.RESET_ALL)
            print('''
Press enter to try again''')
            input()
            clear_screen()
            print(f'''Enter the number of colors in the secret code (4-6):{DIFFICULTY_LEVELS['CUSTOM']['NUM_COLORS']}

Enter the maximum number of attempts (1-20):{DIFFICULTY_LEVELS['CUSTOM']['MAX_ATTEMPTS']}''')

    return 'CUSTOM'

def generate_secret_code(num_colors):
    secret_code = random.sample(colors, num_colors)
    return secret_code

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
                print(Fore.RED + '''
No duplicate colors is allowed.''' + Style.RESET_ALL)
            else:
                print(Fore.RED + '''
Invalid guess. Please try again.''' + Style.RESET_ALL)
    elif DIFFICULTY_LEVELS['EXPERT']['NUM_COLORS'] == num_colors:
        while True:
            guess = input(f'''
Enter your {num_colors}-color guess (e.g., RGBYP) or 'menu' to quit:''').upper()
            if guess == 'MENU':
                return ['MENU']
            elif len(guess) == num_colors and all(color in colors for color in guess) and len(set(guess)) == len(guess):
                return list(guess)
            elif len(guess) == num_colors and all(color in colors for color in guess) and len(set(guess)) != len(guess):
                print(Fore.RED + '''
No duplicate colors is allowed.''' + Style.RESET_ALL)
            else:
                print(Fore.RED + '''
Invalid guess. Please try again.''' + Style.RESET_ALL)


def evaluate_guess(secret_code, guess):
    black_pins = 0
    white_pins = 0
    remaining_secret = secret_code[:]
    remaining_guess = guess[:]

    for i in range(len(secret_code)):
        if guess[i] == secret_code[i]:
            black_pins += 1
            remaining_secret[i] = None
            remaining_guess[i] = None

    for color in remaining_guess:
        if color in remaining_secret:
            white_pins += 1
            remaining_secret[remaining_secret.index(color)] = None
    white_pins = white_pins - black_pins
    return black_pins, white_pins

def display_guess_history(guess_history):
    print("\nGuess History:")
    print("Round | Guess | Black Pins | White Pins |")
    print("-" * 41)
    for round_num, guess, black_pins, white_pins in guess_history:
        print(f"{round_num:5} | {guess:5} | {black_pins:10} | {white_pins:10} |")
    print()

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
                print(Fore.RED + '''
Invalid input.''' + Style.RESET_ALL)
                print('''
Press enter to try again''')
                input()
                clear_screen()

def play_game():
    difficulty = choose_difficulty()
    if difficulty is None:
        return
    if difficulty == 'CUSTOM':
        custom_difficulty_result = set_custom_difficulty()
        if custom_difficulty_result == 'MENU':
            return 

        if custom_difficulty_result is not None:
            difficulty = custom_difficulty_result 
    clear_screen()
    
    max_attempts = DIFFICULTY_LEVELS[difficulty]['MAX_ATTEMPTS']
    secret_code = generate_secret_code(DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'])
    attempts = 0
    guess_history = []
    start_time = start_timer(DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT'])
    print(f"You have {Fore.CYAN}{max_attempts}{Style.RESET_ALL} attempts to guess the secret code.")
    print(f"Colors code available : {Fore.RED}R{Style.RESET_ALL}, {Fore.GREEN}G{Style.RESET_ALL}, {Fore.CYAN}B{Style.RESET_ALL}, {Fore.YELLOW}Y{Style.RESET_ALL}, {ORANGE}O{Style.RESET_ALL}, {Fore.MAGENTA}P{Style.RESET_ALL} ")
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
            print(f"Time remaining: {Fore.CYAN}{int(time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))}{Style.RESET_ALL} seconds")
            print(f"Attempts left: {Fore.CYAN}{remaining_attempts}{Style.RESET_ALL}")

        if cheat:
            print(f"The secret code is: {secret_code}")
        
        if black_pins != DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'] :
            display_guess_history(guess_history)
            print(f"Colors code available : {Fore.RED}R{Style.RESET_ALL}, {Fore.GREEN}G{Style.RESET_ALL}, {Fore.CYAN}B{Style.RESET_ALL}, {Fore.YELLOW}Y{Style.RESET_ALL}, {ORANGE}O{Style.RESET_ALL}, {Fore.MAGENTA}P{Style.RESET_ALL} ")

        if difficulty == 'BEGINNER':
            level_score = 0.5
        elif difficulty == 'NORMAL':
            level_score = 1
        elif difficulty == 'EXPERT':
            level_score = 2
        
        if not cheat and black_pins == DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'] and difficulty != 'CUSTOM' and current_user == "guest":
            score = int((100 + remaining_attempts * 10 + time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))) * level_score
            display_guess_history(guess_history)
            print(f'''{Fore.GREEN}Congratulations! You cracked the secret code.{Style.RESET_ALL}
Your score = {score}''')
            time_taken = int(DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT'] - time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))
            record_game(username, difficulty, attempts + 1, time_taken, score)
            print(Fore.GREEN + '''
Game history recorded''' + Style.RESET_ALL)
            print('''
Press enter to return menu page''')
            input()
            return
        
        if not cheat and black_pins == DIFFICULTY_LEVELS[difficulty]['NUM_COLORS'] and difficulty != 'CUSTOM' and current_user == None:
            score = int((100 + remaining_attempts * 10 + time_remaining(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']))) * level_score
            display_guess_history(guess_history)
            print(f'''{Fore.GREEN}Congratulations! You cracked the secret code.{Style.RESET_ALL}
Your score = {score}''')
            print('''
Press enter to return menu page''')
            input()
            return

        if difficulty == 'CUSTOM' and black_pins == DIFFICULTY_LEVELS[difficulty]['NUM_COLORS']:
            display_guess_history(guess_history)
            print(Fore.GREEN + '''
Congratulations! You cracked the secret code.''' + Style.RESET_ALL)
            print('''
Press enter to return menu page''')
            input()
            return
        
        if cheat and black_pins == 5:
            display_guess_history(guess_history)
            print(Fore.GREEN + '''
Congratulations! You cracked the secret code.''' + Style.RESET_ALL)
            print('''
Press enter to return menu page''')
            input()
            return
        

        attempts += 1

    if check_time_limit(start_time, DIFFICULTY_LEVELS[difficulty]['TIME_LIMIT']):
        print(f'''
{Fore.RED}Sorry, you ran out of time.{Style.RESET_ALL} The secret code was {''.join(secret_code)}''')
        print('''
Press enter to return menu page''')
        input()
        return
    else:
        print(f'''
{Fore.RED}Sorry, you ran out of attempts.{Style.RESET_ALL} The secret code was {''.join(secret_code)}''')
        print('''
Press enter to return menu page''')
        input()
        return

def record_game(username, difficulty, attempts, time_taken, score):
    connect = sqlite3.connect("mastermind.db")
    cur = connect.cursor()
    cur.execute("INSERT INTO records VALUES(?,?,?,?,?)", (username, difficulty, attempts, time_taken, score))
    connect.commit()
    connect.close()

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

After each guess, you will receive immediate feedback using black and white hint beads:
- A black bead indicates that a color in the player's guess is correct and in the correct position.
- A white bead indicates that a color in the player's guess is correct but in the wrong position.
    
Press Enter to return menu page
    ''')
    input()

def main():
    while True:
        clear_screen()
        print_rainbow_text("Welcome to the Mastermind game!")
        print(Fore.RED + '''            
- Play Game (1)''' + Style.RESET_ALL)
        print(ORANGE + '''- Game Rules (2)''' + Style.RESET_ALL)
        print(Fore.YELLOW + '''- Manage Your Account (3)''' + Style.RESET_ALL)
        print(Fore.GREEN + '''- History (4)''' + Style.RESET_ALL)
        print(Fore.CYAN + '''- Scoreboard (5)''' + Style.RESET_ALL)
        print(Fore.MAGENTA + '''- Exit Game (6)
''' + Style.RESET_ALL)

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
                print(Fore.RED + '''
You must log in to see history. Press enter to return menu page''' + Style.RESET_ALL)
                input()
            elif current_user == "admin":
                print(Fore.RED + '''
Please log in as "guest" to see history. Press enter to return menu page''' + Style.RESET_ALL)
                input()
            else:
                history()
        elif user_input == '5':
            scoreboard()
        elif user_input == '6':
            print_rainbow_text("Goodbye!")
            break
        else:
            print(Fore.RED + '''Invalid input.''' + Style.RESET_ALL)
            print('''
Press enter to try again''')
            input()

if __name__ == "__main__":
    main()