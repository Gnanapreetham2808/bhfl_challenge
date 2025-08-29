from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any, Dict

app = FastAPI(title="BFHL API")


class DataInput(BaseModel):
    data: List[str]


FULL_NAME = "john_doe"  # must stay lowercase per requirement
DATE_DDMMYYYY = "17091999"  # example DOB
USER_ID = f"{FULL_NAME}_{DATE_DDMMYYYY}"
EMAIL = "john@xyz.com"
ROLL_NUMBER = "ABCD123"


@app.post("/bfhl")
def process_bfhl(payload: DataInput) -> Dict[str, Any]:
    """Process the incoming data list per spec and classify elements.

    Numbers: kept as original strings (including +, - or leading zeros) and parity determined on integer value.
    Alphabets: returned uppercased; concat_string is letters with original case reversed.
    Sum: arithmetic sum of all integer-detected values returned as string.
    """
    try:
        odd_numbers: List[str] = []
        even_numbers: List[str] = []
        alphabets: List[str] = []  # Always uppercase per requirement
        special_characters: List[str] = []
        original_letters: List[str] = []  # Track original letter forms for concat_string logic
        total_sum = 0

        for item in payload.data:
            # Numeric detection (integers only)
            numeric_candidate = item.strip()
            if numeric_candidate and all(c in "+-0123456789" for c in numeric_candidate) and numeric_candidate.lstrip("+-").isdigit():
                # Convert for arithmetic but preserve original string form (without surrounding spaces)
                try:
                    num_value = int(numeric_candidate)
                    total_sum += num_value
                    target_list = even_numbers if abs(num_value) % 2 == 0 else odd_numbers
                    # Preserve original representation (e.g., "+8", "001", "-5")
                    target_list.append(numeric_candidate)
                    continue
                except Exception:
                    # If conversion somehow fails, fall through to other classification
                    pass

            # Alphabet (single character a-z/A-Z)
            if len(item) == 1 and item.isalpha():
                original_letters.append(item)
                alphabets.append(item.upper())
                continue

            # Special character (single non-alphanumeric printable symbol)
            if len(item) == 1 and not item.isalnum():
                special_characters.append(item)
                continue

            # Fallback classification: if multi-char alphabetic string treat as sequence of letters
            if item.isalpha():
                for ch in item:
                    original_letters.append(ch)
                    alphabets.append(ch.upper())
                continue

            # Else, extract individual special characters
            for ch in item:
                if ch.isalpha():
                    original_letters.append(ch)
                    alphabets.append(ch.upper())
                elif ch.isdigit():
                    # digits encountered inside a mixed string don't count toward sum per assumption
                    continue
                elif not ch.isspace():
                    special_characters.append(ch)

        # concat_string: concatenate letters with case reversed from their original input appearance.
        # If original was lower -> becomes upper; original upper -> becomes lower.
        concat_chars = []
        for ch in original_letters:
            if ch.islower():
                concat_chars.append(ch.upper())
            else:
                concat_chars.append(ch.lower())
        concat_string = ''.join(concat_chars)

        response = {
            "is_success": True,
            "user_id": USER_ID,
            "email": EMAIL,
            "roll_number": ROLL_NUMBER,
            "odd_numbers": odd_numbers,
            "even_numbers": even_numbers,
            "alphabets": alphabets,
            "special_characters": special_characters,
            "sum": str(total_sum),
            "concat_string": concat_string,
        }
        return response
    except Exception as e:
        # Graceful error response
        return {
            "is_success": False,
            "user_id": USER_ID,
            "email": EMAIL,
            "roll_number": ROLL_NUMBER,
            "odd_numbers": [],
            "even_numbers": [],
            "alphabets": [],
            "special_characters": [],
            "sum": "0",
            "concat_string": "",
            "error": str(e)
        }


@app.get("/")
def health():
    return {"status": "ok"}
