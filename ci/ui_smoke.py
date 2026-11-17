"""Android CI: exercise the app through real taps and the on-screen keyboard."""
import json
import math
from pathlib import Path
import re
import subprocess
import time

PACKAGE = 'ru.abkittyb.vietatrainer'
OUT = Path('diagnostics')
OUT.mkdir(exist_ok=True)


def adb(*args, check=True):
    return subprocess.run(['adb', *args], check=check, capture_output=True).stdout


def state(screen=None):
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        try:
            value = json.loads(adb('exec-out', 'run-as', PACKAGE, 'cat', 'files/ui-test.json'))
            if screen is None or value['screen'] == screen:
                return value
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        time.sleep(0.2)
    raise AssertionError(f'No geometry for {screen}')


def capture(name, data):
    (OUT / (name + '.png')).write_bytes(adb('exec-out', 'screencap', '-p'))
    (OUT / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2))


def inside(data, tag, touch=False):
    w = data['widgets'][tag]
    left, top, right, bottom = data['padding']
    tolerance = 2
    assert w['x'] >= left - tolerance, (tag, w, data)
    assert w['x'] + w['width'] <= data['width'] - right + tolerance, (tag, w, data)
    assert w['y'] >= top - tolerance, (tag, w, data)
    assert w['y'] + w['height'] <= data['height'] - bottom + tolerance, (tag, w, data)
    if touch:
        assert min(w['width'], w['height']) >= 48 * data['density'] - tolerance, (tag, w)


def tap(tag, data=None):
    data = data or state()
    w = data['widgets'][tag]
    adb('shell', 'input', 'tap', str(round(w['x'] + w['width']/2)), str(round(w['y'] + w['height']/2)))


def launch(width, height, density, scale, prefix):
    adb('shell', 'am', 'force-stop', PACKAGE)
    adb('shell', 'wm', 'size', f'{width}x{height}')
    adb('shell', 'wm', 'density', str(density))
    adb('shell', 'settings', 'put', 'system', 'font_scale', str(scale))
    adb('shell', 'run-as', PACKAGE, 'rm', '-f', 'files/ui-test.json')
    adb('shell', 'am', 'start', '-W', '-n', PACKAGE + '/org.kivy.android.PythonActivity', '--ez', 'ui_test', 'true')
    data = state('start')
    time.sleep(1.5)
    data = state('start')
    inside(data, 'title')
    inside(data, 'start', True)
    capture(prefix + '-start', data)
    tap('start', data)
    time.sleep(1)
    data = state('train')
    inside(data, 'timer')
    inside(data, 'end', True)
    capture(prefix + '-train', data)
    return data


adb('logcat', '-c')
data = launch(1080, 2400, 420, 1.0, 'phone')
for tag in ('x1', 'x2', 'check'):
    inside(data, tag, True)
# Solve the displayed equation independently of the app's answer-checking code.
eq = data['widgets']['equation']['text'].replace('−', '-').replace(' ', '')
match = re.fullmatch(r'x²([+-]\d+x)?([+-]\d+)?=0', eq)
assert match, eq
b = int(match[1][:-1]) if match[1] else 0
c = int(match[2]) if match[2] else 0
root = math.isqrt(b*b - 4*c)
answers = [(-b + root)//2, (-b - root)//2]
for tag, answer in zip(('x1', 'x2'), answers):
    tap(tag)
    time.sleep(0.8)
    if tag == 'x1': capture('phone-keyboard', state('train'))
    adb('shell', 'input', 'text', str(answer))
    adb('shell', 'input', 'keyevent', '4')
    time.sleep(0.7)
tap('check')
time.sleep(0.8)
data = state('train')
assert data['widgets']['feedback']['text'] == 'Правильно!', data
capture('phone-correct-answer', data)
tap('end', data)
time.sleep(1)
data = state('results')
inside(data, 'restart', True)
assert data['widgets']['correct_count']['text'].endswith(': 1'), data
assert data['widgets']['grade']['text'] == '5', data
capture('phone-results', data)
tap('restart', data)
time.sleep(1)
assert state('start')['screen'] == 'start'
launch(720, 1280, 320, 1.0, 'compact')
launch(1080, 2400, 420, 1.3, 'large-text')
(OUT / 'logcat.txt').write_bytes(adb('logcat', '-d'))
assert b'Traceback (most recent call last)' not in (OUT / 'logcat.txt').read_bytes()
(OUT / 'ui-test-result.txt').write_text('PASS: system-bar safe bounds, 48dp targets, start/train/results/restart, keyboard input, correct answer and grade, compact screen and larger text.\n')
print((OUT / 'ui-test-result.txt').read_text())
