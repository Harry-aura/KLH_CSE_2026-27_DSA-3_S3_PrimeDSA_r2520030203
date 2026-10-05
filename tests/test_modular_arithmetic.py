"""Unit tests for modular arithmetic and bitwise decomposition."""

import pytest
from engine.modular_arithmetic import decompose_n_minus_one, square_and_multiply, mod_exp, get_integer_metrics


def test_decompose_n_minus_one_standard():
    # 13 - 1 = 12 = 2^2 * 3 -> s=2, d=3
    s, d = decompose_n_minus_one(13)
    assert s == 2
    assert d == 3
    assert (2 ** s) * d == 12

    # 17 - 1 = 16 = 2^4 * 1 -> s=4, d=1
    s, d = decompose_n_minus_one(17)
    assert s == 4
    assert d == 1
    assert (2 ** s) * d == 16

    # 561 - 1 = 560 = 2^4 * 35 -> s=4, d=35
    s, d = decompose_n_minus_one(561)
    assert s == 4
    assert d == 35
    assert (2 ** s) * d == 560


def test_decompose_n_minus_one_large_prime():
    # 1024-bit integer decomposition
    n = (1 << 1024) - 105  # Odd 1024-bit integer
    s, d = decompose_n_minus_one(n)
    assert s >= 1
    assert d % 2 == 1  # d must be odd
    assert ((1 << s) * d) == (n - 1)


def test_decompose_invalid_inputs():
    with pytest.raises(ValueError):
        decompose_n_minus_one(2)  # n <= 2
    with pytest.raises(ValueError):
        decompose_n_minus_one(1)  # n <= 2
    with pytest.raises(ValueError):
        decompose_n_minus_one(10)  # Even integer


def test_square_and_multiply_small():
    # 3^4 mod 7 = 81 mod 7 = 4
    assert square_and_multiply(3, 4, 7) == 4
    # 7^12 mod 13 = 1 (Fermat's little theorem)
    assert square_and_multiply(7, 12, 13) == 1
    # 2^10 mod 1000 = 1024 mod 1000 = 24
    assert square_and_multiply(2, 10, 1000) == 24


def test_square_and_multiply_vs_pow_1024_bit():
    base = 1234567890123456789
    exp = (1 << 256) - 189
    mod = (1 << 1024) - 105

    custom_res = square_and_multiply(base, exp, mod)
    native_res = pow(base, exp, mod)
    assert custom_res == native_res


def test_mod_exp_dispatcher():
    base, exp, mod = 42, 1234567, 1000000007
    assert mod_exp(base, exp, mod, use_custom=True) == mod_exp(base, exp, mod, use_custom=False)


def test_integer_metrics():
    m0 = get_integer_metrics(0)
    assert m0["bit_length"] == 0
    assert m0["decimal_length"] == 1

    m1024 = get_integer_metrics((1 << 1024) - 1)
    assert m1024["bit_length"] == 1024
    assert m1024["decimal_length"] > 300
