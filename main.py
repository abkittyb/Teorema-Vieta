"""Тренажёр теоремы Виета. Адаптивный интерфейс для Android."""
import json
import random
import time
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform

INK = (0.10, 0.20, 0.40, 1)
MUTED = (0.25, 0.35, 0.50, 1)
BLUE = (0.16, 0.48, 0.88, 1)
Window.clearcolor = (0.85, 0.92, 1, 1)
Window.softinput_mode = 'resize'


def text_label(text='', size=20, bold=False, minimum=32, tag=None):
    label = Label(text=text, font_size=sp(size), bold=bold, color=INK,
                  halign='center', valign='middle', size_hint_y=None)
    label.test_id = tag
    def fit(*_):
        label.text_size = (max(1, label.width), None)
        label.height = max(dp(minimum), label.texture_size[1] + dp(8))
    label.bind(width=fit, texture_size=fit)
    fit()
    return label


def action(text, callback, tag, secondary=False):
    button = Button(text=text, font_size=sp(20), bold=True,
                    size_hint_y=None, height=dp(56), background_normal='',
                    background_down='', background_color=(0.74, 0.84, 0.96, 1) if secondary else BLUE,
                    color=INK if secondary else (1, 1, 1, 1))
    button.test_id = tag
    button.bind(on_release=callback)
    return button


