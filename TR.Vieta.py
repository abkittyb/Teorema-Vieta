import tkinter as tk
import random
import time

class Vieta:
    def __init__(self, root):
        self.root = root
        self.root.title("Теорема Виета - Тренажер")
        self.root.geometry("900x700")
        self.root.configure(bg="#e6ccff")

        self.score_total = 0
        self.score_first_try = 0
        self.score_errors = 0
        self.total_attempts = 0
        
        self.x1_correct = 0
        self.x2_correct = 0
        
        self.current_try = 0
        
        self.start_time = 0
        self.paused_time = 0
        self.timer_running = False
        self.is_paused = False

        self.create_widgets()

    def create_widgets(self):
        self.lbl_time = tk.Label(self.root, text="Суммарное время: 00 мин 00 сек", font=("Arial", 14, "bold"), bg="#e6ccff", fg="#800080")
        self.lbl_time.pack(pady=15)

        self.frame_main = tk.Frame(self.root, bg="#e6ccff")
        self.frame_main.pack(expand=True, fill="both")

        self.frame_center = tk.Frame(self.frame_main, bg="#e6ccff")
        self.frame_center.pack(expand=True)

        self.lbl_title = tk.Label(self.frame_center, text="Подберите корни устно:", font=("Arial", 28, "bold"), bg="#e6ccff", fg="#800080")
        self.lbl_title.pack(pady=(0, 30))

        self.frame_eq = tk.Frame(self.frame_center, bg="#e6ccff")
        self.frame_eq.pack(pady=(0, 40))

        self.frame_inputs = tk.Frame(self.frame_center, bg="#e6ccff")
        self.frame_inputs.pack(pady=10)

        tk.Label(self.frame_inputs, text="x1 =", font=("Arial", 32, "bold"), bg="#e6ccff", fg="blue").grid(row=0, column=0)
        self.entry_x1 = tk.Entry(self.frame_inputs, font=("Arial", 28), width=5, bg="#ccffff", justify="center")
        self.entry_x1.grid(row=0, column=1, padx=20)
        self.entry_x1.bind('<KeyRelease>', self.check_inputs_filled)

        tk.Label(self.frame_inputs, text="x2 =", font=("Arial", 32, "bold"), bg="#e6ccff", fg="blue").grid(row=0, column=2, padx=(30, 0))
        self.entry_x2 = tk.Entry(self.frame_inputs, font=("Arial", 28), width=5, bg="#ccffff", justify="center")
        self.entry_x2.grid(row=0, column=3, padx=20)
        self.entry_x2.bind('<KeyRelease>', self.check_inputs_filled)

        self.lbl_result = tk.Label(self.frame_center, text="", font=("Arial", 24, "bold"), bg="#e6ccff", height=2)
        self.lbl_result.pack(pady=10)

        self.frame_buttons = tk.Frame(self.frame_center, bg="#e6ccff")
        self.frame_buttons.pack(pady=20)

        self.btn_start = tk.Button(self.frame_buttons, text="Старт", font=("Arial", 20, "bold"), width=22, command=self.start_game)
        self.btn_start.pack()

        self.btn_check = tk.Button(self.frame_buttons, text="Проверить", font=("Arial", 20, "bold"), width=22, command=self.check_answer)
        self.btn_next = tk.Button(self.frame_buttons, text="Дальше", font=("Arial", 20, "bold"), width=22, bg="#b3e6b3", command=self.next_task)

        self.bottom_bar = tk.Frame(self.root, bg="#e6ccff")
        self.bottom_bar.pack(fill="x", side="bottom")

        self.btn_end = tk.Button(self.bottom_bar, text="Завершить", font=("Arial", 16, "bold"), width=20, bg="#ff9999", command=self.end_game)
        self.btn_end.pack(side="bottom", pady=15)

        self.frame_stats = tk.Frame(self.bottom_bar, bg="#d9b3ff", bd=2, relief="groove")
        self.frame_stats.pack(fill="x", side="bottom", pady=(0, 10), padx=20)
        
        self.lbl_stats = tk.Label(self.frame_stats, text="Решено всего: 0 | С первой попытки: 0 | Ошибочных попыток: 0", font=("Arial", 14, "bold"), bg="#d9b3ff", fg="#333")
        self.lbl_stats.pack(pady=8)

        self.entry_x1.config(state="disabled")
        self.entry_x2.config(state="disabled")
        self.update_timer()

    def start_game(self):
        self.btn_start.pack_forget()
        self.start_time = time.time()
        self.paused_time = 0
        self.timer_running = True
        self.is_paused = False
        self.generate_task()

    def draw_equation(self, a, b, c):
        for widget in self.frame_eq.winfo_children():
            widget.destroy()

        inner_frame = tk.Frame(self.frame_eq, bg="#e6ccff")
        inner_frame.pack(expand=True)

        font_main = ("Arial", 40, "bold")
        font_pow = ("Arial", 22, "bold")

        color_x = "#800080"     
        color_coef = "#cc0000"  

        def add_part(text, font, color, is_power=False):
            lbl = tk.Label(inner_frame, text=text, font=font, bg="#e6ccff", fg=color)
            if is_power:
                lbl.pack(side="left", anchor="n", pady=(0, 20))
            else:
                lbl.pack(side="left")

        if a != 1:
            add_part(str(a) if a != -1 else "-", font_main, color_coef)
            
        add_part("x", font_main, color_x)
        add_part("2", font_pow, color_x, is_power=True)

        if b != 0:
            if b > 0:
                add_part(" + ", font_main, color_x)
            else:
                add_part(" - ", font_main, color_x)
            
            abs_b = abs(b)
            if abs_b != 1:
                add_part(str(abs_b), font_main, color_coef)
            add_part("x", font_main, color_x)

        if c != 0:
            if c > 0:
                add_part(" + ", font_main, color_x)
            else:
                add_part(" - ", font_main, color_x)
            
            add_part(str(abs(c)), font_main, color_coef)

        add_part(" = 0", font_main, color_x)

    def generate_task(self):
        self.lbl_result.config(text="")
        self.entry_x1.config(state="normal")
        self.entry_x2.config(state="normal")
        self.entry_x1.delete(0, tk.END)
        self.entry_x2.delete(0, tk.END)
        self.entry_x1.focus()

        self.current_try = 1
        self.btn_next.pack_forget()
        self.btn_check.pack_forget()

        eq_type = random.choice(["simple", "scaled", "no_c", "opposite_roots"])

        if eq_type == "simple":
            a = 1
            self.x1_correct = random.randint(-10, 10)
            self.x2_correct = random.randint(-10, 10)
            while self.x1_correct == self.x2_correct or self.x1_correct == 0 or self.x2_correct == 0:
                self.x1_correct = random.randint(-10, 10)
                self.x2_correct = random.randint(-10, 10)
                
        elif eq_type == "scaled":
            a = random.randint(2, 5)
            if random.random() < 0.3: a = -a
            self.x1_correct = random.randint(-10, 10)
            self.x2_correct = random.randint(-10, 10)
            while self.x1_correct == self.x2_correct or self.x1_correct == 0 or self.x2_correct == 0:
                self.x1_correct = random.randint(-10, 10)
                self.x2_correct = random.randint(-10, 10)
                
        elif eq_type == "no_c":
            a = random.randint(1, 4)
            self.x1_correct = 0
            self.x2_correct = random.randint(-10, 10)
            while self.x2_correct == 0:
                self.x2_correct = random.randint(-10, 10)
                
        else:
            a = random.randint(1, 3)
            self.x1_correct = random.randint(1, 10)
            self.x2_correct = -self.x1_correct

        b = -a * (self.x1_correct + self.x2_correct)
        c = a * (self.x1_correct * self.x2_correct)

        self.draw_equation(a, b, c)

    def check_inputs_filled(self, event):
        if self.entry_x1.get() and self.entry_x2.get() and not self.btn_check.winfo_ismapped():
            self.btn_check.pack()

    def check_answer(self):
        try:
            u_x1 = int(self.entry_x1.get())
            u_x2 = int(self.entry_x2.get())
        except ValueError:
            self.lbl_result.config(text="Ошибка! Введите целые числа.", fg="red")
            return

        self.btn_check.pack_forget()
        self.entry_x1.config(state="disabled")
        self.entry_x2.config(state="disabled")
        
        self.total_attempts += 1

        if (u_x1 == self.x1_correct and u_x2 == self.x2_correct) or (u_x1 == self.x2_correct and u_x2 == self.x1_correct):
            self.lbl_result.config(text="ПРАВИЛЬНО", fg="green")
            self.score_total += 1
            if self.current_try == 1:
                self.score_first_try += 1
            self.btn_next.config(text="Дальше", command=self.next_task)
        else:
            self.lbl_result.config(text=f"НЕПРАВИЛЬНО. Верные корни: {self.x1_correct} и {self.x2_correct}", fg="red")
            self.score_errors += 1
            self.current_try += 1
            self.btn_next.config(text="Следующее уравнение", command=self.next_task)
            
            if not self.is_paused:
                self.paused_time += time.time() - self.start_time
                self.is_paused = True

        self.update_stats()
        self.btn_next.pack(pady=10)

    def next_task(self):
        if self.is_paused:
            self.start_time = time.time()
            self.is_paused = False
            
        self.generate_task()

    def update_stats(self):
        self.lbl_stats.config(text=f"Решено всего: {self.score_total} | С первой попытки: {self.score_first_try} | Ошибочных попыток: {self.score_errors}")

    def update_timer(self):
        if self.timer_running:
            if not self.is_paused:
                elapsed = self.paused_time + (time.time() - self.start_time)
            else:
                elapsed = self.paused_time
                
            elapsed = int(elapsed)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.lbl_time.config(text=f"Суммарное время: {minutes:02d} мин {seconds:02d} сек")
        self.root.after(1000, self.update_timer)

    def end_game(self):
        if not self.timer_running and self.score_total == 0:
            self.root.quit()
            return

        self.timer_running = False
        
        if not self.is_paused:
            elapsed = self.paused_time + (time.time() - self.start_time)
        else:
            elapsed = self.paused_time
            
        elapsed = int(elapsed)
        minutes = elapsed // 60
        seconds = elapsed % 60
        time_str = f"{minutes:02d} мин {seconds:02d} сек"

        if self.score_total == 0:
            grade = 2
        else:
            percent_first_try = (self.score_first_try / self.score_total) * 100
            
            if percent_first_try >= 90:
                base_grade = 5
            elif percent_first_try >= 70:
                base_grade = 4
            elif percent_first_try >= 50:
                base_grade = 3
            else:
                base_grade = 2

            avg_time_per_task = elapsed / self.score_total
            if base_grade >= 4 and avg_time_per_task > 20:
                grade = base_grade - 1
            else:
                grade = base_grade
                
            if self.score_total < 3 and grade == 5:
                grade = 4

        self.lbl_time.pack_forget()
        self.lbl_title.pack_forget()
        self.frame_eq.pack_forget()
        self.frame_inputs.pack_forget()
        self.lbl_result.pack_forget()
        self.frame_buttons.pack_forget()
        self.bottom_bar.pack_forget()

        self.root.configure(bg="#f0e6ff") 
        self.frame_main.configure(bg="#f0e6ff")
        self.frame_center.configure(bg="#f0e6ff")

        final_text = (
            f"Время: {time_str}\n"
            f"Всего попыток: {self.total_attempts}\n"
            f"Из них ошибочных: {self.score_errors}\n\n"
            f"Ваша оценка:\n{grade}"
        )

        self.lbl_final = tk.Label(self.frame_center, 
                                  text=final_text, 
                                  font=("Arial", 28, "bold"), 
                                  bg="#f0e6ff", 
                                  fg="#800080",
                                  justify="center")
        self.lbl_final.pack(expand=True)

        self.frame_final_buttons = tk.Frame(self.frame_center, bg="#f0e6ff")
        self.frame_final_buttons.pack(pady=40)

        self.btn_resume = tk.Button(self.frame_final_buttons, text="Продолжить", font=("Arial", 18, "bold"), bg="#b3e6b3", command=self.resume_game)
        self.btn_resume.pack(side="left", padx=20)

        self.btn_exit = tk.Button(self.frame_final_buttons, text="Выйти", font=("Arial", 18, "bold"), bg="#ff9999", command=self.root.quit)
        self.btn_exit.pack(side="left", padx=20)

    def resume_game(self):
        self.lbl_final.pack_forget()
        self.frame_final_buttons.pack_forget()

        self.root.configure(bg="#e6ccff")
        self.frame_main.configure(bg="#e6ccff")
        self.frame_center.configure(bg="#e6ccff")
        self.bottom_bar.configure(bg="#e6ccff")

        self.lbl_time.pack(pady=15)
        self.lbl_title.pack(pady=(0, 30))
        self.frame_eq.pack(pady=(0, 40))
        self.frame_inputs.pack(pady=10)
        self.lbl_result.pack(pady=10)
        self.frame_buttons.pack(pady=20)
        self.bottom_bar.pack(fill="x", side="bottom")

        self.timer_running = True
        if self.is_paused:
            self.start_time = time.time()
            self.is_paused = False
            
        self.generate_task()

if __name__ == "__main__":
    root = tk.Tk()
    app = Vieta(root)
    root.mainloop()