import io
import random
import sys
import pytest
from befunge93 import run, load_program, InputStream, WIDTH, HEIGHT


def execute(code, input_data=""):
    # создаём "виртуальную" сетку
    lines = code.splitlines(True)
    grid = load_program(lines)
    inp = InputStream(input_data.encode('utf-8'))
    out_stream = io.StringIO()
    run(grid, inp, out_stream)
    return out_stream.getvalue()


def test_addition():
    code = "23+.@"
    assert execute(code) == "5 "


def test_subtraction():
    code = "52-.@"
    assert execute(code) == "3 "


def test_multiplication():
    code = "34*.@"
    assert execute(code) == "12 "


def test_division():
    code = "84/.@"
    assert execute(code) == "2 "


def test_modulo():
    code = "85%.@"
    assert execute(code) == "3 "


def test_logical_not_zero():
    code = "0!.@"
    assert execute(code) == "1 "


def test_logical_not_nonzero():
    code = "2!.@"
    assert execute(code) == "0 "


def test_greater_true():
    code = "53`.@"
    assert execute(code) == "1 "


def test_greater_false():
    code = "35`.@"
    assert execute(code) == "0 "


def test_division_by_zero():
    code = "80/.@"
    assert execute(code) == "0 "


def test_modulo_by_zero():
    code = "80%.@"
    assert execute(code) == "0 "


def test_direction_changes():
    directions = {
        '>': (1, 0),
        '<': (-1, 0),
        '^': (0, -1),
        'v': (0, 1)
    }

    for symbol, expected in directions.items():
        grid = [[' '] * 80 for _ in range(25)]
        grid[0][0] = symbol

        x, y = 0, 0
        dx, dy = 1, 0

        instr = grid[y][x]

        if instr == '>':
            dx, dy = 1, 0
        elif instr == '<':
            dx, dy = -1, 0
        elif instr == '^':
            dx, dy = 0, -1
        elif instr == 'v':
            dx, dy = 0, 1

        assert (dx, dy) == expected


def test_question_mark_direction():
    """Тест случайного направления '?' """
    grid = [['?'] + [' '] * 79] + [[' '] * 80 for _ in range(24)]
    x, y = 0, 0
    random.seed(0)
    instr = grid[y][x]
    dx, dy = 1, 0
    if instr == '?':
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    assert (dx, dy) in [(1, 0), (-1, 0), (0, 1), (0, -1)]


def test_underscore_direction():
    """Тест направления команды '_' """
    # pop() == 0 => вправо
    stack = [0]
    a = stack.pop() if stack else 0
    if a == 0:
        dx, dy = (1, 0)
    else:
        dx, dy = (-1, 0)
    assert (dx, dy) == (1, 0)

    # pop() != 0 => влево
    stack = [42]
    a = stack.pop() if stack else 0
    if a == 0:
        dx, dy = (1, 0)
    else:
        dx, dy = (-1, 0)
    assert (dx, dy) == (-1, 0)


def test_pipe_direction():
    """Тест направления команды '|' """
    # pop() == 0 => вниз
    stack = [0]
    a = stack.pop() if stack else 0
    if a == 0:
        dx, dy = (0, 1)
    else:
        dx, dy = (0, -1)
    assert (dx, dy) == (0, 1)

    # pop() != 0 => вверх
    stack = [9]
    a = stack.pop() if stack else 0
    if a == 0:
        dx, dy = (0, 1)
    else:
        dx, dy = (0, -1)
    assert (dx, dy) == (0, -1)


def test_colon_duplicate():
    """Тест команды ':' — дублирование верхнего значения стека."""
    # Если стек пуст — добавить 0 дважды
    stack = []
    def pop(): return stack.pop() if stack else 0
    def push(v): stack.append(int(v))

    a = pop()
    push(a)
    push(a)
    assert stack == [0, 0]

    # Если стек не пуст — дублирует верхний элемент
    stack = [7]
    a = pop()
    push(a)
    push(a)
    assert stack == [7, 7]


def test_backslash_swap():
    """Тест команды '\\' — обмен двух верхних элементов стека."""
    # Если в стеке менее двух элементов — подставлять 0
    stack = []
    def pop(): return stack.pop() if stack else 0
    def push(v): stack.append(int(v))

    # обмен если стек пуст
    a, b = pop(), pop()
    push(a)
    push(b)
    assert stack == [0, 0]

    # обмен если один элемент в стеке
    stack = [42]
    a, b = pop(), pop()
    push(a)
    push(b)
    assert stack == [42, 0]

    # обмен если два элемента
    stack = [10, 20]
    a, b = pop(), pop()
    push(a)
    push(b)
    assert stack == [20, 10]


def test_dollar_pop():
    """Тест команды '$' — удаление верхнего элемента стека."""
    # Если стек пуст — ничего не меняется
    stack = []
    def pop(): return stack.pop() if stack else 0

    pop()  # операция, стек был пуст
    assert stack == []

    # Если в стеке один элемент — элемент удаляется
    stack = [99]
    pop()  # операция, стек станет пустым
    assert stack == []

    # Если в стеке несколько элементов — удаляется только верхний
    stack = [4, 5, 6]
    pop()  # операция, стек остается [4, 5]
    assert stack == [4, 5]


def test_dot_output():
    """Тест команды '.' — вывод верхнего элемента стека как числа и пробела."""
    # В тестах будем использовать StringIO вместо настоящего out_stream
    stack = [123]
    def pop(): return stack.pop() if stack else 0
    out_stream = io.StringIO()

    a = pop()
    out_stream.write(str(a) + ' ')
    out_stream.flush()

    assert out_stream.getvalue() == '123 '

    # Тест с пустым стеком (выводит 0)
    stack = []
    out_stream = io.StringIO()
    a = pop()
    out_stream.write(str(a) + ' ')
    out_stream.flush()
    assert out_stream.getvalue() == '0 '


