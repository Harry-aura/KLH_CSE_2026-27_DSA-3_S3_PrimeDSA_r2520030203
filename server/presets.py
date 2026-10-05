"""Curated Presets Library for Primality Testing.

Provides verified primes across various bit-lengths (128, 256, 512, 1024-bit),
Mersenne primes, Carmichael numbers (Fermat pseudoprimes), and composite semiprimes.
"""

from typing import List, Dict, Any

PRESETS: List[Dict[str, Any]] = [
    # --- 1. Cryptographic Bit-Length Primes ---
    {
        "id": "prime-128",
        "name": "128-Bit Cryptographic Prime",
        "category": "primes",
        "bitLength": 128,
        "description": "Standard 128-bit prime integer often used in lightweight symmetric cryptography.",
        "value": "340282366920938463463374607431768211297",
    },
    {
        "id": "prime-256",
        "name": "256-Bit Prime (secp256k1 Field Size)",
        "category": "primes",
        "bitLength": 256,
        "description": "The 256-bit prime modulus 2^256 - 2^32 - 977 powering the Bitcoin elliptic curve (secp256k1).",
        "value": "115792089237316195423570985008687907853269984665640564039457584007908834671663",
    },
    {
        "id": "prime-512",
        "name": "512-Bit Cryptographic Prime",
        "category": "primes",
        "bitLength": 512,
        "description": "512-bit prime factor suitable for cryptographic key generation.",
        "value": "8331504005952028544408906167693035710639111048204012949355625002480948723637879031873527982478272729481094204240328923412074767284218625828910636320581471",
    },
    {
        "id": "prime-1024",
        "name": "1024-Bit Cryptographic Prime (RFC 3526 MODP Group 2)",
        "category": "primes",
        "bitLength": 1024,
        "description": "1024-bit prime modulus 2^1024 - 2^960 - 1 + 2^64 * {[2^894 pi] + 129093} specified in RFC 3526 for Diffie-Hellman Key Exchange.",
        "value": "179769313486231590770839156793787453197860296048756011706444423684197180216158519368947833795864925541502180565485980503646440548199239100050792877003355816639229553136239076508735759914822574862575007425302077447712589550957937778424442426617334727629299387668709205606050270810842907692932019128194467627007",
    },

    # --- 2. Mersenne Primes ---
    {
        "id": "mersenne-127",
        "name": "Mersenne Prime M127 (2^127 - 1)",
        "category": "mersenne",
        "bitLength": 127,
        "description": "Discovered by Édouard Lucas in 1876; was the largest known prime for 75 years.",
        "value": str((1 << 127) - 1),
    },
    {
        "id": "mersenne-521",
        "name": "Mersenne Prime M521 (2^521 - 1)",
        "category": "mersenne",
        "bitLength": 521,
        "description": "521-bit Mersenne prime discovered in 1952 by Robinson, used in NIST P-521 elliptic curve.",
        "value": str((1 << 521) - 1),
    },
    {
        "id": "mersenne-607",
        "name": "Mersenne Prime M607 (2^607 - 1)",
        "category": "mersenne",
        "bitLength": 607,
        "description": "607-bit Mersenne prime discovered in 1952 using SWAC computer.",
        "value": str((1 << 607) - 1),
    },

    # --- 3. Carmichael Numbers (Fermat Pseudoprimes) ---
    {
        "id": "carmichael-561",
        "name": "Carmichael 561 (Smallest Carmichael)",
        "category": "carmichael",
        "bitLength": 10,
        "description": "3 * 11 * 17 = 561. Satisfies a^560 = 1 (mod 561) for all gcd(a,561)=1, completely fooling Fermat's test, but caught instantly by Miller-Rabin.",
        "value": "561",
    },
    {
        "id": "carmichael-1105",
        "name": "Carmichael 1105",
        "category": "carmichael",
        "bitLength": 11,
        "description": "5 * 13 * 17 = 1105. Strong Fermat pseudoprime to all coprime bases.",
        "value": "1105",
    },
    {
        "id": "carmichael-1729",
        "name": "Carmichael 1729 (Ramanujan-Hardy Number)",
        "category": "carmichael",
        "bitLength": 11,
        "description": "7 * 13 * 19 = 1729. The smallest number expressible as the sum of two cubes in two different ways (1^3+12^3 = 9^3+10^3) and also a Carmichael number.",
        "value": "1729",
    },
    {
        "id": "carmichael-2465",
        "name": "Carmichael 2465",
        "category": "carmichael",
        "bitLength": 12,
        "description": "5 * 17 * 29 = 2465. Carmichael pseudoprime.",
        "value": "2465",
    },
    {
        "id": "carmichael-2821",
        "name": "Carmichael 2821",
        "category": "carmichael",
        "bitLength": 12,
        "description": "7 * 13 * 31 = 2821. Carmichael pseudoprime.",
        "value": "2821",
    },
    {
        "id": "carmichael-6601",
        "name": "Carmichael 6601",
        "category": "carmichael",
        "bitLength": 13,
        "description": "7 * 23 * 41 = 6601. Carmichael pseudoprime.",
        "value": "6601",
    },
    {
        "id": "carmichael-41041",
        "name": "Carmichael 41041 (4 Prime Factors)",
        "category": "carmichael",
        "bitLength": 16,
        "description": "7 * 11 * 13 * 41 = 41041. Carmichael number composed of 4 distinct primes.",
        "value": "41041",
    },

    # --- 4. Composite & Edge Cases ---
    {
        "id": "mersenne-composite-67",
        "name": "Mersenne Composite (2^67 - 1)",
        "category": "composites",
        "bitLength": 67,
        "description": "Factored by Cole in 1903 after 3 years of Sundays: 193,707,721 * 761,838,257,287.",
        "value": str((1 << 67) - 1),
    },
    {
        "id": "rsa-128-composite",
        "name": "128-bit Semiprime (RSA-style Composite)",
        "category": "composites",
        "bitLength": 128,
        "description": "Product of two 64-bit primes: 18446744073709551557 * 18446744073709551533.",
        "value": str(18446744073709551557 * 18446744073709551533),
    },
    {
        "id": "power-of-two",
        "name": "2^512 Even Composite (Power of 2)",
        "category": "composites",
        "bitLength": 513,
        "description": "Extremely large pure power of 2: 2^512. Trivial composite caught by fast-path pre-check.",
        "value": str(1 << 512),
    },
]
