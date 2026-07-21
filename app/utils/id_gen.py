"""
app/utils/id_gen.py
─────────────────
Generates deterministic, pseudo-random 8-character user IDs:

  Format:  RC<6-DIGIT-FEISTEL-SUFFIX>
  Example: RC889234  (Recruiter)

Algorithm — 3-round Feistel cipher on a 20-bit block (split L=10, R=10)
  • Inputs : DB integer id
  • Output : zero-padded 6-digit decimal string (000000 – 999999)

Why Feistel?
  ✓ Deterministic (same id → same output every time)
  ✓ Bijective     (no two ids collide — guaranteed by the round function)
  ✓ Looks random  (sequential DB ids produce non-sequential visible ids)

Note: this app is single-role (recruiter only), so the previous role→prefix
mapping has been removed. Every user is a recruiter.
"""

import hashlib

PREFIX = "RC"

_HALF_BITS  = 10          # 10-bit halves  →  range 0-1023
_HALF_MOD   = 1 << _HALF_BITS   # 1024
_ROUNDS     = 3
_SEED       = 0xA5_3C          # Arbitrary non-zero mixing constant
_ROLE_KEY   = sum(ord(c) for c in PREFIX)


def _round_fn(value: int, round_key: int) -> int:
    """Non-linear mixing function for one Feistel round."""
    raw = hashlib.sha256(f"{value}:{round_key}".encode()).digest()
    return int.from_bytes(raw[:2], "big") % _HALF_MOD


def _feistel(n: int) -> int:
    """
    Encrypt a 20-bit integer `n` with a 3-round Feistel network.
    Returns a 20-bit integer (0 – 1 048 575).
    """
    n = n % (_HALF_MOD * _HALF_MOD)   # clamp to 20 bits
    L = (n >> _HALF_BITS) & (_HALF_MOD - 1)
    R = n & (_HALF_MOD - 1)

    for i in range(_ROUNDS):
        round_key = (_SEED ^ _ROLE_KEY ^ i) & 0xFFFF
        L, R = R, (L ^ _round_fn(R, round_key)) % _HALF_MOD

    return (L << _HALF_BITS) | R


def generate_user_id(db_id: int) -> str:
    """
    Public API — call this once after db.flush() returns the new PK.

    Args:
        db_id : integer primary key assigned by Postgres / SQLite

    Returns:
        8-character string, e.g. "RC889234"
    """
    feistel_out = _feistel(db_id)          # 0 – 1 048 575
    suffix      = feistel_out % 1_000_000  # clamp to 6 digits

    return f"{PREFIX}{suffix:06d}"
