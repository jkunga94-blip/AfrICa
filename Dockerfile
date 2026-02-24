FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY generate_africa_quiz_dataset.py ./

RUN pip install --no-cache-dir -r requirements.txt

# Default values (can be overridden with env/CLI args)
ENV TARGET_SIZE=10000
ENV SEED=42

CMD ["sh", "-c", "python generate_africa_quiz_dataset.py --target-size ${TARGET_SIZE} --seed ${SEED}"]

