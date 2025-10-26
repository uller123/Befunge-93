import io
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
