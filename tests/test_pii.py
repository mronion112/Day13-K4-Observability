import json
from pathlib import Path

from app.pii import (
    hash_user_id,
    mask_credit_card,
    mask_email,
    mask_phone,
    scrub_pii,
    scrub_text,
    summarize_text,
)

SAMPLE_PII_LOGS = Path(__file__).parents[1] / "data" / "sample_pii_logs.jsonl"


def test_mask_email_keeps_first_character_and_domain() -> None:
    out = mask_email("Email me at student@vinuni.edu.vn")
    assert "student@vinuni.edu.vn" not in out
    assert "s***@vinuni.edu.vn" in out


def test_mask_phone_supports_common_vietnamese_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = mask_phone(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "[REDACTED_PHONE:" in out
        assert out.endswith("567]")


def test_mask_credit_card_keeps_last_four_digits() -> None:
    out = mask_credit_card("Card: 4111 1111 1111 1234")
    assert "4111 1111 1111 1234" not in out
    assert "[REDACTED_CARD:************1234]" in out


def test_scrub_pii_masks_multiple_types_in_one_line() -> None:
    raw = (
        'payload={"email":"student@vinuni.edu.vn","phone":"090 123 4567",'
        '"card":"4111-1111-1111-1234"}'
    )

    out = scrub_pii(raw)

    assert "student@vinuni.edu.vn" not in out
    assert "090 123 4567" not in out
    assert "4111-1111-1111-1234" not in out
    assert "s***@vinuni.edu.vn" in out
    assert "[REDACTED_PHONE:" in out
    assert "[REDACTED_CARD:************1234]" in out


def test_scrub_text_handles_empty_and_none_safely() -> None:
    assert scrub_text("") == ""
    assert scrub_text(None) == ""


def test_scrub_text_leaves_non_matching_content_unchanged() -> None:
    raw = "No personal data here, only error_id=abc-123."
    assert scrub_text(raw) == raw


def test_invalid_or_incomplete_values_are_not_masked() -> None:
    raw = "email=user@localhost phone=090123 card=4111-1111-1111"
    assert scrub_pii(raw) == raw


def test_scrubber_handles_unusual_characters_and_embedded_values() -> None:
    raw = "[warn] user=(student+lab@vinuni.edu.vn); phone=<090-123-4567> | \u2603"

    out = scrub_pii(raw)

    assert out == "[warn] user=(s***@vinuni.edu.vn); phone=<[REDACTED_PHONE:*******567]> | \u2603"


def test_sample_jsonl_logs_can_be_scrubbed_without_pii_leaks() -> None:
    records = [json.loads(line) for line in SAMPLE_PII_LOGS.read_text().splitlines()]

    for record in records:
        raw_line = json.dumps(record, ensure_ascii=False)
        scrubbed_line = scrub_pii(raw_line)

        for sensitive_value in record["expected_secrets"]:
            assert sensitive_value not in scrubbed_line
        assert json.loads(scrubbed_line)["event"]


def test_summarize_text_scrubs_before_truncating() -> None:
    raw = (
        "Please contact student@vinuni.edu.vn or call 0901234567 for the full "
        "incident write-up and next steps."
    )

    out = summarize_text(raw, max_len=50)

    assert "student@vinuni.edu.vn" not in out
    assert "0901234567" not in out
    assert len(out) <= 53


def test_hash_user_id_is_stable_and_short() -> None:
    first = hash_user_id("student-01")
    second = hash_user_id("student-01")

    assert first == second
    assert len(first) == 12
