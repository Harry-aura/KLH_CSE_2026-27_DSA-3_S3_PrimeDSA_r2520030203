"""PrimeDSA Algorithmic Engine Package."""

from .modular_arithmetic import decompose_n_minus_one, square_and_multiply, mod_exp
from .small_primes import FIRST_100_PRIMES, fast_precheck
from .miller_rabin import miller_rabin_test, PrimalityResult
from .prime_generator import generate_probable_prime
from .benchmark_runner import trial_division, run_benchmark_comparison

__all__ = [
    "decompose_n_minus_one",
    "square_and_multiply",
    "mod_exp",
    "FIRST_100_PRIMES",
    "fast_precheck",
    "miller_rabin_test",
    "PrimalityResult",
    "generate_probable_prime",
    "trial_division",
    "run_benchmark_comparison",
]
