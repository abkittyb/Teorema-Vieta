from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
import random
import time

Window.clearcolor = (0.85, 0.92, 1, 1)

class StartScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=30)

        layout.add_widget(Label())

        layout.add_widget(Label(text="Теорема Виета", font_size=55, bold=True, color=(0.1, 0.2, 0.4, 1), halign="center"))
        layout.add_widget(Label(text="ax² + bx + c = 0", font_size=36, color=(0.2, 0.3, 0.5, 1), halign="center"))

        layout.add_widget(Label(size_hint_y=None, height=50))

        btn_start = Button(text="Начать", font_size=45, bold=True,
                           size_hint=(None, None), size=(250, 90),
                           pos_hint={'center_x': 0.5},
                           background_normal='', background_color=(0.2, 0.6, 1, 1), color=(1,1,1,1))
        btn_start.bind(on_press=self.go_to_train)
        layout.add_widget(btn_start)

        layout.add_widget(Label())
        self.add_widget(layout)

    def go_to_train(self, *args):
        self.manager.current = "train"
        self.manager.get_screen("train").start_game()


class TrainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.score_total = 0
        self.total_attempts = 0
        self.score_errors = 0
        self.x1_correct = 0
        self.x2_correct = 0
        self.start_time = 0
        self.timer_running = False

        layout = BoxLayout(orientation="vertical", padding=[20, 30, 20, 30], spacing=15)

        self.lbl_time = Label(text="Суммарное время: 00 мин 00 сек", font_size=24, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_y=None, height=50)
        layout.add_widget(self.lbl_time)

        layout.add_widget(Label(text="Устно подберите корни:", font_size=32, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_y=None, height=60))

        self.lbl_eq = Label(text="x² + bx + c = 0", font_size=55, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_y=None, height=100)
        layout.add_widget(self.lbl_eq)

        layout.add_widget(Label(size_hint_y=None, height=10))

        row1 = BoxLayout(size_hint_y=None, height=70, spacing=10)
        row1.add_widget(Label())
        row1.add_widget(Label(text="x1 =", font_size=40, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_x=None, width=90))
        self.entry_x1 = TextInput(input_type="number", multiline=False, font_size=40, halign="center", background_color=(1,1,1,1), size_hint_x=None, width=100)
        row1.add_widget(self.entry_x1)

        btn_minus1 = Button(text="−", font_size=40, size_hint_x=None, width=60, background_normal='', background_color=(0.8, 0.9, 1, 1), color=(0,0,0,1), bold=True)
        btn_minus1.bind(on_press=lambda *_: self.toggle_minus(self.entry_x1))
        row1.add_widget(btn_minus1)
        row1.add_widget(Label())
        layout.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=70, spacing=10)
        row2.add_widget(Label())
        row2.add_widget(Label(text="x2 =", font_size=40, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_x=None, width=90))
        self.entry_x2 = TextInput(input_type="number", multiline=False, font_size=40, halign="center", background_color=(1,1,1,1), size_hint_x=None, width=100)
        row2.add_widget(self.entry_x2)

        btn_minus2 = Button(text="−", font_size=40, size_hint_x=None, width=60, background_normal='', background_color=(0.8, 0.9, 1, 1), color=(0,0,0,1), bold=True)
        btn_minus2.bind(on_press=lambda *_: self.toggle_minus(self.entry_x2))
        row2.add_widget(btn_minus2)
        row2.add_widget(Label())
        layout.add_widget(row2)

        layout.add_widget(Label(size_hint_y=None, height=10))

        check_container = BoxLayout(size_hint_y=None, height=80)
        check_container.add_widget(Label())

        self.btn_check = Button(text="Проверить", font_size=40, bold=True,
                                size_hint_x=None, width=250,
                                background_normal='', background_color=(0.2, 0.6, 1, 1), color=(1,1,1,1))
        self.btn_check.bind(on_press=self.check_answer)

        check_container.add_widget(self.btn_check)
        check_container.add_widget(Label())
        layout.add_widget(check_container)

        self.result_container = BoxLayout(size_hint_y=None, height=130)
        self.result_container.background_normal = ''
        self.result_container.background_color = (0,0,0,0)

        self.lbl_result = Label(text="", font_size=34, bold=True, halign="center", valign="middle")
        self.lbl_result.bind(size=self.lbl_result.setter('text_size'))

        self.result_container.add_widget(self.lbl_result)
        layout.add_widget(self.result_container)

        layout.add_widget(Label())

        end_container = BoxLayout(size_hint_y=None, height=70)
        end_container.add_widget(Label())

        self.btn_end = Button(text="Завершить", font_size=32, bold=True,
                              size_hint_x=None, width=200,
                              background_normal='', background_color=(1, 0.5, 0.5, 1), color=(0,0,0,1))
        self.btn_end.bind(on_press=self.end_game)

        end_container.add_widget(self.btn_end)
        end_container.add_widget(Label())
        layout.add_widget(end_container)

        self.add_widget(layout)
        self.disable_inputs()
        Clock.schedule_interval(self.update_timer, 1)

    def toggle_minus(self, entry):
        if entry.disabled: return
        if entry.text.startswith("-"): entry.text = entry.text[1:]
        else: entry.text = "-" + entry.text

    def start_game(self):
        self.start_time = time.time()
        self.timer_running = True
        self.score_total = 0
        self.score_errors = 0
        self.total_attempts = 0
        self.generate_task()

    def generate_task(self):
        self.lbl_result.text = ""
        self.result_container.background_color = (0,0,0,0)

        self.entry_x1.disabled = False
        self.entry_x2.disabled = False
        self.entry_x1.text = ""
        self.entry_x2.text = ""
        self.btn_check.disabled = False

        while True:
            self.x1_correct = random.randint(-10, 10)
            self.x2_correct = random.randint(-10, 10)
            if self.x1_correct != 0 and self.x2_correct != 0:
                break

        if random.random() < 0.2:
            self.x2_correct = self.x1_correct

        b = -(self.x1_correct + self.x2_correct)
        c = self.x1_correct * self.x2_correct

        eq_str = "x²"

        if b > 0:
            eq_str += f" + {b}x"
        elif b < 0:
            eq_str += f" - {abs(b)}x"

        if c > 0:
            eq_str += f" + {c}"
        elif c < 0:
            eq_str += f" - {abs(c)}"

        eq_str += " = 0"
        self.lbl_eq.text = eq_str

    def check_answer(self, *_):
        try:
            u_x1 = int(self.entry_x1.text)
            u_x2 = int(self.entry_x2.text)
        except ValueError:
            self.lbl_result.text = "Введите числа!"
            self.lbl_result.color = (1,0,0,1)
            return

        self.disable_inputs()
        self.total_attempts += 1

        correct = ((u_x1 == self.x1_correct and u_x2 == self.x2_correct) or
                   (u_x1 == self.x2_correct and u_x2 == self.x1_correct))

        if correct:
            self.lbl_result.text = "Правильно"
            self.lbl_result.color = (0, 0.7, 0, 1)
            self.score_total += 1
            Clock.schedule_once(lambda dt: self.generate_task(), 1.5)
        else:
            self.lbl_result.text = f"Неправильно\nВерные: {self.x1_correct} и {self.x2_correct}"
            self.lbl_result.color = (0.9, 0, 0, 1)
            self.score_errors += 1
            Clock.schedule_once(lambda dt: self.generate_task(), 3.0)

    def disable_inputs(self):
        self.entry_x1.disabled = True
        self.entry_x2.disabled = True
        self.btn_check.disabled = True

    def update_timer(self, dt):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            m = elapsed // 60
            s = elapsed % 60
            self.lbl_time.text = f"Суммарное время: {m:02d} мин {s:02d} сек"

    def end_game(self, *_):
        self.timer_running = False
        self.disable_inputs()
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        results = self.manager.get_screen("results")
        results.show_results(elapsed, self.total_attempts, self.score_total, self.score_errors)
        self.manager.current = "results"


class ResultsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation="vertical", padding=[30, 50, 30, 50], spacing=20)

        layout.add_widget(Label(text="Итоги:", font_size=55, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_y=None, height=80))

        self.lbl_time = Label(text="Время:", font_size=34, bold=True, color=(0.1, 0.2, 0.4, 1), halign="left")
        self.lbl_correct = Label(text="Верные ответы:", font_size=34, bold=True, color=(0.1, 0.2, 0.4, 1), halign="left")
        self.lbl_errors = Label(text="Неверные ответы:", font_size=34, bold=True, color=(0.1, 0.2, 0.4, 1), halign="left")

        layout.add_widget(self.lbl_time)
        layout.add_widget(self.lbl_correct)
        layout.add_widget(self.lbl_errors)

        layout.add_widget(Label(text="Оценка:", font_size=40, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_y=None, height=70))

        self.lbl_grade = Label(text="", font_size=120, bold=True, color=(0,0,0,1))
        layout.add_widget(self.lbl_grade)

        layout.add_widget(Label())

        btn_container = BoxLayout(size_hint_y=None, height=80)
        btn_container.add_widget(Label())

        btn_resume = Button(text="Продолжить", font_size=40, bold=True,
                            size_hint_x=None, width=250,
                            background_normal='', background_color=(0.2, 0.6, 1, 1), color=(1,1,1,1))
        btn_resume.bind(on_press=self.resume)

        btn_container.add_widget(btn_resume)
        btn_container.add_widget(Label())
        layout.add_widget(btn_container)

        self.add_widget(layout)

    def show_results(self, time_sec, total_attempts, correct, errors):
        m = time_sec // 60
        s = time_sec % 60
        self.lbl_time.text = f"Время: {m:02d} мин {s:02d} сек"
        self.lbl_correct.text = f"Верные ответы: {correct}"
        self.lbl_errors.text = f"Неверные ответы: {errors}"

        if total_attempts == 0:
            grade = 2
        else:
            percent = (correct / total_attempts) * 100
            if percent >= 90: grade = 5
            elif percent >= 70: grade = 4
            elif percent >= 50: grade = 3
            else: grade = 2

        self.lbl_grade.text = str(grade)

        if grade == 5:
            self.lbl_grade.color = (0, 0.8, 0, 1)
        elif grade == 4:
            self.lbl_grade.color = (0.9, 0.7, 0, 1)
        elif grade == 3:
            self.lbl_grade.color = (1, 0.5, 0, 1)
        else:
            self.lbl_grade.color = (1, 0, 0, 1)

    def resume(self, *_):
        self.manager.current = "start"


class VietaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(TrainScreen(name="train"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm

if __name__ == "__main__":
    VietaApp().run()