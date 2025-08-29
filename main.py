from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any, Dict

app = FastAPI(title="BFHL API")


class DataInput(BaseModel):
    data: List[str]


FULL_NAME = "john_doe"
DATE_DDMMYYYY = "17091999"
USER_ID = f"{FULL_NAME}_{DATE_DDMMYYYY}"
EMAIL = "john@xyz.com"
ROLL_NUMBER = "ABCD123"


@app.post("/bfhl")
def process_bfhl(payload: DataInput) -> Dict[str, Any]:
    try:
        odd_numbers: List[str] = []
        even_numbers: List[str] = []
        alphabets: List[str] = []
        special_characters: List[str] = []
        original_letters: List[str] = []
        total_sum = 0

        for item in payload.data:
            numeric_candidate = item.strip()
            if numeric_candidate and all(c in "+-0123456789" for c in numeric_candidate) and numeric_candidate.lstrip("+-").isdigit():
                try:
                    num_value = int(numeric_candidate)
                    total_sum += num_value
                    target_list = even_numbers if abs(num_value) % 2 == 0 else odd_numbers
                    target_list.append(numeric_candidate)
                    continue
                except Exception:
                    pass

            if len(item) == 1 and item.isalpha():
                original_letters.append(item)
                alphabets.append(item.upper())
                continue

            if len(item) == 1 and not item.isalnum():
                special_characters.append(item)
                continue

            if item.isalpha():
                for ch in item:
                    original_letters.append(ch)
                    alphabets.append(ch.upper())
                continue

            for ch in item:
                if ch.isalpha():
                    original_letters.append(ch)
                    alphabets.append(ch.upper())
                elif ch.isdigit():
                    continue
                elif not ch.isspace():
                    special_characters.append(ch)

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
def root():
    return {"message": "FastAPI is live! Use POST /bfhl for the challenge."}
