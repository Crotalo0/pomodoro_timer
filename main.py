"""Pomodoro timer app."""
import tkinter as tk
import datetime as dt
from plyer import notification
import simpleaudio as sa
import pandas as pd


# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
CHECKMARK = "✓"
reps = 0
total_pomo = 0
timer = ''
row_check_boxes = 1
VERSION = 1.1
# 1.1: added log function
#   introduced pomo_log()
#   LOG saved to pomolog.csv


# TODO:
#   - Add settings tab to change pomodoro timers; DONE
#   - Add About page with info; DONE
#   - PC notification when starting work or break timer; DONE
#   - Custom guitar sound when timer ends; DONE
#   - Custom sound effects for different tasks;
#   - Work Report: total pomo log DONE
#   - to-do and tasks linked to log;
#   - Mail sync with daily log;
#   - Adding relaxing audio;
#   - Google calendar sync? I'm not even sure in what is does;
#   - Advanced to-do with subtasks, reminders, recurring tasks and notes.


# ---------------------------- LOG FILE ------------------------------------ #

def pomo_log(date: str) -> None:
    """Log total pomo in a day with some info to csv."""
    global total_pomo
    entries = pd.read_csv("pomolog.csv")
    test = entries.to_dict(orient="records")
    date_list = entries["date"].to_list()
    if date in date_list:
        test_date = entries[entries.date == date]
        total_pomo += int(test_date.pomodoro)

    data_dict = [{
        "date": date,
        "pomodoro": total_pomo,
    }]
    final_data = pd.DataFrame(data_dict)
    final_data.to_csv("pomolog.csv", index=False)


# ---------------------------- SETTINGS PAGE ------------------------------- #

def settings_page():
    """Tk settings page to tune timers."""
    global WORK_MIN
    global SHORT_BREAK_MIN
    global LONG_BREAK_MIN

    def option_confirm():
        global WORK_MIN
        global SHORT_BREAK_MIN
        global LONG_BREAK_MIN
        WORK_MIN = scale1.get()
        SHORT_BREAK_MIN = scale2.get()
        LONG_BREAK_MIN = scale3.get()
        top.destroy()

    top = tk.Toplevel(window, bg=YELLOW)
    top.title("pomodoro settings")
    top.iconphoto(False, pomodoro_icon)

    scale1_label = tk.Label(top, text="Work time\n(min)",
                            bg=YELLOW, fg=PINK,
                            font=(FONT_NAME, 14, "bold"))
    scale1_label.grid(column=0, row=0, padx=5, pady=5)

    scale1 = tk.Scale(top, from_=5, to=60, bg=YELLOW, highlightthickness=False)
    scale1.grid(column=0, row=1, padx=5, pady=5)

    scale2_label = tk.Label(top, text="Short break\n(min)",
                            bg=YELLOW, fg=PINK,
                            font=(FONT_NAME, 14, "bold"))
    scale2_label.grid(column=1, row=0, padx=5, pady=5)

    scale2 = tk.Scale(top, from_=1, to=30, bg=YELLOW, highlightthickness=False)
    scale2.grid(column=1, row=1, padx=5, pady=5)

    scale3_label = tk.Label(top, text="Long break\n(min)",
                            bg=YELLOW, fg=PINK,
                            font=(FONT_NAME, 14, "bold"))
    scale3_label.grid(column=2, row=0, padx=5, pady=5)

    scale3 = tk.Scale(top, from_=1, to=45, bg=YELLOW, highlightthickness=False)
    scale3.grid(column=2, row=1, padx=5, pady=5)

    confirm_button = tk.Button(top, text='Apply', command=option_confirm)
    confirm_button.grid(column=1, row=2, padx=5, pady=5)

    scale1.set(WORK_MIN)
    scale2.set(SHORT_BREAK_MIN)
    scale3.set(LONG_BREAK_MIN)


# ---------------------------- TO_DO LIST ADDER ------------------------------- #

def todo_list_entry():
    """Tk todo entry."""
    def add_check_box():
        """Add check box to list entry."""
        def remove_check_box():
            """Remove entry button from list."""
            chk_btn.grid_forget()
            remove_btn.grid_forget()

        global row_check_boxes
        var = tk.IntVar()
        chk_btn = tk.Checkbutton(todo_frame, text=f"{entry.get()}", variable=var,
                                 highlightthickness=False, fg=RED, bg=YELLOW,
                                 font=(FONT_NAME, 12, "bold"),
                                 activebackground=PINK, activeforeground=GREEN)
        chk_btn.grid(row=row_check_boxes, column=1, sticky='w')
        remove_btn = tk.Button(todo_frame, text='-',
                               highlightthickness=False, command=remove_check_box)
        remove_btn.grid(row=row_check_boxes, column=0)
        row_check_boxes += 1
        top.destroy()

    top = tk.Toplevel(window, bg=YELLOW)
    top.geometry("200x90")
    top.title("todo entry")
    top.iconphoto(False, pomodoro_icon)

    label = tk.Label(top, text="enter todo topic: ", bg=YELLOW, fg=PINK,
                     font=(FONT_NAME, 14, "bold"))
    label.pack(pady=3)
    entry = tk.Entry(top, width=30)
    entry.pack(padx=5, pady=5)
    entry.focus_set()
    btn = tk.Button(top, text='Ok', command=add_check_box)
    btn.pack()


