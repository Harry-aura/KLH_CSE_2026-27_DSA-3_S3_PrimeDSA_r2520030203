"""Pydantic Request and Response Models for Prime Check Service."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class PrimeCheckRequest(BaseModel):
    """Request payload for /api/check-prime."""
    number: str = Field(..., description="Integer string up to 1024 bits and beyond (arbitrary precision)")
    iterations: int = Field(default=40, ge=1, le=500, description="Number of Miller-Rabin rounds (default 40)")
    use_custom_modpow: bool = Field(default=False, description="Whether to use explicit square-and-multiply modpow")
    deterministic_for_small: bool = Field(default=True, description="Whether to use deterministic base set for < 64 bits")

    @field_validator("number")
    @classmethod
    def validate_number_format(cls, v: str) -> str:
        clean_v = v.strip().replace(" ", "").replace("_", "").replace(",", "")
        if not clean_v:
            raise ValueError("Number string cannot be empty")
        # Allow negative sign or positive
        test_v = clean_v[1:] if clean_v[0] in ("-", "+") else clean_v
        if not test_v.isdigit():
            raise ValueError(f"Invalid integer format: '{v}' contains non-digit characters")
        return clean_v


class RoundTraceModel(BaseModel):
    """Trace details for a single test round."""
    round_index: int
    base_a: str
    initial_x: str
    passed: bool
    reason: str


class PrimeCheckResponse(BaseModel):
    """Response payload for /api/check-prime."""
    number: str
    result: str  # "Prime" or "Composite"
    is_prime: bool
    confidence: str
    confidence_formula: str
    error_probability: str
    executionTimeMs: float
    executionTimeUs: float
    executionTimeNs: int
    bitLength: int
    decimalLength: int
    roundsCompleted: int
    method: str
    deterministic: bool
    witness: Optional[str] = None
    s: Optional[int] = None
    d: Optional[str] = None
    carmichael_number: bool = False
    traces: List[Dict[str, Any]] = []


class PrimeGenResponse(BaseModel):
    """Response payload for /api/generate-prime."""
    number: str
    bitLength: int
    decimalLength: int
    candidatesTested: int
    generationTimeMs: float
    confidence: str
    validationResult: PrimeCheckResponse


class BenchmarkItem(BaseModel):
    """Benchmark item comparison across bit lengths."""
    bit_length: int
    sample_prime_preview: str
    miller_rabin_time_ms: float
    miller_rabin_time_us: float
    trial_division_time_ms: float
    trial_division_completed: bool
    trial_division_projected_ms: float
    speedup_factor: float
    status: str


class BenchmarkResponse(BaseModel):
    """Response payload for /api/benchmark."""
    iterations: int
    results: List[BenchmarkItem]
    complexity_analysis: Dict[str, str]


class PresetItem(BaseModel):
    """Preset entry model."""
    id: str
    name: str
    category: str
    bitLength: int
    description: str
    value: str
