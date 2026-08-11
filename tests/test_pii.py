from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_nested_passport_and_address() -> None:
    from app.logging_config import scrub_event

    record = scrub_event(
        None,
        "info",
        {
            "event": "profile_received",
            "payload": {
                "identity": {"passport": "B1234567"},
                "notes": ["Địa chỉ: 12 Nguyễn Trãi, Hà Nội"],
            },
        },
    )

    rendered = str(record)
    assert "B1234567" not in rendered
    assert "12 Nguyễn Trãi" not in rendered
    assert "REDACTED_PASSPORT_VN" in rendered
    assert "REDACTED_ADDRESS_VN" in rendered
