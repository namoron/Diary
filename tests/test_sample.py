import pytest

def test_func1():
    assert 1 == 1


def test_func3(app_data):
    assert app_data == 3