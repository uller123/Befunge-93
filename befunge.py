import sys
import random
from collections import deque

WIDTH = 80
HEIGHT = 25

def load_program(lines):
    # Normalize lines to WIDTH, HEIGHT
    grid = [[' ']*WIDTH for _ in range(HEIGHT)]
    for y, line in enumerate(lines[:HEIGHT]):
        for x, ch in enumerate(line.rstrip('\n')[:WIDTH]):
            grid[y][x] = ch
    return grid

class InputStream:
    def __init__(self, data=b''):
        # data: bytes
        self.buf = data
        self.pos = 0
        self.tokens = deque()
        self._populate_tokens()

    def _populate_tokens(self):
        # Prepare integer tokens (for &)
        s = self.buf.decode('utf-8', errors='replace')
        # split by whitespace for integers
        parts = s.strip().split()
        for p in parts:
            self.tokens.append(p)

    def read_char(self):
        if self.pos >= len(self.buf):
            return None
        b = self.buf[self.pos:self.pos+1]
        self.pos += 1
        try:
            return b.decode('utf-8', errors='replace')
        except Exception:
            return chr(b[0])

    def read_int_token(self):
        if self.tokens:
            t = self.tokens.popleft()
            try:
                return int(t)
            except Exception:
                return None
        else:
            return None

def run(grid, inp_stream, out_stream):
    x = 0
    y = 0
    dx, dy = 1, 0
    stack = []
    string_mode = False

    def push(v):
        stack.append(int(v))

    def pop():
        if stack:
            return stack.pop()
        else:
            return 0

    steps = 0
    max_steps = 10000000  # safety cap, but won't be hit in tests normally

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
                a = pop(); b = pop(); push(b + a)
            elif instr == '-':
                a = pop(); b = pop(); push(b - a)
            elif instr == '*':
                a = pop(); b = pop(); push(b * a)
            elif instr == '/':
                a = pop(); b = pop()
                if a == 0:
                    push(0)
                else:
                    push(int(b / a))
            elif instr == '%':
                a = pop(); b = pop()
                if a == 0:
                    push(0)
                else:
                    push(b % a)
            elif instr == '!':
                a = pop(); push(0 if a else 1)
            elif instr == '`':
                a = pop(); b = pop(); push(1 if b > a else 0)
            elif instr == '>':
                dx, dy = 1, 0
            elif instr == '<':
                dx, dy = -1, 0
            elif instr == '^':
                dx, dy = 0, -1
            elif instr == 'v':
                dx, dy = 0, 1
            elif instr == '?':
                d = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                dx, dy = d
            elif instr == '_':
                a = pop()
                if a == 0:
                    dx, dy = 1, 0
                else:
                    dx, dy = -1, 0
            elif instr == '|':
                a = pop()
                if a == 0:
                    dx, dy = 0, 1
                else:
                    dx, dy = 0, -1
            elif instr == ':':
                a = pop()
                push(a); push(a)
            elif instr == '\\':
                a = pop(); b = pop()
                push(a); push(b)
            elif instr == '$':
                _ = pop()
            elif instr == '.':
                a = pop()
                out_stream.write(str(a))
                out_stream.write(' ')
                out_stream.flush()
            elif instr == ',':
                a = pop()
                out_stream.write(chr(a % 256))
                out_stream.flush()
            elif instr == '#':
                # move one step in current direction (bridge)
                x = (x + dx) % WIDTH
                y = (y + dy) % HEIGHT
            elif instr == 'g':
                a = pop(); b = pop()
                if 0 <= b < HEIGHT and 0 <= a < WIDTH:
                    out = grid[b][a]
                    push(ord(out))
                else:
                    push(0)
            elif instr == 'p':
                a = pop(); b = pop(); v = pop()
                if 0 <= b < HEIGHT and 0 <= a < WIDTH:
                    grid[b][a] = chr(v % 256)
            elif instr == '&':
                val = inp_stream.read_int_token()
                if val is None:
                    push(-1)
                else:
                    push(val)
            elif instr == '~':
                ch = inp_stream.read_char()
                if ch is None:
                    push(-1)
                else:
                    push(ord(ch[0]))
            elif instr == '@':
                break
            else:
                # unknown -> no-op
                pass

        # move IP
        x = (x + dx) % WIDTH
        y = (y + dy) % HEIGHT

    # finished
    return

def main(argv):
    import io
    if len(argv) >= 2:
        prog_path = argv[1]
        with open(prog_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    else:
        # read program from stdin entirely
        lines = sys.stdin.read().splitlines(True)

    # If user provided an input-file argument, load it as runtime input
    runtime_input = b''
    if len(argv) >= 3:
        with open(argv[2], 'rb') as f:
            runtime_input = f.read()
    else:
        runtime_input = b''

    grid = load_program(lines)
    inp_stream = InputStream(runtime_input)
    out_stream = sys.stdout
    run(grid, inp_stream, out_stream)

if __name__ == '__main__':
    main(sys.argv)