class SafeScreen(Screen):
    """System-bar insets surround a centred, scrollable content column."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shell = BoxLayout(orientation='vertical', spacing=dp(16))
        self.add_widget(self.shell)
        self.scroll = ScrollView(do_scroll_x=False, bar_width=dp(3),
                                 scroll_type=['bars', 'content'])
        self.shell.add_widget(self.scroll)
        self.viewport = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None)
        self.scroll.add_widget(self.viewport)
        self.body = BoxLayout(orientation='vertical', size_hint=(None, None), spacing=dp(16))
        self.viewport.add_widget(self.body)
        self.body.bind(minimum_height=self._layout)
        self.scroll.bind(size=self._layout)
        self.viewport.bind(width=self._layout)
        self._apply_insets(0, dp(28), 0, dp(28))
        self.bind(on_enter=self._entered)

    def _layout(self, *_):
        self.body.width = min(self.scroll.width, dp(480))
        self.body.height = self.body.minimum_height
        self.viewport.height = max(self.scroll.height, self.body.height)

    def _apply_insets(self, left, top, right, bottom):
        self.shell.padding = [left + dp(20), top + dp(16), right + dp(20), bottom + dp(16)]
        self._layout()

    def add_footer(self, widget):
        holder = AnchorLayout(size_hint_y=None, height=widget.height)
        holder.add_widget(widget)
        widget.size_hint_x = None
        holder.bind(width=lambda *_: setattr(widget, 'width', min(holder.width, dp(480))))
        self.shell.add_widget(holder)

    def _entered(self, *_):
        self.scroll.scroll_y = 1
        app = App.get_running_app()
        if app:
            app.refresh_insets()
            app.schedule_audit()


class StartScreen(SafeScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.body.add_widget(text_label('Теорема Виета', 28, True, 56, 'title'))
        self.body.add_widget(text_label('ax² + bx + c = 0', 24, minimum=48))
        self.body.add_widget(text_label('Устно подберите два корня\nи проверьте свой ответ.', 17, minimum=64))
        self.body.add_widget(action('Начать', self.go_to_train, 'start'))

    def go_to_train(self, *_):
        train = self.manager.get_screen('train')
        train.start_game()
        self.manager.current = 'train'


class TrainScreen(SafeScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score_total = self.total_attempts = self.score_errors = 0
        self.x1_correct = self.x2_correct = 0
        self.start_time = 0
        self.timer_running = False
        self.next_task_event = None
        self.lbl_time = text_label('Время: 00:00', 17, minimum=32, tag='timer')
        self.lbl_time.color = MUTED
        self.body.add_widget(self.lbl_time)
        self.body.add_widget(text_label('Устно подберите корни', 21, True, 40))
        self.lbl_eq = text_label('', 28, True, 72, 'equation')
        self.body.add_widget(self.lbl_eq)
        self.entry_x1 = self._root_row('x1 =', 'x1')
        self.entry_x2 = self._root_row('x2 =', 'x2')
        self.btn_check = action('Проверить', self.check_answer, 'check')
        self.body.add_widget(self.btn_check)
        self.lbl_result = text_label('', 18, True, 64, 'feedback')
        self.body.add_widget(self.lbl_result)
        self.btn_end = action('Завершить', self.end_game, 'end', secondary=True)
        self.add_footer(self.btn_end)
        self.disable_inputs()
        Clock.schedule_interval(self.update_timer, 1)

    def _root_row(self, caption, tag):
        row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(12))
        row.add_widget(Label(text=caption, font_size=sp(24), color=INK,
                             size_hint_x=None, width=dp(62)))
        entry = TextInput(multiline=False, input_type='number', input_filter='int',
                          font_size=sp(24), halign='center', padding=[dp(12), dp(12)],
                          background_normal='', background_active='',
                          background_color=(1, 1, 1, 1), foreground_color=INK,
                          write_tab=False)
        entry.test_id = tag
        entry.bind(focus=self._focus)
        row.add_widget(entry)
        minus = action('−', lambda *_: self.toggle_minus(entry), tag + '_minus', secondary=True)
        minus.size_hint_x = None
        minus.width = dp(56)
        row.add_widget(minus)
        self.body.add_widget(row)
        return entry

    def _focus(self, entry, focused):
        if focused:
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(entry, padding=dp(16)), 0.3)

    def toggle_minus(self, entry):
        if not entry.disabled:
            entry.text = entry.text[1:] if entry.text.startswith('-') else '-' + entry.text

    def _cancel_next(self):
        if self.next_task_event:
            self.next_task_event.cancel()
            self.next_task_event = None

    def start_game(self):
        self._cancel_next()
        self.start_time = time.monotonic()
        self.timer_running = True
        self.score_total = self.total_attempts = self.score_errors = 0
        self.lbl_time.text = 'Время: 00:00'
        self.generate_task()

    def generate_task(self, *_):
        self.next_task_event = None
        if not self.timer_running:
            return
        self.lbl_result.text = ''
        for entry in (self.entry_x1, self.entry_x2):
            entry.disabled = False
            entry.text = ''
        self.btn_check.disabled = False
        self.x1_correct = random.choice([n for n in range(-10, 11) if n])
        self.x2_correct = random.choice([n for n in range(-10, 11) if n])
        if random.random() < 0.2:
            self.x2_correct = self.x1_correct
        b = -(self.x1_correct + self.x2_correct)
        c = self.x1_correct * self.x2_correct
        equation = 'x²'
        if b:
            equation += f" {'+' if b > 0 else '−'} {abs(b)}x"
        if c:
            equation += f" {'+' if c > 0 else '−'} {abs(c)}"
        self.lbl_eq.text = equation + ' = 0'
        app = App.get_running_app()
        if app:
            app.schedule_audit()

    def check_answer(self, *_):
        try:
            answers = [int(self.entry_x1.text), int(self.entry_x2.text)]
        except ValueError:
            self.lbl_result.text = 'Введите два целых числа'
            self.lbl_result.color = (0.75, 0.12, 0.12, 1)
            return
        self.disable_inputs()
        self.total_attempts += 1
        correct = sorted(answers) == sorted([self.x1_correct, self.x2_correct])
        if correct:
            self.score_total += 1
            self.lbl_result.text = 'Правильно!'
            self.lbl_result.color = (0.05, 0.45, 0.15, 1)
        else:
            self.score_errors += 1
            self.lbl_result.text = f'Неверно. Корни: {self.x1_correct} и {self.x2_correct}'
            self.lbl_result.color = (0.75, 0.12, 0.12, 1)
        self.next_task_event = Clock.schedule_once(self.generate_task, 1.5 if correct else 3)
        App.get_running_app().schedule_audit()

    def disable_inputs(self):
        for entry in (self.entry_x1, self.entry_x2):
            entry.focus = False
            entry.disabled = True
        self.btn_check.disabled = True

    def update_timer(self, _):
        if self.timer_running:
            elapsed = int(time.monotonic() - self.start_time)
            self.lbl_time.text = f'Время: {elapsed // 60:02d}:{elapsed % 60:02d}'

    def end_game(self, *_):
        self.timer_running = False
        self._cancel_next()
        self.disable_inputs()
        elapsed = int(time.monotonic() - self.start_time) if self.start_time else 0
        self.manager.get_screen('results').show_results(
            elapsed, self.total_attempts, self.score_total, self.score_errors)
        self.manager.current = 'results'


class ResultsScreen(SafeScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.body.add_widget(text_label('Итоги тренировки', 27, True, 56, 'results_title'))
        self.lbl_time = text_label('', 20, minimum=40)
        self.lbl_correct = text_label('', 20, minimum=40, tag='correct_count')
        self.lbl_errors = text_label('', 20, minimum=40, tag='error_count')
        for label in (self.lbl_time, self.lbl_correct, self.lbl_errors):
            self.body.add_widget(label)
        self.body.add_widget(text_label('Оценка', 20, minimum=40))
        self.lbl_grade = text_label('', 64, True, 96, 'grade')
        self.body.add_widget(self.lbl_grade)
        self.add_footer(action('Новая тренировка', self.resume, 'restart'))

    def show_results(self, time_sec, total_attempts, correct, errors):
        self.lbl_time.text = f'Время: {time_sec // 60:02d}:{time_sec % 60:02d}'
        self.lbl_correct.text = f'Верные ответы: {correct}'
        self.lbl_errors.text = f'Ошибки: {errors}'
        percent = correct / total_attempts * 100 if total_attempts else 0
        grade = 5 if percent >= 90 else 4 if percent >= 70 else 3 if percent >= 50 else 2
        self.lbl_grade.text = str(grade)
        self.lbl_grade.color = (0.05, 0.45, 0.15, 1) if grade >= 4 else (0.75, 0.30, 0.08, 1)

    def resume(self, *_):
        self.manager.current = 'start'


class VietaApp(App):
    def build(self):
        self.ui_test = False
        if platform == 'android':
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            self.ui_test = activity.getIntent().getBooleanExtra('ui_test', False)
        self.sm = ScreenManager(transition=NoTransition())
        for cls, name in ((StartScreen, 'start'), (TrainScreen, 'train'), (ResultsScreen, 'results')):
            self.sm.add_widget(cls(name=name))
        Window.bind(size=lambda *_: self.refresh_insets())
        return self.sm

    def on_start(self):
        Clock.schedule_once(lambda dt: self.refresh_insets(), 0.2)
        Clock.schedule_once(lambda dt: self.refresh_insets(), 0.8)

    def on_resume(self):
        self.refresh_insets()

    def refresh_insets(self):
        if platform != 'android':
            return
        from android.runnable import run_on_ui_thread
        from jnius import autoclass
        @run_on_ui_thread
        def read():
            try:
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                insets = activity.getWindow().getDecorView().getRootWindowInsets()
                types = autoclass('android.view.WindowInsets$Type')
                bars = insets.getInsets(types.systemBars() | types.displayCutout())
                values = (bars.left, bars.top, bars.right, bars.bottom)
            except Exception:
                # Conservative fallback for Android 7–10 and not-yet-attached views.
                values = (0, dp(32), 0, dp(32))
            Clock.schedule_once(lambda dt: self.apply_insets(values), 0)
        read()

    def apply_insets(self, values):
        for screen in self.sm.screens:
            screen._apply_insets(*values)
        self.schedule_audit()

    def schedule_audit(self):
        if getattr(self, 'ui_test', False):
            Clock.schedule_once(self.audit_layout, 0.5)

    def audit_layout(self, *_):
        """Geometry is exported only when the CI launches with ui_test=true."""
        screen = self.sm.current_screen
        widgets = {}
        for widget in screen.walk():
            tag = getattr(widget, 'test_id', None)
            if tag:
                x, y = widget.to_window(widget.x, widget.y)
                widgets[tag] = dict(x=x, y=Window.height-y-widget.height,
                                    width=widget.width, height=widget.height,
                                    text=getattr(widget, 'text', ''), disabled=widget.disabled)
        Path(self.user_data_dir, 'ui-test.json').write_text(json.dumps(dict(
            screen=screen.name, width=Window.width, height=Window.height,
            density=dp(1), padding=list(screen.shell.padding), widgets=widgets)))


if __name__ == '__main__':
    VietaApp().run()
