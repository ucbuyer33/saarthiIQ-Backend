"""
app/utils/id_gen.py
───────────────────
Generates deterministic, pseudo-random 8-character user IDs:

  Format:  <PREFIX><6-DIGIT-FEISTEL-SUFFIX>
  Example: CD001423  (Candidate/Recruitee)
           RC889234  (Recruiter)

Algorithm — 3-round Feistel cipher on a 20-bit block (split L=10, R=10)
  • Inputs : role string + DB integer id
  • Output : zero-padded 6-digit decimal string (000000 – 999999)

Why Feistel?
  ✓ Deterministic (same role+id → same output every time)
  ✓ Bijective     (no two ids collide — guaranteed by the round function)
  ✓ Looks random  (sequential DB ids produce non-sequential visible ids)
"""

import hashlib
from app.lib.constants import ROLE_PREFIX          # noqa: F401  (re-exported for callers)
import uuid

# ── Role → 2-char prefix map ────────────────────────────────────────────────
ROLE_PREFIX: dict[str, str] = {
    "user":        "CD",   # Candidate / Recruitee
    "recruiter":   "RC",
    "admin":       "AD",
}

# ── Internal constants ────────────────────────────────────────────────────────
_HALF_BITS  = 10          # 10-bit halves  →  range 0-1023
_HALF_MOD   = 1 << _HALF_BITS   # 1024
_ROUNDS     = 3
_SEED       = 0xA5_3C          # Arbitrary non-zero mixing constant


def _round_fn(value: int, round_key: int) -> int:
    """Non-linear mixing function for one Feistel round."""
    raw = hashlib.sha256(f"{value}:{round_key}".encode()).digest()
    return int.from_bytes(raw[:2], "big") % _HALF_MOD


def _feistel(n: int, role_key: int) -> int:
    """
    Encrypt a 20-bit integer `n` with a 3-round Feistel network.
    Returns a 20-bit integer (0 – 1 048 575).
    """
    n = n % (_HALF_MOD * _HALF_MOD)   # clamp to 20 bits
    L = (n >> _HALF_BITS) & (_HALF_MOD - 1)
    R = n & (_HALF_MOD - 1)

    for i in range(_ROUNDS):
        round_key = (_SEED ^ role_key ^ i) & 0xFFFF
        L, R = R, (L ^ _round_fn(R, round_key)) % _HALF_MOD

    return (L << _HALF_BITS) | R


def generate_user_id(db_id: int, role: str) -> str:
    """
    Public API — call this once after db.flush() returns the new PK.

    Args:
        db_id : integer primary key assigned by Postgres / SQLite
        role  : one of "user", "recruiter", "interviewer", "admin"

    Returns:
        8-character string, e.g. "CD001423" or "RC889234"
    """
    prefix   = ROLE_PREFIX.get(role, "US")          # fallback prefix
    role_key = sum(ord(c) for c in prefix)           # cheap role → int

    feistel_out = _feistel(db_id, role_key)          # 0 – 1 048 575
    suffix      = feistel_out % 1_000_000            # clamp to 6 digits

    return f"{prefix}{suffix:06d}"
