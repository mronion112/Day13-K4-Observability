# PII Scrubber Handoff

Import `scrub_pii` from `app.pii` and run it on log strings before JSON is
rendered or written. The individual `mask_email`, `mask_phone`, and
`mask_credit_card` functions are available when only one rule is needed.

## Supported patterns

- Email addresses with a conventional domain suffix. The first local-part
  character and full domain remain visible, for example `a***@gmail.com`.
- Vietnamese phone numbers written as ten local digits beginning with `0`, or
  in `+84` form. Spaces, dots, and hyphens are accepted; the final three digits
  remain visible.
- Sixteen-digit payment card numbers, contiguous or grouped with spaces or
  hyphens. Only the final four digits remain visible.
- Multiple supported values in free text or JSON-stringified log lines.
- `None`, empty strings, and non-matching text without raising an exception.

The module also masks contiguous twelve-digit Vietnamese citizen IDs (CCCD),
leaving only the final four digits visible.

## Current limitations

- Obfuscated emails, emails without a domain suffix, extensions, and
  international phone formats other than Vietnam are not detected.
- Phone numbers with parentheses and card numbers with mixed separators are
  not detected.
- Card matching is format-based and does not perform a Luhn validity check.
- The scrubber accepts strings; callers must serialize structured payloads or
  apply it recursively before passing non-string fields.

Use `data/sample_pii_logs.jsonl` for a quick integration check. The fixture is
synthetic and its `expected_secrets` arrays list values that must disappear
after scrubbing.
