import argparse
import json
import random
import sqlite3
from copy import deepcopy
from itertools import cycle
from pathlib import Path


DIFFICULTY_POINTS = {
    "Easy": 10,
    "Medium": 20,
    "Hard": 40,
}

XP_MULTIPLIER = {
    "Easy": 1,
    "Medium": 1.5,
    "Hard": 2,
}

STREAK_BONUS = {
    "Easy": 2,
    "Medium": 5,
    "Hard": 10,
}

FLAG_CODES = {
    "Kenya": "ke",
    "Nigeria": "ng",
    "Ghana": "gh",
    "Egypt": "eg",
    "Tanzania": "tz",
    "South Africa": "za",
    "Ethiopia": "et",
    "Botswana": "bw",
    "Algeria": "dz",
    "Zimbabwe": "zw",
    "Zambia": "zm",
    "Madagascar": "mg",
    "Chad": "td",
    "Uganda": "ug",
    "Mali": "ml",
}


def load_base_questions(path: Path) -> list[dict]:
    """
    Load base questions from CSV or Excel.

    Expected columns:
      - category
      - subcategory
      - question
      - correct
      - difficulty
      - option1, option2, option3, option4 (any non-empty option columns will be used)
    """
    import pandas as pd

    if not path.exists():
        raise FileNotFoundError(f"Base questions file not found: {path}")

    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    required_cols = {"category", "subcategory", "question", "correct", "difficulty"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {', '.join(sorted(missing))}")

    option_cols = [c for c in df.columns if c.startswith("option")]
    if not option_cols:
        raise ValueError("No option columns found. Expected columns like 'option1', 'option2', ...")

    base: list[dict] = []
    for _, row in df.iterrows():
        options = [str(row[c]) for c in option_cols if pd.notna(row[c]) and str(row[c]).strip() != ""]
        base.append(
            {
                "category": row["category"],
                "subcategory": row["subcategory"],
                "question": row["question"],
                "correct": row["correct"],
                "options": options,
                "difficulty": row["difficulty"],
            }
        )

    return base


def enrich_question(q: dict, qid: int) -> dict:
    difficulty = q["difficulty"]

    country_flag = None
    if q["correct"] in FLAG_CODES:
        country_flag = f"https://flagcdn.com/w320/{FLAG_CODES[q['correct']]}.png"

    return {
        "id": qid,
        "category": q["category"],
        "subcategory": q["subcategory"],
        "question": q["question"],
        "options": q["options"],
        "correct_answer": q["correct"],
        "difficulty": difficulty,
        "points": DIFFICULTY_POINTS[difficulty],
        "xp_multiplier": XP_MULTIPLIER[difficulty],
        "streak_bonus": STREAK_BONUS[difficulty],
        "tags": [
            q["category"],
            q["subcategory"],
            difficulty,
            "Africa",
            "Multiple Choice",
        ],
        "flag_image": country_flag,
    }


def generate_large_dataset(base: list[dict], target_size: int, rng: random.Random) -> list[dict]:
    expanded: list[dict] = []
    id_counter = 1
    generator = cycle(base)

    while len(expanded) < target_size:
        template = deepcopy(next(generator))
        rng.shuffle(template["options"])
        expanded.append(enrich_question(template, id_counter))
        id_counter += 1

    return expanded


def export_json(questions: list[dict], out_path: Path) -> None:
    out_path.write_text(json.dumps(questions, indent=4, ensure_ascii=False), encoding="utf-8")


def export_sqlite(questions: list[dict], out_path: Path) -> None:
    conn = sqlite3.connect(str(out_path))
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY,
                category TEXT,
                subcategory TEXT,
                question TEXT,
                options TEXT,
                correct_answer TEXT,
                difficulty TEXT,
                points INTEGER,
                xp_multiplier REAL,
                streak_bonus INTEGER,
                tags TEXT,
                flag_image TEXT
            )
            """
        )

        rows = [
            (
                q["id"],
                q["category"],
                q["subcategory"],
                q["question"],
                json.dumps(q["options"], ensure_ascii=False),
                q["correct_answer"],
                q["difficulty"],
                q["points"],
                q["xp_multiplier"],
                q["streak_bonus"],
                json.dumps(q["tags"], ensure_ascii=False),
                q["flag_image"],
            )
            for q in questions
        ]

        cursor.executemany(
            """
            INSERT OR REPLACE INTO quiz_questions (
                id, category, subcategory, question, options,
                correct_answer, difficulty, points,
                xp_multiplier, streak_bonus, tags, flag_image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def export_excel(questions: list[dict], out_path: Path) -> None:
    import pandas as pd

    df = pd.DataFrame(questions)
    df.to_excel(out_path, index=False)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Africa quiz dataset (JSON, SQLite, Excel).")
    p.add_argument("--target-size", type=int, default=10000, help="Number of questions to generate.")
    p.add_argument("--seed", type=int, default=None, help="Random seed for deterministic shuffling.")
    p.add_argument(
        "--base-file",
        type=str,
        default=None,
        help="CSV/Excel file with base questions. If omitted, falls back to a small built-in set.",
    )
    p.add_argument("--json", dest="json_path", default="africa_quiz_10000.json", help="JSON output path.")
    p.add_argument("--sqlite", dest="sqlite_path", default="africa_quiz.db", help="SQLite output path.")
    p.add_argument("--excel", dest="excel_path", default="Africa_Quiz_10k_MC.xlsx", help="Excel output path.")
    p.add_argument(
        "--no-excel",
        action="store_true",
        help="Skip Excel export (avoids requiring pandas/openpyxl).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)

    if args.base_file:
        base_questions = load_base_questions(Path(args.base_file))
    else:
        base_questions = [
            {
                "category": "Geography & Landmarks",
                "subcategory": "Countries",
                "question": "What is the largest country in Africa by land area?",
                "correct": "Algeria",
                "options": ["Algeria", "Nigeria", "Sudan", "DR Congo"],
                "difficulty": "Easy",
            },
            {
                "category": "Capitals",
                "subcategory": "Capitals",
                "question": "What is the capital of Kenya?",
                "correct": "Nairobi",
                "options": ["Nairobi", "Mombasa", "Kampala", "Dodoma"],
                "difficulty": "Easy",
            },
            {
                "category": "History & Civilizations",
                "subcategory": "Independence",
                "question": "Who became South Africa’s first Black president?",
                "correct": "Nelson Mandela",
                "options": ["Nelson Mandela", "Thabo Mbeki", "Jacob Zuma", "Desmond Tutu"],
                "difficulty": "Easy",
            },
            {
                "category": "Food & Cuisine",
                "subcategory": "West Africa",
                "question": "What West African rice dish is widely debated between Ghana and Nigeria?",
                "correct": "Jollof Rice",
                "options": ["Jollof Rice", "Fufu", "Injera", "Tagine"],
                "difficulty": "Easy",
            },
        ]

    questions = generate_large_dataset(base_questions, args.target_size, rng)

    export_json(questions, Path(args.json_path))
    export_sqlite(questions, Path(args.sqlite_path))
    if not args.no_excel:
        export_excel(questions, Path(args.excel_path))

    print(f"Generated {len(questions)} questions.")
    print(f"JSON: {args.json_path}")
    print(f"SQLite: {args.sqlite_path}")
    if not args.no_excel:
        print(f"Excel: {args.excel_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

