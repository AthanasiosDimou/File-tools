"""
Euler's Totient Theorem for RSA Key Factorization
==================================================

How Euler's Totient Theorem Works:
-----------------------------------

Euler's Totient Function φ(n) counts the number of integers from 1 to n that are coprime with n.
For an RSA public key (n, e), where n = p * q (two prime numbers):
    φ(n) = (p - 1) * (q - 1)

The RSA Algorithm uses:
    d ≡ e^(-1) (mod φ(n))  — to find the private exponent

If we can find φ(n), we can compute the private exponent d and decrypt messages.

The Challenge:
---------------
To find φ(n), we need to factor n into its primes p and q. This is the hard problem.
However, if n is small or has weak factors, we can attempt factorization.

Method: Fermat's Factorization
------------------------------
For numbers that are a product of two primes close to each other:
    n = p * q, where p ≈ q
    
We can use: n = a² - b² = (a-b)(a+b)
So: p = a - b, q = a + b

Start with a = ceil(sqrt(n)) and increment until we find a perfect square: a² - n = b²

Example:
--------
If n = 21 = 3 * 7
    sqrt(21) ≈ 4.58, so start with a = 5
    5² - 21 = 25 - 21 = 4 = 2²
    p = 5 - 2 = 3
    q = 5 + 2 = 7
    φ(21) = 2 * 6 = 12

Time Complexity:
-----------------
- If p and q are close: FAST (polynomial time)
- If p and q are far apart: SLOW (exponential time)
- Modern RSA uses primes that are far apart to prevent this attack
"""

import math
from typing import Optional, Tuple


def gcd(a: int, b: int) -> int:
    """
    Compute the Greatest Common Divisor using Euclidean algorithm.
    Used to verify if two numbers are coprime.
    """
    while b:
        a, b = b, a % b
    return a


def euler_totient(n: int) -> int:
    """
    Calculate Euler's Totient φ(n) by finding all coprime integers.
    
    WARNING: This is O(n) and ONLY works for small n!
    For real RSA keys, this is infeasible.
    
    Args:
        n: The integer to compute totient for
    
    Returns:
        Count of integers from 1 to n that are coprime with n
    """
    count = 0
    for i in range(1, n + 1):
        if gcd(i, n) == 1:
            count += 1
    return count


def euler_totient_fast(p: int, q: int) -> int:
    """
    Fast calculation of Euler's Totient if we know the prime factors.
    
    If n = p * q (where p and q are prime):
        φ(n) = (p - 1) * (q - 1)
    
    Args:
        p: First prime factor
        q: Second prime factor
    
    Returns:
        φ(n) = φ(p * q)
    """
    return (p - 1) * (q - 1)


def fermat_factorization(n: int, max_iterations: int = 1000000) -> Optional[Tuple[int, int]]:
    """
    Attempt to factor n using Fermat's factorization method.
    
    This works well when n = p * q and p ≈ q (close primes).
    
    Algorithm:
    1. Start with a = ceil(sqrt(n))
    2. Compute b² = a² - n
    3. If b is an integer, we found: n = (a-b)(a+b)
    4. If not, increment a and try again
    
    Args:
        n: The number to factor
        max_iterations: Maximum attempts (safety limit)
    
    Returns:
        Tuple of (p, q) if factorization found, None otherwise
    """
    if n % 2 == 0:
        return (2, n // 2)
    
    a = math.ceil(math.sqrt(n))
    
    for _ in range(max_iterations):
        b_squared = a * a - n
        b = math.isqrt(b_squared)
        
        # Check if b² == b_squared (perfect square)
        if b * b == b_squared:
            p = a - b
            q = a + b
            if p > 1 and q > 1:  # Valid factors
                return (p, q)
        
        a += 1
    
    return None  # Could not factor


def rsa_crack(n: int, e: int, c: int) -> Optional[int]:
    """
    Attempt to crack an RSA message using Euler's Totient Theorem.
    
    Given:
        n: RSA modulus (public)
        e: RSA exponent (public)
        c: Ciphertext (what we're trying to decrypt)
    
    Process:
        1. Factor n into primes p and q
        2. Calculate φ(n) = (p-1)(q-1)
        3. Find d where e*d ≡ 1 (mod φ(n))
        4. Decrypt: m = c^d mod n
    
    Args:
        n: RSA modulus
        e: Public exponent
        c: Ciphertext to decrypt
    
    Returns:
        Plaintext message, or None if factorization fails
    """
    # Try to factor n
    factors = fermat_factorization(n)
    if not factors:
        return None
    
    p, q = factors
    phi_n = euler_totient_fast(p, q)
    
    # Find modular multiplicative inverse of e mod φ(n)
    d = mod_inverse(e, phi_n)
    if d is None:
        return None
    
    # Decrypt the message
    plaintext = pow(c, d, n)
    return plaintext


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Find modular multiplicative inverse of a modulo m.
    Returns d where (a * d) ≡ 1 (mod m)
    
    Uses Extended Euclidean Algorithm.
    
    Args:
        a: The number to find inverse of
        m: The modulus
    
    Returns:
        d if inverse exists, None otherwise
    """
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y
    
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        return None  # Inverse doesn't exist
    return (x % m + m) % m


if __name__ == "__main__":
    # Example: Factor a composite of two close primes
    p, q = 61, 53
    n = p * q
    print(f"Testing Fermat Factorization:")
    print(f"Original primes: p={p}, q={q}")
    print(f"n = {n}")
    
    factors = fermat_factorization(n)
    if factors:
        print(f"Factored as: {factors}")
        print(f"Verification: {factors[0]} * {factors[1]} = {factors[0] * factors[1]}")
    
    print(f"\nEuler's Totient:")
    phi = euler_totient_fast(p, q)
    print(f"φ({n}) = ({p}-1) * ({q}-1) = {phi}")
    
    # Simple RSA example
    print(f"\nRSA Example:")
    e = 17
    m = 42  # Message
    c = pow(m, e, n)  # Encrypt
    print(f"Message: {m}")
    print(f"Encrypted: {c}")
    
    d = mod_inverse(e, phi)
    decrypted = pow(c, d, n)
    print(f"Decrypted: {decrypted}")
    print(f"Match: {decrypted == m}")
