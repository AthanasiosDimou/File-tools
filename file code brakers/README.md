# File Code Breakers

Collection of tools for cracking encrypted files and hashes using brute force attacks, dictionary attacks, and cryptographic exploits.

## Projects

### [Password Brute Force](./password%20brute%20force/)

PDF password cracker with in-memory batching optimization.

**Features:**
- Efficient in-memory PDF loading (no repeated disk I/O)
- Multithreaded password testing
- Dictionary + brute force attacks
- Batch size optimization

**Quick Start:**
```bash
cd "password brute force"
pip install -r requirements.txt
python PDF_code.py
```

### [Hashing](./Hashing/)

Hash cracker for common encryption types with Euler's method for RSA.

**Supported Types:**
- MD5
- SHA-1
- SHA-256
- bcrypt
- RSA (via Euler's Totient Theorem)

**Quick Start:**
```bash
cd Hashing
pip install -r requirements.txt

# Crack MD5 hash
python hash_cracker.py "5d41402abc4b2a76b9719d911017c592" --type md5

# Learn RSA cracking
python euler.py
```

## Common Features

- **Batching** - Multiple attempts per operation (reduces I/O overhead)
- **Multithreading** - Parallel password testing on all CPU cores
- **Dictionary Attack** - Test common passwords first
- **Brute Force** - Systematic character-by-character generation
- **Progress Tracking** - Shows attempts and current guess on interrupt

## Installation

Each project has its own `requirements.txt`. Install separately:

```bash
# PDF Password Brute Force
cd "password brute force"
pip install -r requirements.txt

# Hash Cracker
cd ../Hashing
pip install -r requirements.txt
```

## Performance Comparison

### PDF Cracking
- **Old Method**: Open PDF from disk for each password → Very slow
- **Optimized**: Load PDF once into memory → 10-100x faster

### Hash Cracking
- **Dictionary Attack**: ~1000s hashes/second
- **Brute Force**: ~100-1000s attempts/second (depends on hash type)
- **Multithreading**: 4-8x speedup on 4-8 core systems

## Files Overview

```
file code brakers/
├── password brute force/
│   ├── PDF_code.py           # Main PDF cracker
│   ├── passwordGenerator.py  # Password generation
│   ├── passwords.txt         # Log of found passwords
│   ├── requirements.txt
│   └── README.md
├── Hashing/
│   ├── hash_cracker.py       # Main hash cracker
│   ├── euler.py              # RSA key factorization
│   ├── requirements.txt
│   ├── cracked_hashes.txt    # Log of found hashes
│   └── README.md
└── README.md                 # This file
```

## Ethical and Legal Notice

### ✅ Legal Uses
- Testing your own passwords/hashes
- Educational/learning purposes
- Authorized penetration testing
- Security audits (with permission)

### ❌ Illegal Uses
- Cracking passwords/hashes you don't own
- Unauthorized access to systems
- Criminal activity

**Use these tools responsibly and only on systems you have permission to test.**

## Advanced Topics

### Euler's Method for RSA

The `Hashing/euler.py` file implements:
- **Fermat's Factorization** - Factor RSA modulus into primes
- **Euler's Totient** - Calculate φ(n) from prime factors
- **RSA Decryption** - Decrypt messages with broken keys

See `Hashing/README.md` and `euler.py` comments for detailed explanation.

### Password Generation

The `passwordGenerator.py` module:
- Generates passwords systematically
- Supports custom character sets
- Efficient iteration without storing entire space in memory

### Optimization Techniques

**Why batching matters:**
1. **Disk I/O** - Reading file 10,000 times is slow; batch testing reduces this
2. **Context Switching** - Many small tasks = many thread wakeups; larger batches = fewer wakeups
3. **Memory** - In-memory operations are orders of magnitude faster than disk

## Troubleshooting

### PDF Cracker
- **Slow**: See [Performance Tips](./password%20brute%20force/README.md#performance-tips)
- **OOM Error**: Reduce batch size or use single-thread mode
- **No Password**: Try longer length or check if using modern AES encryption

### Hash Cracker
- **Slow**: Use dictionary attack first, or reduce brute force length
- **bcrypt slow**: This is intentional (security feature)
- **Not Found**: Password may be outside length range

## Contributing

Improvements welcome! Consider:
- GPU acceleration for hash cracking
- CUDA/OpenCL for parallel password generation
- Rainbow table integration
- Dictionary optimization (trie data structure)

## License

Educational purposes. Use responsibly and legally.