# ---------------------------- TIMER RESET ------------------------------- #

def reset_timer():
    """Reset pomodoro timer."""
    global timer
    global reps
    window.after_cancel(timer)
    canvas.itemconfig(timer_text, text="00:00")
    timer_label.config(text='Timer', fg=GREEN)
    counter["text"] = ''
    reps = 0


# ---------------------------- TIMER MECHANISM ------------------------------- #

def start_timer():
    """Start timer."""
    global reps
    reps += 1

    work_secs = 60 * WORK_MIN
    short_break_secs = 60 * SHORT_BREAK_MIN
    long_break_secs = 60 * LONG_BREAK_MIN

    # wave_obj = sa.WaveObject.from_wave_file("alarm.wav")
    wave_obj = sa.WaveObject.from_wave_file("pomodoro_alarm.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()

    if reps % 2 != 0:
        timer_label.config(text='Work', fg=GREEN)

        notification.notify(title="Pomodoro timer",
                            message=f"Time for work: {WORK_MIN}min",
                            timeout=50)
        count_down(work_secs)
    else:
        if reps % 8 == 0:
            timer_label.config(text='Long Break', fg=RED)
            notification.notify(title="Pomodoro timer",
                                message=f"Time for long break: {LONG_BREAK_MIN}min",
                                timeout=50)
            count_down(long_break_secs)
        else:
            timer_label.config(text='Break', fg=PINK)
            notification.notify(title="Pomodoro timer",
                                message=f"Time for short break: {SHORT_BREAK_MIN}min",
                                timeout=50)
            count_down(short_break_secs)


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #

def count_down(count):
    """Timer logic."""
    global timer
    global total_pomo
    count_min = count // 60
    count_sec = count % 60
    if count_sec < 10:
        count_sec = '0' + str(count_sec)
    if count_min < 10:
        count_min = '0' + str(count_min)
    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        timer = window.after(1000, count_down, count - 1)
    else:
        start_timer()
        if reps % 2 == 0:
            counter["text"] += CHECKMARK
            total_pomo += 1
        if reps % 8 == 0:
            counter['text'] += '\n'


# ---------------------------- UI SETUP ------------------------------- #

window = tk.Tk()
window.title("Pomodoro timer")
window.config(padx=100, pady=50, bg=YELLOW)
pomodoro_icon = tk.PhotoImage(file="pomodoro.png")
window.iconphoto(False, pomodoro_icon)
canvas = tk.Canvas(window, width=200, height=224, bg=YELLOW,
                   highlightthickness=False)
pomodoro = tk.PhotoImage(file='tomato.png')
canvas.create_image(100, 112, image=pomodoro)
timer_text = canvas.create_text(100, 140, text="00:00", fill="white",
                                font=(FONT_NAME, 35, "bold"))
canvas.grid(column=1, row=1)
timer_label = tk.Label(text='Timer', bg=YELLOW, fg=GREEN,
                       font=(FONT_NAME, 50, "bold"))
timer_label.grid(column=1, row=0)
start_button = tk.Button(text="Start",
                         highlightthickness=False, command=start_timer)
start_button.grid(column=0, row=2)
reset_button = tk.Button(text="Reset",
                         highlightthickness=False, command=reset_timer)
reset_button.grid(column=2, row=2)
counter = tk.Label(bg=YELLOW, fg=GREEN, font=(FONT_NAME, 30, "normal"))
counter.grid(column=1, row=3)


# ---------------------------- TO-DO FRAME ------------------------------- #

todo_frame = tk.Frame(bg=YELLOW)
todo_frame.grid(row=1, column=3, sticky="n")

todo_label = tk.Label(todo_frame, text="todo-list:",
                      highlightthickness=False, bg=YELLOW, fg=RED,
                      font=(FONT_NAME, 20, "bold"))
todo_btn = tk.Button(todo_frame, text="+",
                     highlightthickness=False, command=todo_list_entry)
todo_btn.grid(row=0, column=0, sticky='w')
todo_label.grid(row=0, column=1, padx=5)


# ---------------------------- MENUBAR ------------------------------- #

def about_page():
    """Tk info page."""
    top = tk.Toplevel(window, bg=YELLOW)
    top.title("About page")
    top.geometry("300x300")
    top.iconphoto(False, pomodoro_icon)
    about_label = tk.Label(top, text=f"Simple pomodoro timer app.",
                           highlightthickness=False, bg=YELLOW, fg=GREEN,
                           font=(FONT_NAME, 14, "bold"))
    about_label.pack(pady=10, padx=10)
    creator_label = tk.Label(top, text=f"Creator: Alex",
                             highlightthickness=False, bg=YELLOW, fg=GREEN,
                             font=(FONT_NAME, 14, "bold"))
    creator_label.pack(pady=10, padx=10)
    version_label = tk.Label(top, text=f"Version: {VERSION}",
                             highlightthickness=False, bg=YELLOW, fg=GREEN,
                             font=(FONT_NAME, 14, "bold"))
    version_label.pack(pady=10, padx=10)


menubar = tk.Menu()
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Settings", command=settings_page)
file_menu.add_command(label="About", command=about_page)
file_menu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=file_menu)
window.config(menu=menubar)

window.mainloop()

now = dt.datetime.now()
date = f"{now.day}/{now.month}/{now.year}"


pomo_log(date)
