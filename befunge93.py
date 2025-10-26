#!/usr/bin/env python3
import sys
import argparse
from io import StringIO
import io
import random
from collections import deque


WIDTH = 80
HEIGHT = 25


def load_program(lines):
    grid = [[' ']*WIDTH for _ in range(HEIGHT)]
    for y, line in enumerate(lines[:HEIGHT]):
        for x, ch in enumerate(line.rstrip('\n')[:WIDTH]):
            grid[y][x] = ch
    return grid


class InputStream:
    def __init__(self, data=b''):
        self.buf = data
        self.pos = 0
        self.tokens = deque()
        self._populate_tokens()

    def _populate_tokens(self):
        s = self.buf.decode('utf-8', errors='replace')
        for p in s.strip().split():
            self.tokens.append(p)

    def read_char(self):
        if self.pos >= len(self.buf):
            return None
        b = self.buf[self.pos:self.pos+1]
        self.pos += 1
        return b.decode('utf-8', errors='replace')

    def read_int_token(self):
        if self.tokens:
            try:
                return int(self.tokens.popleft())
            except ValueError:
                return None
        return None


def run(grid, inp_stream, out_stream):
    x = 0
    y = 0
    dx, dy = 1, 0
    stack = []
    string_mode = False

    def push(v): stack.append(int(v))
    def pop(): return stack.pop() if stack else 0

    steps = 0
    max_steps = 10_000_000
    while steps < max_steps:
        steps += 1
        instr = grid[y][x]
        if string_mode and instr != '"':
            push(ord(instr))
        else:
            if instr == ' ':
                pass
            elif instr == '"':
                string_mode = not string_mode
            elif instr in '0123456789':
                push(int(instr))
            elif instr == '+':
                a, b = pop(), pop()
                push(b + a)
            elif instr == '-':
                a, b = pop(), pop()
                push(b - a)
            elif instr == '*':
                a, b = pop(), pop()
                push(b * a)
            elif instr == '/':
                a, b = pop(), pop()
                push(0 if a == 0 else b // a)
            elif instr == '%':
                a, b = pop(), pop()
                push(0 if a == 0 else b % a)
            elif instr == '!':
                a = pop()
                push(0 if a else 1)
            elif instr == '`':
                a, b = pop(), pop()
                push(1 if b > a else 0)
            elif instr == '>':
                dx, dy = 1, 0
            elif instr == '<':
                dx, dy = -1, 0
            elif instr == '^':
                dx, dy = 0, -1
            elif instr == 'v':
                dx, dy = 0, 1
            elif instr == '?':
                dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            elif instr == '_':
                dx, dy = (1,0) if pop() == 0 else (-1,0)
            elif instr == '|':
                dx, dy = (0,1) if pop() == 0 else (0,-1)
            elif instr == ':':
                a = pop(); push(a); push(a)
            elif instr == '\\':
                a, b = pop(), pop()
                push(a)
                push(b)
            elif instr == '$':
                pop()
            elif instr == '.':
                a = pop()
                out_stream.write(str(a) + ' ')
                out_stream.flush()
            elif instr == ',':
                a = pop()
                out_stream.write(chr(a % 256))
                out_stream.flush()
            elif instr == '#':
                x = (x + dx) % WIDTH
                y = (y + dy) % HEIGHT
            elif instr == 'g':
                a, b = pop(), pop()
                push(ord(grid[b][a]) if 0 <= b < HEIGHT and 0 <= a < WIDTH else 0)
            elif instr == 'p':
                a, b, v = pop(), pop(), pop()
                if 0 <= b < HEIGHT and 0 <= a < WIDTH:
                    grid[b][a] = chr(v % 256)
            elif instr == '&':
                val = inp_stream.read_int_token()
                push(-1 if val is None else val)
            elif instr == '~':
                ch = inp_stream.read_char()
                push(-1 if ch is None else ord(ch[0]))
            elif instr == '@':
                break
        x = (x + dx) % WIDTH
        y = (y + dy) % HEIGHT
    return


def main():
    parser = argparse.ArgumentParser(
        description="Befunge-93 Interpreter — исполняет 2D-программы Befunge."
    )
    parser.add_argument("program", help="Путь к файлу с программой Befunge-93.")
    parser.add_argument("--input", "-i", help="Файл с вводом для программы.", default=None)
    args = parser.parse_args()

    try:
        with open(args.program, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Ошибка: файл {args.program} не найден.", file=sys.stderr)
        sys.exit(1)

    runtime_input = b""
    if args.input:
        try:
            with open(args.input, "rb") as f:
                runtime_input = f.read()
        except FileNotFoundError:
            print(f"Ошибка: файл ввода {args.input} не найден.", file=sys.stderr)
            sys.exit(1)

    grid = load_program(lines)
    inp_stream = InputStream(runtime_input)
    run(grid, inp_stream, sys.stdout)


if __name__ == "__main__":
    main()
