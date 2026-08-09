"""Project entry point for the E-Commerce Order Analytics System."""

from scripts.clean_data import run_cleaning_pipeline
from scripts.data_generator import main as generate_raw_data
from scripts.load_database import load_database


def main() -> None:
    """Run raw-data generation, cleaning, SQLite loading, and database validation."""
    generate_raw_data()
    run_cleaning_pipeline()
    load_database()


if __name__ == "__main__":
    main()
