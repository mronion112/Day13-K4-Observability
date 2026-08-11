from __future__ import annotations

import hashlib
import re
from typing import Final

EMAIL_RE: Final[re.Pattern[str]] = re.compile(r"\b([A-Za-z0-9])([A-Za-z0-9._%+-]*)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
PHONE_VN_RE: Final[re.Pattern[str]] = re.compile(r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)")
CREDIT_CARD_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b")
CCCD_RE: Final[re.Pattern[str]] = re.compile(r"\b\d{12}\b")


def _coerce_text(text: str | None) -> str:
    return "" if text is None else text


def mask_email(text: str | None) -> str:
    safe_text = _coerce_text(text)

    def repl(match: re.Match[str]) -> str:
        first_char, _, domain = match.groups()
        return f"{first_char}***@{domain}"

    return EMAIL_RE.sub(repl, safe_text)


def _mask_phone_number(raw_phone: str) -> str:
    digits_only = re.sub(r"\D", "", raw_phone)
    if len(digits_only) < 4:
        return "[REDACTED_PHONE]"

    visible_suffix = digits_only[-3:] if len(digits_only) >= 10 else digits_only[-2:]
    masked_middle = "*" * max(0, len(digits_only) - len(visible_suffix))
    return f"[REDACTED_PHONE:{masked_middle}{visible_suffix}]"


def mask_phone(text: str | None) -> str:
    safe_text = _coerce_text(text)
    return PHONE_VN_RE.sub(lambda match: _mask_phone_number(match.group(0)), safe_text)


def _mask_grouped_digits(raw_value: str, label: str) -> str:
    digits_only = re.sub(r"\D", "", raw_value)
    if len(digits_only) < 4:
        return f"[REDACTED_{label}]"

    visible_suffix = digits_only[-4:]
    hidden_length = len(digits_only) - 4
    return f"[REDACTED_{label}:{'*' * hidden_length}{visible_suffix}]"


def mask_credit_card(text: str | None) -> str:
    safe_text = _coerce_text(text)
    return CREDIT_CARD_RE.sub(
        lambda match: _mask_grouped_digits(match.group(0), "CARD"),
        safe_text,
    )


def mask_cccd(text: str | None) -> str:
    safe_text = _coerce_text(text)
    return CCCD_RE.sub(
        lambda match: _mask_grouped_digits(match.group(0), "CCCD"),
        safe_text,
    )


def scrub_pii(text: str | None) -> str:
    safe_text = _coerce_text(text)
    safe_text = mask_email(safe_text)
    safe_text = mask_phone(safe_text)
    safe_text = mask_credit_card(safe_text)
    safe_text = mask_cccd(safe_text)
    return safe_text


def scrub_text(text: str | None) -> str:
    return scrub_pii(text)


def summarize_text(text: str | None, max_len: int = 80) -> str:
    safe = scrub_pii(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