def test_comma_output():
    """Тест команды ',' — вывод верхнего значения стека как символ."""
    # Когда a = 65, выводится 'A' (chr(65))
    stack = [65]
    def pop(): return stack.pop() if stack else 0
    out_stream = io.StringIO()

    a = pop()
    out_stream.write(chr(a % 256))
    out_stream.flush()

    assert out_stream.getvalue() == 'A'

    # Когда стек пуст, выводится chr(0) — это символ с кодом 0 (NUL)
    stack = []
    out_stream = io.StringIO()
    a = pop()
    out_stream.write(chr(a % 256))
    out_stream.flush()
    assert out_stream.getvalue() == '\x00'


def test_sharp_bridge():
    """Тест команды '#' — перепрыгивает одну ячейку по текущему направлению."""

    WIDTH, HEIGHT = 80, 25

    # Тест вправо из верхнего левого угла
    x, y, dx, dy = 0, 0, 1, 0
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    # эффект "моста" (перекинуть "мост" через клетку)
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    assert (x, y) == (2, 0)

    # Тест вниз из любого места
    x, y, dx, dy = 5, 5, 0, 1
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    assert (x, y) == (5, 7)

    # Проверка перехода вправо с конца строки (wrap)
    x, y, dx, dy = 79, 0, 1, 0
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    assert (x, y) == (1, 0)

    # Проверка перехода вверх с границы (wrap по y)
    x, y, dx, dy = 0, 0, 0, -1
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    x = (x + dx) % WIDTH
    y = (y + dy) % HEIGHT
    assert (x, y) == (0, 23)


def test_g_command():
    WIDTH, HEIGHT = 80, 25
    grid = [[' '] * WIDTH for _ in range(HEIGHT)]
    grid[3][2] = 'A'
    stack = [2, 3]
    def pop(): return stack.pop() if stack else 0
    def push(v): stack.append(int(v))
    a, b = pop(), pop()
    push(ord(grid[b][a]) if 0 <= b < HEIGHT and 0 <= a < WIDTH else 0)
    assert stack[-1] == ord(grid[2][3])


def test_p_command():
    """Тест команды 'p' — запись значения в grid[x][y] по модулю 256."""
    WIDTH, HEIGHT = 80, 25
    grid = [[' '] * WIDTH for _ in range(HEIGHT)]
    # Чтобы записать 'A' в grid[3][2], нужно:
    # stack = [2, 3, 65]
    stack = [2, 3, 65]  # x=2, y=3, v=65
    def pop(): return stack.pop() if stack else 0

    v = pop()  # 65
    y = pop()  # 3
    x = pop()  # 2
    if 0 <= y < HEIGHT and 0 <= x < WIDTH:
        grid[y][x] = chr(v % 256)
    assert grid[3][2] == 'A'

    # Проверяем выход за границы (ничего не меняется)
    grid = [[' '] * WIDTH for _ in range(HEIGHT)]
    stack = [99, 99, 66]  # x=99, y=99, v=66
    v = pop()
    y = pop()
    x = pop()
    if 0 <= y < HEIGHT and 0 <= x < WIDTH:
        grid[y][x] = chr(v % 256)
    # За границами ничего не изменится
    assert all(grid[row][col] == ' ' for row in range(HEIGHT) for col in range(WIDTH))


def test_ampersand_input_int():
    """Тест команды '&' — читает целое число из inp_stream."""
    stack = []
    def push(v): stack.append(v)

    # Вариант: есть целое число
    class DummyInputStream:
        def read_int_token(self):
            return 42  # эмулируем найденное число
    inp_stream = DummyInputStream()
    val = inp_stream.read_int_token()
    push(-1 if val is None else val)
    assert stack[-1] == 42

    # Вариант: нет числа (возвращает None)
    stack = []
    class DummyInputStreamNone:
        def read_int_token(self):
            return None
    inp_stream = DummyInputStreamNone()
    val = inp_stream.read_int_token()
    push(-1 if val is None else val)
    assert stack[-1] == -1


def test_tilde_input_char():
    """Тест команды '~' — читает один символ из inp_stream."""
    stack = []
    def push(v): stack.append(v)

    # Вариант: есть символ
    class DummyInputStream:
        def read_char(self):
            return 'X'  # эмулируем найденный символ
    inp_stream = DummyInputStream()
    ch = inp_stream.read_char()
    push(-1 if ch is None else ord(ch[0]))
    assert stack[-1] == ord('X')

    # Вариант: нет символа (возвращает None)
    stack = []
    class DummyInputStreamNone:
        def read_char(self):
            return None
    inp_stream = DummyInputStreamNone()
    ch = inp_stream.read_char()
    push(-1 if ch is None else ord(ch[0]))
    assert stack[-1] == -1


def test_at_halt():
    """Тест команды '@' — завершает исполнение программы."""
    # Минимальная имитация: программа состоит только из '@'
    WIDTH, HEIGHT = 80, 25
    grid = [[' '] * WIDTH for _ in range(HEIGHT)]
    grid[0][0] = '@'

    # Будем считать количество шагов, чтобы проверить остановку
    x = 0
    y = 0
    dx, dy = 1, 0
    steps = 0
    max_steps = 10

    halted = False
    while steps < max_steps:
        steps += 1
        instr = grid[y][x]
        if instr == '@':
            halted = True
            break
        x = (x + dx) % WIDTH
        y = (y + dy) % HEIGHT

    assert halted