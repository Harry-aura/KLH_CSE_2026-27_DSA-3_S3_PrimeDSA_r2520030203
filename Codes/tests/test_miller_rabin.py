"""Unit tests for Miller-Rabin primality test engine and edge cases."""

import pytest
from engine.miller_rabin import miller_rabin_test, calculate_confidence_strings


def test_edge_cases_zero_one_negatives():
    for val in [-10, -1, 0, 1]:
        res = miller_rabin_test(val)
        assert not res.is_prime
        assert res.result == "Composite"


def test_base_primes_two_and_three():
    res2 = miller_rabin_test(2)
    assert res2.is_prime
    assert res2.result == "Prime"

    res3 = miller_rabin_test(3)
    assert res3.is_prime
    assert res3.result == "Prime"


def test_even_numbers_and_powers_of_two():
    for val in [4, 6, 8, 100, 1024, 1 << 64, 1 << 512]:
        res = miller_rabin_test(val)
        assert not res.is_prime
        assert res.result == "Composite"
        assert res.witness == "2" or res.witness is not None


def test_small_primes_sieve():
    known_small_primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for p in known_small_primes:
        res = miller_rabin_test(p)
        assert res.is_prime
        assert res.result == "Prime"


def test_small_composites():
    known_composites = [9, 15, 21, 25, 27, 33, 35, 49, 51, 65, 77, 85, 91, 93, 95]
    for c in known_composites:
        res = miller_rabin_test(c)
        assert not res.is_prime
        assert res.result == "Composite"
        assert res.witness is not None


def test_carmichael_numbers_resilience():
    """Carmichael numbers fool Fermat's test a^(n-1) = 1 (mod n) but MUST fail Miller-Rabin."""
    carmichael_numbers = [561, 1105, 1729, 2465, 2821, 6601, 8911, 41041]
    for c in carmichael_numbers:
        res = miller_rabin_test(c, iterations=40)
        assert not res.is_prime, f"Carmichael number {c} was incorrectly marked as prime!"
        assert res.result == "Composite"
        assert res.witness is not None


def test_mersenne_primes():
    # M127 = 2^127 - 1 (127-bit prime)
    m127 = (1 << 127) - 1
    res127 = miller_rabin_test(m127, iterations=40)
    assert res127.is_prime
    assert res127.result == "Prime"
    assert res127.bit_length == 127

    # M521 = 2^521 - 1 (521-bit prime)
    m521 = (1 << 521) - 1
    res521 = miller_rabin_test(m521, iterations=40)
    assert res521.is_prime
    assert res521.result == "Prime"
    assert res521.bit_length == 521


def test_mersenne_composite():
    # M67 = 2^67 - 1 is composite
    m67 = (1 << 67) - 1
    res67 = miller_rabin_test(m67, iterations=40)
    assert not res67.is_prime
    assert res67.result == "Composite"


def test_known_1024_bit_cryptographic_prime():
    # RFC 3526 1024-bit MODP Group 2 prime
    p1024 = int(
        "179769313486231590770839156793787453197860296048756011706444423684197180216158519368947833795864925541502180565485980503646440548199239100050792877003355816639229553136239076508735759914822574862575007425302077447712589550957937778424442426617334727629299387668709205606050270810842907692932019128194467627007"
    )
    res = miller_rabin_test(p1024, iterations=40)
    assert res.is_prime
    assert res.result == "Prime"
    assert res.bit_length == 1024
    assert res.execution_time_ms < 500  # Should be fast (< 50ms typical)
    assert "99.99" in res.confidence_level


def test_confidence_calculation():
    conf_str, formula, err_prob = calculate_confidence_strings(40, is_deterministic=False)
    assert "99.99" in conf_str
    assert "1 - 4^(-40)" in formula
    assert "e-25" in err_prob

    conf_det, form_det, err_det = calculate_confidence_strings(40, is_deterministic=True)
    assert "Deterministic" in conf_det
    assert err_det == "0.0"
