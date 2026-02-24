# Africa quiz dataset generator

Generates an Africa-themed multiple-choice quiz dataset and exports it to:

- JSON (`.json`)
- SQLite (`.db`)
- Excel (`.xlsx`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Default (10,000 questions, built-in base set):

```bash
python generate_africa_quiz_dataset.py
```

Custom size + deterministic shuffle:

```bash
python generate_africa_quiz_dataset.py --target-size 25000 --seed 123
```

Use your own base questions from CSV:

```bash
python generate_africa_quiz_dataset.py \
  --base-file my_base_questions.csv \
  --target-size 10000 \
  --seed 42
```

Or from Excel:

```bash
python generate_africa_quiz_dataset.py \
  --base-file my_base_questions.xlsx \
  --target-size 10000
```

Expected columns in the base file:

- `category`
- `subcategory`
- `question`
- `correct`
- `difficulty`
- `option1`, `option2`, `option3`, `option4` (any number of `option*` columns is fine)

## Install as a CLI tool (optional)

From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

You can then run:

```bash
africa-quiz-generate --target-size 10000 --seed 42
```

## Run with Docker (optional)

Build the image:

```bash
docker build -t africa-quiz-generator .
```

Generate a dataset (10,000 questions by default):

```bash
docker run --rm -v "$PWD:/app" africa-quiz-generator
```

Override target size / seed:

```bash
docker run --rm -v "$PWD:/app" \
  -e TARGET_SIZE=5000 \
  -e SEED=123 \
  africa-quiz-generator
```


Skip Excel export (no pandas/openpyxl needed):

```bash
python generate_africa_quiz_dataset.py --no-excel
```

