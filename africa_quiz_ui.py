from pathlib import Path
import random

import streamlit as st

from generate_africa_quiz_dataset import (
    load_base_questions,
    generate_large_dataset,
    export_json,
    export_sqlite,
    export_excel,
)


DEFAULT_BASE_QUESTIONS = [
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


def configure_page() -> None:
    st.set_page_config(
        page_title="Africa Quiz Dataset Generator",
        layout="wide",
    )
    st.markdown(
        """
        <style>
        .main {
            background: radial-gradient(circle at top left, #14342b 0, #0a0c10 45%, #000000 100%);
            color: #f5f5f5;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .africa-card {
            background: linear-gradient(135deg, rgba(20, 52, 43, 0.95), rgba(43, 24, 7, 0.98));
            border-radius: 1rem;
            padding: 1.5rem 1.75rem;
            border: 1px solid rgba(255, 215, 0, 0.35);
            box-shadow: 0 18px 38px rgba(0, 0, 0, 0.6);
        }
        .africa-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.18rem 0.7rem;
            border-radius: 999px;
            font-size: 0.8rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.45);
            color: #ffd700;
        }
        .africa-title {
            font-size: 1.9rem;
            font-weight: 700;
            margin-top: 0.6rem;
            margin-bottom: 0.2rem;
        }
        .africa-subtitle {
            font-size: 0.98rem;
            color: #e0e0e0;
            max-width: 38rem;
        }
        .metric-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #c9c9c9;
        }
        .metric-value {
            font-size: 1.4rem;
            font-weight: 600;
            color: #ffd700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    with st.container():
        st.markdown('<div class="africa-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="africa-badge">
                Africa Quiz Studio
            </div>
            <div class="africa-title">
                Generate Rich Africa-Themed Quiz Datasets
            </div>
            <div class="africa-subtitle">
                Upload your base questions or start with a curated sample.
                Instantly create JSON, SQLite, and Excel datasets with gamification
                metadata for your learning apps or trivia games.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-label">Formats</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">JSON · SQLite · Excel</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-label">Gamification</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">Points · XP · Streaks</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-label">Difficulty Tiers</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">Easy · Medium · Hard</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


def load_base_from_ui(uploaded_file, base_path_text: str):
    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix or ".xlsx"
        temp_path = Path("uploaded_base_questions" + suffix)
        temp_path.write_bytes(uploaded_file.getbuffer())
        return load_base_questions(temp_path), str(temp_path)

    if base_path_text.strip():
        path = Path(base_path_text.strip())
        return load_base_questions(path), str(path)

    return DEFAULT_BASE_QUESTIONS, "built-in sample"


def main() -> None:
    configure_page()
    render_header()

    st.write("")

    with st.sidebar:
        st.subheader("Configuration")
        target_size = st.slider("Number of questions to generate", min_value=1000, max_value=50000, value=10000, step=1000)
        seed = st.number_input("Random seed (optional)", value=42, step=1)

        st.markdown("---")
        st.subheader("Base questions")
        uploaded = st.file_uploader(
            "Upload CSV or Excel with base questions",
            type=["csv", "xlsx", "xls"],
            help="Columns: category, subcategory, question, correct, difficulty, option1..optionN",
        )
        base_path_text = st.text_input(
            "Or use a path on disk",
            value="",
            placeholder="e.g. data/africa_base_questions.xlsx",
        )

        st.markdown("---")
        st.subheader("Output filenames")
        json_name = st.text_input("JSON file name", value="africa_quiz_10000.json")
        sqlite_name = st.text_input("SQLite DB name", value="africa_quiz.db")
        excel_name = st.text_input("Excel file name", value="Africa_Quiz_10k_MC.xlsx")
        include_excel = st.checkbox("Generate Excel file", value=True)

        generate_clicked = st.button("Generate dataset", use_container_width=True)

    col_left, col_right = st.columns((2.2, 1.3))

    with col_left:
        st.subheader("Generation status")
        status_placeholder = st.empty()
        preview_placeholder = st.empty()

    with col_right:
        st.subheader("Output summary")
        files_placeholder = st.empty()

    if generate_clicked:
        try:
            status_placeholder.info("Preparing base questions...")
            base_questions, source_label = load_base_from_ui(uploaded, base_path_text)

            rng = random.Random(seed)
            status_placeholder.info(f"Generating {target_size} questions from {source_label}...")

            questions = generate_large_dataset(base_questions, target_size, rng)

            json_path = Path(json_name)
            sqlite_path = Path(sqlite_name)
            excel_path = Path(excel_name)

            export_json(questions, json_path)
            export_sqlite(questions, sqlite_path)
            if include_excel:
                export_excel(questions, excel_path)

            status_placeholder.success(f"Generated {len(questions)} questions successfully.")

            if questions:
                import pandas as pd

                preview_df = pd.DataFrame(questions[:20])
                preview_placeholder.dataframe(
                    preview_df[["id", "category", "subcategory", "difficulty", "question", "correct_answer"]],
                    use_container_width=True,
                )

            files_md = f"""
            **Files created in current folder:**

            - `{json_path.name}`
            - `{sqlite_path.name}`
            """
            if include_excel:
                files_md += f"\n- `{excel_path.name}`"

            files_placeholder.markdown(files_md)
        except Exception as exc:  # noqa: BLE001
            status_placeholder.error(f"Error while generating dataset: {exc}")


if __name__ == "__main__":
    main()

