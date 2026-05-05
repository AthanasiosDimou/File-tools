# Hash Cracker

Brute force and dictionary attack tool for cracking common password hashes.

## Supported Hash Types

- **MD5** - Fast but cryptographically broken (use for educational purposes)
- **SHA-1** - Deprecated but still found in legacy systems
- **SHA-256** - Modern standard
- **bcrypt** - Modern, slow hash (makes brute force difficult)

## Features

- **Dictionary Attack** - Load common passwords from a file
- **Brute Force** - Generate passwords and test systematically
- **Batching** - Test multiple passwords per disk/network operation
- **Multithreading** - Utilize multiple CPU cores for speed
- **Euler's Method** - RSA key factorization for educational purposes

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Hash Cracking

```bash
# Crack MD5 hash
python hash_cracker.py "5d41402abc4b2a76b9719d911017c592" --type md5

# Crack SHA-256 hash
python hash_cracker.py "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" --type sha256

# Crack bcrypt hash
python hash_cracker.py "$2b$12$..." --type bcrypt
```

### With Dictionary Attack

```bash
python hash_cracker.py "5d41402abc4b2a76b9719d911017c592" \
  --type md5 \
  --dict common_passwords.txt
```

### Brute Force with Custom Length

```bash
python hash_cracker.py "5d41402abc4b2a76b9719d911017c592" \
  --type md5 \
  --min-len 1 \
  --max-len 8
```

### Single-threaded Mode

```bash
python hash_cracker.py "5d41402abc4b2a76b9719d911017c592" \
  --type md5 \
  --single-thread
```

## Performance Tips

1. **Use Dictionary Attack First** - Fastest method if the password is common
2. **Keep Brute Force Length Short** - Exponential complexity (95^n possibilities)
3. **Use Multithreading** - Enabled by default, utilize all CPU cores
4. **bcrypt is Slow** - Design feature to prevent brute force; may take very long

## Files

- `hash_cracker.py` - Main hash cracking tool
- `euler.py` - Euler's Totient Theorem implementation for RSA (educational)
- `requirements.txt` - Dependencies

## Example: Generate Test Hashes

```python
import hashlib

# MD5 of "test"
print(hashlib.md5(b"test").hexdigest())
# Output: 098f6bcd4621d373cade4e832627b4f6

# SHA-256 of "test"
print(hashlib.sha256(b"test").hexdigest())
# Output: 9f86d081884c7d6d9ffd60bb75380e50c1e8de6d9d20d6d5ca1fc20dd5b31f42
```

## Euler's Method

The `euler.py` file contains implementation of Euler's Totient Theorem for RSA:

- **Fermat Factorization** - Break RSA keys with close prime factors
- **Euler's Totient** - Calculate φ(n) from prime factors
- **RSA Cracking** - Decrypt RSA-encrypted messages

See `euler.py` for detailed comments and examples.

## Ethical Notice

This tool is for:
- ✅ Testing your own password hashes
- ✅ Educational purposes
- ✅ Authorized security audits

This tool is NOT for:
- ❌ Cracking passwords you don't have permission to crack
- ❌ Unauthorized access to systems
- ❌ Illegal activities

Use responsibly and legally.
