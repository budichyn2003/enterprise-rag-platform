import re


_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE = re.compile(r"(?<!\w)(?:\+?62|0)8\d{7,12}(?!\w)")
_NIK = re.compile(r"(?<!\d)\d{16}(?!\d)")
_CARD = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_PASSWORD = re.compile(
    r"(?i)\b(?:password|kata\s+sandi|pin)\s*[:=]\s*\S+"
)
_INJECTION = re.compile(
    r"(?i)\b(?:ignore|forget|abaikan|lupakan)\b.{0,60}\b(?:instruction|instruksi|aturan|prompt|system|sistem)\b"
    r"|\b(?:reveal|show|print|tampilkan|bocorkan)\b.{0,50}\b(?:system prompt|prompt sistem|secret|rahasia)\b"
    r"|\b(?:developer message|pesan developer)\b"
)
_RESTRICTED_TOPIC = re.compile(
    r"(?i)\b(?:diagnosis|diagnose|pengobatan|obat resep|medical advice|nasihat medis|"
    r"nasihat hukum|legal advice|lawyer|pengacara|investasi|investment advice|"
    r"insider trading|tax advice|nasihat pajak)\b"
)
_TOXIC_OUTPUT = re.compile(r"(?i)\b(?:kill yourself|bunuh diri|hate speech)\b")


def _is_luhn_valid(value: str) -> bool:
    digits = [int(character) for character in value if character.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def redact_pii(text: str) -> str:
    redacted = _PASSWORD.sub("[REDACTED]", text)
    redacted = _EMAIL.sub("[REDACTED_EMAIL]", redacted)
    redacted = _PHONE.sub("[REDACTED_PHONE]", redacted)
    redacted = _NIK.sub("[REDACTED_ID]", redacted)
    redacted = _CARD.sub(
        lambda match: "[REDACTED_CARD]" if _is_luhn_valid(match.group()) else match.group(),
        redacted,
    )
    return redacted


def detect_prompt_injection(text: str) -> bool:
    return bool(_INJECTION.search(text))


def detect_restricted_topic(text: str) -> bool:
    return bool(_RESTRICTED_TOPIC.search(text))


def moderate_output(text: str) -> str:
    if _TOXIC_OUTPUT.search(text):
        return "Maaf, saya tidak dapat memberikan jawaban tersebut. Saya akan menghubungkan Anda dengan tim support."
    return redact_pii(text)
