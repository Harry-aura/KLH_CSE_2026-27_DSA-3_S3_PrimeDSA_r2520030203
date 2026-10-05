# PrimeDSA | 1024-Bit Miller–Rabin Primality Engine

An end-to-end, high-performance web-based **Prime Check Service** designed to validate arbitrary-precision integers up to 1024 bits and beyond using the randomized **Miller–Rabin Primality Test**, deterministic 64-bit fallbacks, rapid small-prime sieve pre-checks, benchmark comparisons, and a modern responsive dashboard.

---

## 🌟 Key Features

1. **Arbitrary-Precision BigInt Support (Up to 1024+ Bits)**:
   - Validates integers of arbitrary size (128-bit, 256-bit, 512-bit, 1024-bit, 2048-bit, Mersenne primes $2^{521}-1$, and beyond) with zero integer overflow.
2. **Cryptographic-Grade Randomized Miller–Rabin**:
   - Default $k = 40$ iterations yielding confidence level $\ge 1 - 4^{-40} = 1 - 2^{-80} > 99.9999999999999999999999\%$ and error probability $\le 8.27 \times 10^{-25}$.
3. **Resilience to Carmichael Numbers & Pseudoprimes**:
   - Closed Fermat pseudoprime vulnerabilities ($561, 1105, 1729, 2465, 2821, 6601, 8911, 41041$) by detecting non-trivial square roots of unity modulo $n$.
4. **Deterministic 64-Bit Fallback**:
   - Employs proven 12-base deterministic sets ($\{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37\}$) for $n < 2^{64}$ to yield 100% mathematical certainty.
5. **Algorithmic Transparency & Square-and-Multiply**:
   - Includes custom binary square-and-multiply modular exponentiation and $(n-1) = 2^s \cdot d$ decomposition tracing.
6. **Live Comparative Benchmarking**:
   - Side-by-side execution time comparisons and dynamic log-scale charts showing Miller–Rabin's $O(k \cdot b^3)$ polynomial scaling vs. Trial Division's $O(2^{b/2})$ exponential explosion.
7. **Curated Preset Test Vectors**:
   - Instant loading of 128-bit, 256-bit (secp256k1), 512-bit, 1024-bit (RFC 3526 MODP), Mersenne primes ($2^{127}-1, 2^{521}-1, 2^{607}-1$), Carmichael numbers, and composite semiprimes.
8. **Cryptographic Prime Generator**:
   - Generates cryptographically strong probable primes on demand for requested bit lengths ($128, 256, 512, 1024, 2048$).

---

## 🏛️ Project Architecture

```
PrimeDSA/
├── engine/
│   ├── __init__.py
│   ├── modular_arithmetic.py     # Square-and-multiply modpow, n-1 = 2^s * d decomposition
│   ├── small_primes.py           # First 100+ primes table, fast pre-filter, trivial checks
│   ├── miller_rabin.py           # Deterministic (64-bit) & randomized Miller-Rabin test
│   ├── prime_generator.py        # Cryptographic b-bit prime generator
│   └── benchmark_runner.py       # Benchmark suite (Miller-Rabin vs Trial Division)
├── server/
│   ├── __init__.py
│   ├── app.py                    # FastAPI application, CORS, static mounting
│   ├── routes.py                 # REST API endpoints (/api/check-prime, /api/benchmark, etc.)
│   ├── models.py                 # Pydantic request/response schemas
│   └── presets.py                # Curated primes, Mersenne primes, Carmichael numbers
├── static/
│   ├── index.html                # Modern cyberpunk/glassmorphism dark UI dashboard
│   ├── style.css                 # Custom styles, animations, responsive design
│   └── app.js                    # UI interaction, BigInt handling, Chart.js benchmarks
├── tests/
│   ├── __init__.py
│   ├── test_modular_arithmetic.py # Unit tests for modpow, decomposition
│   ├── test_miller_rabin.py      # Edge cases (0,1,2,3), Carmichael, 1024-bit primes
│   ├── test_prime_generator.py   # Generator validation
│   └── test_api.py               # FastAPI test client for all endpoints
├── requirements.txt              # fastapi, uvicorn, pydantic, pytest
├── run.py                        # Entry point to launch the server
└── README.md
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10+ (Tested on Python 3.12, 3.13, 3.14)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Service
```bash
python run.py
```
Or with Uvicorn directly:
```bash
uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Access the Interfaces
- **Interactive Web UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 REST API Documentation

### 1. Check Primality
`POST /api/check-prime`

#### Request Payload:
```json
{
  "number": "179769313486231590770839156793787453197860296048756011706444423684197180216158519368947833795864925541502180565485980503646440548199239100050792877003355816639229553136239076508735759914822574862575007425302077447712589550957937778424442426617334727629299387668709205606050270810842907692932019128194467627007",
  "iterations": 40,
  "use_custom_modpow": false,
  "deterministic_for_small": true
}
```

#### Response:
```json
{
  "number": "1797693134862315907708391...",
  "result": "Prime",
  "is_prime": true,
  "confidence": "99.9999999999999999999999%",
  "confidence_formula": "1 - 4^(-40) = 1 - 2^(-80)",
  "error_probability": "8.2718e-25",
  "executionTimeMs": 1.485,
  "executionTimeUs": 1485.0,
  "executionTimeNs": 1485000,
  "bitLength": 1024,
  "decimalLength": 309,
  "roundsCompleted": 40,
  "method": "Probabilistic Miller-Rabin (40 rounds)",
  "deterministic": false,
  "witness": null,
  "s": 1,
  "d": "898846567431157953854195783968937265989301480243780058532222118420985901080792596844739168979324627707510902827429902518232202740996195500253964385016779083196147765681195382543678799574112874312875037126510387238562947754789688892122221213308667363814649693834354602803025135405421453846466009564097233813503",
  "carmichael_number": false,
  "traces": [...]
}
```

---

### 2. Generate Random Prime
`GET /api/generate-prime?bits=1024&iterations=40`

#### Response:
```json
{
  "number": "1384029482...",
  "bitLength": 1024,
  "decimalLength": 309,
  "candidatesTested": 142,
  "generationTimeMs": 284.15,
  "confidence": "99.9999999999999999999999%",
  "validationResult": { ... }
}
```

---

### 3. Performance Benchmark
`GET /api/benchmark?iterations=40`

Compares Miller–Rabin execution time against Trial Division across bit lengths: `16, 24, 32, 48, 64, 128, 256, 512, 1024`.

---

### 4. Presets Catalog
`GET /api/presets`

Returns the curated list of test numbers: 128-1024 bit primes, Mersenne primes ($2^{127}-1, 2^{521}-1$), Carmichael numbers ($561, 1105, 1729, 2465, 2821, 6601, 8911$), and composite numbers.

---

## 🧪 Automated Testing

Run the full automated test suite:
```bash
python -m pytest tests/ -v
```

All 29 tests verify:
- Edge cases: $0, 1, 2, 3$, negatives, even numbers, powers of 2.
- Small primes sieve $< 1000$ and small composites.
- Carmichael numbers resilience (zero false positives on $561, 1105, 1729, \dots$).
- Cryptographic primes (128-bit, 256-bit secp256k1, 512-bit, 1024-bit RFC 3526).
- Binary square-and-multiply modular exponentiation vs native `pow`.
- Arbitrary-precision prime generator.
- All REST API endpoints and error handling.
