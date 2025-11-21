"""
Автоматические тесты для упражнения Red-Green-Refactor
"""

import pytest


def test_add_basic():
    """Базовый тест сложения"""
    from solution import add

    assert add(2, 3) == 5


def test_add_negative():
    """Тест сложения отрицательных чисел"""
    from solution import add

    assert add(-1, 1) == 0


def test_add_zero():
    """Тест сложения с нулем"""
    from solution import add

    assert add(0, 0) == 0
    assert add(5, 0) == 5
    assert add(0, 5) == 5


def test_add_float():
    """Тест сложения чисел с плавающей точкой"""
    from solution import add

    assert add(1.5, 2.5) == 4.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
