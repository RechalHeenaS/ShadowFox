import sqlite3
import random
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

DB_NAME = "words.db"

# ---- Database Setup ----
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create game_results table
    c.execute('''
        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            word TEXT,
            result TEXT,
            score INTEGER
        )
    ''')

    # Create words table
    c.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            level TEXT NOT NULL
        )
    ''')

    # Insert sample words if not already present
    c.execute("SELECT COUNT(*) FROM words")
    if c.fetchone()[0] == 0:
        words_data = [
            ("apple", "simple"), ("dog", "simple"), ("tree", "simple"), ("car", "simple"), ("book", "simple"),
            ("planet", "medium"), ("garden", "medium"), ("hunter", "medium"), ("laptop", "medium"), ("bridge", "medium"),
            ("galaxy", "hard"), ("python", "hard"), ("quantum", "hard"), ("neutron", "hard"), ("diamond", "hard")
        ]
        c.executemany("INSERT INTO words (word, level) VALUES (?, ?)", words_data)

    conn.commit()
    conn.close()

def get_words(level, count):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM words WHERE level = ? ORDER BY RANDOM() LIMIT ?", (level, count))
    result = [row[0] for row in cursor.fetchall()]
    conn.close()
    return result

def save_game(word, result, score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
    cursor.execute("INSERT INTO game_results (timestamp, word, result, score) VALUES (?, ?, ?, ?)",
                   (timestamp, word, result, score))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM game_results")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM game_results WHERE result='Won'")
    won = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM game_results WHERE result='Lost'")
    lost = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(score) FROM game_results")
    avg_score = cursor.fetchone()[0] or 0
    conn.close()
    return total, won, lost, round(avg_score, 2)

# ---- Hangman Game Class ----
class HangmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Hangman Game")
        self.root.geometry("500x600")
        self.root.config(bg="#ffc0cb")

        self.level_map = {'1': 'simple', '2': 'medium', '3': 'hard'}
        self.word_count_map = {'simple': 5, 'medium': 7, 'hard': 10}
        self.tries_map = {'simple': 8, 'medium': 6, 'hard': 4}

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="🧠 Choose Difficulty", font=("Helvetica", 16), bg="#ffc0cb", fg="#000000").pack(pady=10)
        self.level_var = tk.StringVar(value='1')

        levels = tk.Frame(self.root, bg="#ffc0cb")
        levels.pack()
        for name, val in [("Simple", '1'), ("Medium", '2'), ("Hard", '3')]:
            tk.Radiobutton(levels, text=name, variable=self.level_var, value=val,
                           bg="#ffc0cb", fg="black", selectcolor="#ff69b4", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

        tk.Button(self.root, text="▶ Start Game", command=self.start_game,
                  font=("Arial", 14), bg="#ff69b4", fg="white").pack(pady=10)

        self.word_display = tk.Label(self.root, text="", font=("Consolas", 30), bg="#ffc0cb", fg="black")
        self.word_display.pack(pady=20)

        self.info_display = tk.Label(self.root, text="", font=("Arial", 14), bg="#ffc0cb", fg="black")
        self.info_display.pack()

        self.input_frame = tk.Frame(self.root, bg="#ffc0cb")
        self.input_frame.pack(pady=10)

        self.input_entry = tk.Entry(self.input_frame, font=("Consolas", 18), width=3)
        self.input_entry.pack(side=tk.LEFT, padx=10)

        tk.Button(self.input_frame, text="✔ Guess", command=self.guess_letter,
                  font=("Arial", 12), bg="#ffb6c1", fg="black").pack(side=tk.LEFT)

        tk.Button(self.root, text="📈 Dashboard", command=self.show_dashboard,
                  font=("Arial", 13), bg="#db7093", fg="white").pack(pady=10)

    def start_game(self):
        level = self.level_map.get(self.level_var.get(), 'simple')
        word_list = get_words(level, self.word_count_map[level])
        if not word_list:
            messagebox.showerror("❌ Error", "No words found. Add to the DB.")
            return

        self.secret_word = random.choice(word_list).lower()
        self.display_word = ['_' for _ in self.secret_word]
        self.tries = self.tries_map[level]
        self.score = 0
        self.guessed = []

        self.update_display()

    def update_display(self):
        self.word_display.config(text=" ".join(self.display_word))
        self.info_display.config(text=f"Tries: {self.tries} | Score: {self.score}")

    def guess_letter(self):
        letter = self.input_entry.get().lower().strip()
        self.input_entry.delete(0, tk.END)

        if not letter.isalpha() or len(letter) != 1:
            messagebox.showwarning("⚠️", "Enter one valid letter.")
            return

        if letter in self.guessed:
            messagebox.showinfo("⚠️", "Already guessed!")
            return

        self.guessed.append(letter)

        if letter in self.secret_word:
            self.score += self.secret_word.count(letter)
            for i, ch in enumerate(self.secret_word):
                if ch == letter:
                    self.display_word[i] = letter
        else:
            self.tries -= 1
            self.score -= 2

        self.update_display()
        self.check_game_status()

    def check_game_status(self):
        if '_' not in self.display_word:
            self.score += 10
            messagebox.showinfo("🎉 You Win!", f"The word was '{self.secret_word}'\nScore: {self.score}")
            save_game(self.secret_word, "Won", self.score)
        elif self.tries <= 0:
            messagebox.showinfo("💀 Game Over", f"The word was '{self.secret_word}'\nScore: {self.score}")
            save_game(self.secret_word, "Lost", self.score)
        else:
            return
        self.word_display.config(text="")
        self.info_display.config(text="")

    def show_dashboard(self):
        total, won, lost, avg = get_stats()
        dash = tk.Toplevel(self.root)
        dash.title("📈 Game Dashboard")
        dash.config(bg="#ffc0cb")
        dash.geometry("320x240")

        tk.Label(dash, text="📊 Your Performance", font=("Arial", 16, 'bold'), fg="black", bg="#ffc0cb").pack(pady=10)
        for text in [
            f"Total Games: {total}",
            f"Games Won: {won}",
            f"Games Lost: {lost}",
            f"Average Score: {avg}"
        ]:
            tk.Label(dash, text=text, font=("Arial", 14), fg="black", bg="#ffc0cb").pack(pady=4)

        tk.Button(dash, text="Close", command=dash.destroy,
                  font=("Arial", 12), bg="#ff69b4", fg="white").pack(pady=10)

# ---- Main Execution ----
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    game = HangmanGUI(root)
    root.mainloop()
