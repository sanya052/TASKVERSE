import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# ----------------- DATABASE SETUP ----------------- #
conn = sqlite3.connect("taskverse.db")
cursor = conn.cursor()

# Ensure correct users table structure (name only)
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute('''
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

# Create tasks table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    category TEXT,
    deadline TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')
conn.commit()

# ----------------- MAIN APP CLASS ----------------- #
class TaskVerseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskVerse – AI-Powered Task Manager")
        self.root.geometry("500x550")
        self.user_id = None
        self.build_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_login_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Welcome to TaskVerse", font=("Helvetica", 18, "bold")).pack(pady=20)
        tk.Label(self.root, text="Enter your name to continue:").pack()
        name_entry = tk.Entry(self.root)
        name_entry.pack(pady=10)

        def start_session():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty.")
                return

            cursor.execute("SELECT user_id FROM users WHERE name = ?", (name,))
            result = cursor.fetchone()
            if result:
                self.user_id = result[0]
            else:
                cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
                conn.commit()
                self.user_id = cursor.lastrowid
            self.dashboard()

        tk.Button(self.root, text="Continue", command=start_session).pack(pady=10)

    def dashboard(self):
        self.clear_window()
        tk.Label(self.root, text="TaskVerse Dashboard", font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Button(self.root, text="Add Task", width=20, command=self.add_task).pack(pady=5)
        tk.Button(self.root, text="View Tasks", width=20, command=self.view_tasks).pack(pady=5)
        tk.Button(self.root, text="AI Suggestion", width=20, command=self.ai_suggestion).pack(pady=5)
        tk.Button(self.root, text="Logout", width=20, command=self.build_login_screen).pack(pady=10)

    def add_task(self):
        self.clear_window()
        tk.Label(self.root, text="Add New Task", font=("Helvetica", 14)).pack(pady=10)

        title = tk.Entry(self.root)
        category = ttk.Combobox(self.root, values=["Academic", "Internship", "Self-Care", "Other"])
        deadline = tk.Entry(self.root)

        for label, widget in [("Task Title", title), ("Category", category), ("Deadline (YYYY-MM-DD)", deadline)]:
            tk.Label(self.root, text=label).pack()
            widget.pack(pady=2)

        def save_task():
            cursor.execute("INSERT INTO tasks (user_id, title, category, deadline) VALUES (?, ?, ?, ?)",
                           (self.user_id, title.get(), category.get(), deadline.get()))
            conn.commit()
            messagebox.showinfo("Success", "Task added!")
            self.dashboard()

        tk.Button(self.root, text="Save Task", command=save_task).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.dashboard).pack()

    def view_tasks(self):
        self.clear_window()
        tk.Label(self.root, text="Your Tasks", font=("Helvetica", 14)).pack(pady=10)

        tasks = cursor.execute("SELECT title, category, deadline, status FROM tasks WHERE user_id = ?", (self.user_id,)).fetchall()
        if not tasks:
            tk.Label(self.root, text="No tasks found.").pack(pady=10)
        else:
            for t in tasks:
                task_str = f"{t[0]} | {t[1]} | Due: {t[2]} | Status: {t[3]}"
                tk.Label(self.root, text=task_str, wraplength=450, justify="left").pack(pady=3)

        tk.Button(self.root, text="Back", command=self.dashboard).pack(pady=10)

    def ai_suggestion(self):
        hours = simpledialog.askfloat("AI Assistant", "How many hours do you have today?")
        if hours is None:
            return

        suggestion = ""
        if hours < 2:
            suggestion = "Revise one topic, do light reading, and take breaks."
        elif 2 <= hours <= 4:
            suggestion = "Do focused study, watch a lecture, and revise notes."
        else:
            suggestion = "Work on a project, study deeply, and add a self-care activity."

        messagebox.showinfo("AI Suggestion", suggestion)

# ----------------- RUN APP ----------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskVerseApp(root)
    root.mainloop()
