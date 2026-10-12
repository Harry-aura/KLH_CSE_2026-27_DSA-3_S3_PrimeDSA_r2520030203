"""Unit tests for arbitrary-precision prime generator."""

import pytest
from engine.prime_generator import generate_probable_prime
from engine.miller_rabin import miller_rabin_test


def test_generate_small_primes():
    prime, candidates, elapsed, result = generate_probable_prime(bit_length=16, iterations=20)
    assert prime.bit_length() == 16
    assert result.is_prime
    assert result.result == "Prime"


def test_generate_128_bit_prime():
    prime, candidates, elapsed, result = generate_probable_prime(bit_length=128, iterations=30)
    assert prime.bit_length() == 128
    assert result.is_prime
    # Verify with independent check
    verify = miller_rabin_test(prime, iterations=40)
    assert verify.is_prime


def test_generate_256_bit_prime():
    prime, candidates, elapsed, result = generate_probable_prime(bit_length=256, iterations=30)
    assert prime.bit_length() == 256
    assert result.is_prime


def test_generate_invalid_bits():
    with pytest.raises(ValueError):
        generate_probable_prime(bit_length=1)
