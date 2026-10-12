"""FastAPI REST API Routes for Prime Check Service."""

import sys
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from engine.miller_rabin import miller_rabin_test
from engine.prime_generator import generate_probable_prime
from engine.benchmark_runner import run_benchmark_comparison
from .models import (
    PrimeCheckRequest,
    PrimeCheckResponse,
    PrimeGenResponse,
    BenchmarkResponse,
    PresetItem,
)
from .presets import PRESETS

# Ensure Python's arbitrary string-to-int conversion limit handles huge numbers
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)

router = APIRouter(prefix="/api", tags=["Primality Engine"])


@router.post(
    "/check-prime",
    response_model=PrimeCheckResponse,
    summary="Validate arbitrary-precision integer for primality using Miller-Rabin",
)
async def check_prime(payload: PrimeCheckRequest) -> PrimeCheckResponse:
    """Validate whether an arbitrary-precision integer up to 1024 bits (or higher) is prime.

    Executes:
    1. Rapid fast-path pre-checks (even numbers, first 100 small primes).
    2. Bitwise decomposition of (n - 1) into 2^s * d.
    3. Randomized Miller-Rabin test (or deterministic bases for < 64-bit numbers).
    4. Exact execution timing with nanosecond resolution.
    """
    try:
        n = int(payload.number)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse number string into integer: {str(e)}",
        )

    res = miller_rabin_test(
        n=n,
        iterations=payload.iterations,
        use_custom_modpow=payload.use_custom_modpow,
        deterministic_for_small=payload.deterministic_for_small,
    )

    return PrimeCheckResponse(
        number=res.number,
        result=res.result,
        is_prime=res.is_prime,
        confidence=res.confidence_level,
        confidence_formula=res.confidence_formula,
        error_probability=res.error_probability,
        executionTimeMs=res.execution_time_ms,
        executionTimeUs=res.execution_time_us,
        executionTimeNs=res.execution_time_ns,
        bitLength=res.bit_length,
        decimalLength=res.decimal_length,
        roundsCompleted=res.rounds_completed,
        method=res.method,
        deterministic=res.deterministic,
        witness=res.witness,
        s=res.s,
        d=res.d,
        carmichael_number=res.carmichael_number,
        traces=res.traces,
    )


@router.get(
    "/benchmark",
    response_model=BenchmarkResponse,
    summary="Benchmark Miller-Rabin vs Standard Trial Division across bit lengths",
)
async def benchmark(
    iterations: int = Query(default=40, ge=1, le=100, description="Rounds of Miller-Rabin to run"),
) -> BenchmarkResponse:
    """Compare performance of Miller-Rabin vs standard trial division from 16 to 1024 bits."""
    data = run_benchmark_comparison(iterations=iterations)
    return BenchmarkResponse(**data)


@router.get(
    "/generate-prime",
    response_model=PrimeGenResponse,
    summary="Generate a random probable prime of specified bit length",
)
async def generate_prime(
    bits: int = Query(default=1024, ge=3, le=2048, description="Target bit length (e.g. 128, 256, 512, 1024)"),
    iterations: int = Query(default=40, ge=1, le=100, description="Miller-Rabin verification rounds"),
) -> PrimeGenResponse:
    """Generate a cryptographically sound probable prime using secure random bits and Miller-Rabin validation."""
    prime_val, candidates, gen_time_ms, val_res = generate_probable_prime(
        bit_length=bits,
        iterations=iterations,
    )

    validation_response = PrimeCheckResponse(
        number=val_res.number,
        result=val_res.result,
        is_prime=val_res.is_prime,
        confidence=val_res.confidence_level,
        confidence_formula=val_res.confidence_formula,
        error_probability=val_res.error_probability,
        executionTimeMs=val_res.execution_time_ms,
        executionTimeUs=val_res.execution_time_us,
        executionTimeNs=val_res.execution_time_ns,
        bitLength=val_res.bit_length,
        decimalLength=val_res.decimal_length,
        roundsCompleted=val_res.rounds_completed,
        method=val_res.method,
        deterministic=val_res.deterministic,
        witness=val_res.witness,
        s=val_res.s,
        d=val_res.d,
        carmichael_number=val_res.carmichael_number,
        traces=val_res.traces,
    )

    return PrimeGenResponse(
        number=str(prime_val),
        bitLength=val_res.bit_length,
        decimalLength=val_res.decimal_length,
        candidatesTested=candidates,
        generationTimeMs=gen_time_ms,
        confidence=val_res.confidence_level,
        validationResult=validation_response,
    )


@router.get(
    "/presets",
    response_model=List[PresetItem],
    summary="Get catalog of pre-configured primes, Carmichael numbers, and test vectors",
)
async def get_presets() -> List[PresetItem]:
    """Retrieve list of preconfigured test numbers including 128/256/512/1024-bit primes, Carmichael pseudoprimes, etc."""
    return [PresetItem(**p) for p in PRESETS]


@router.get(
    "/health",
    summary="Health check endpoint",
)
async def health_check():
    """Service liveness and health probe."""
    return {
        "status": "healthy",
        "service": "Prime Check Service (Miller-Rabin 1024-bit Engine)",
        "version": "1.0.0",
        "timestamp": time.time(),
    }
