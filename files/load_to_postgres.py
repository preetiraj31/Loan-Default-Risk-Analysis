"""
Phase 3: Load cleaned loan data into PostgreSQL star schema
==============================================================
Prerequisites:
1. PostgreSQL database "loan_default_risk" created
2. sql/schema.sql already run in pgAdmin's Query Tool (creates the tables)
3. pip install sqlalchemy psycopg2-binary --break-system-packages

Run: python src/load_to_postgres.py
"""

import pandas as pd
from sqlalchemy import create_engine

# ---- Update these to match your local PostgreSQL setup ----
DB_USER = "postgres"
DB_PASSWORD = "2004"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "loan_default_risk"
# -------------------------------------------------------------

IN_PATH = "loan_cleaned.csv"


def get_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def bucket_income(income: float) -> str:
    if income < 40000:
        return "Low"
    elif income < 90000:
        return "Medium"
    else:
        return "High"


def bucket_dti(dti: float) -> str:
    if dti < 15:
        return "Low"
    elif dti < 30:
        return "Medium"
    else:
        return "High"


def bucket_emp_length(years: float) -> str:
    if years < 2:
        return "0-1 yrs"
    elif years < 6:
        return "2-5 yrs"
    else:
        return "6+ yrs"


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DataFrame({"full_date": pd.to_datetime(df["issue_d"]).dt.date.unique()})
    dates["full_date"] = pd.to_datetime(dates["full_date"])
    dates["year"] = dates["full_date"].dt.year
    dates["quarter"] = dates["full_date"].dt.quarter
    dates["month"] = dates["full_date"].dt.month
    dates["month_name"] = dates["full_date"].dt.month_name()
    dates = dates.sort_values("full_date").reset_index(drop=True)
    dates.insert(0, "date_id", range(1, len(dates) + 1))
    return dates


def build_dim_purpose(df: pd.DataFrame) -> pd.DataFrame:
    purposes = pd.DataFrame({"purpose": sorted(df["purpose"].unique())})
    purposes.insert(0, "purpose_id", range(1, len(purposes) + 1))
    return purposes


def build_dim_borrower_segment(df: pd.DataFrame) -> pd.DataFrame:
    seg_cols = [
        "sub_grade", "home_ownership", "verification_status", "application_type",
        "income_bucket", "dti_bucket", "emp_length_bucket",
    ]
    segments = df[seg_cols].drop_duplicates().reset_index(drop=True)
    segments.insert(0, "segment_id", range(1, len(segments) + 1))
    return segments


def main():
    print("Loading cleaned data...")
    df = pd.read_csv(IN_PATH, parse_dates=["issue_d", "earliest_cr_line"])

    # Derive bucket columns used by dim_borrower_segment
    df["income_bucket"] = df["annual_inc"].apply(bucket_income)
    df["dti_bucket"] = df["dti"].apply(bucket_dti)
    df["emp_length_bucket"] = df["emp_length_years"].apply(bucket_emp_length)

    print("Building dimension tables...")
    dim_date = build_dim_date(df)
    dim_purpose = build_dim_purpose(df)
    dim_borrower_segment = build_dim_borrower_segment(df)

    engine = get_engine()

    print("Loading dimension tables into PostgreSQL...")
    dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
    dim_purpose.to_sql("dim_purpose", engine, if_exists="append", index=False)
    dim_borrower_segment.to_sql("dim_borrower_segment", engine, if_exists="append", index=False)
    print(f"  dim_date: {len(dim_date)} rows")
    print(f"  dim_purpose: {len(dim_purpose)} rows")
    print(f"  dim_borrower_segment: {len(dim_borrower_segment)} rows")

    # Build fact_loans by joining df to the surrogate keys of each dimension
    print("Building fact_loans...")
    df["full_date"] = pd.to_datetime(df["issue_d"].dt.date)
    fact = df.merge(dim_date[["date_id", "full_date"]], on="full_date", how="left")
    fact = fact.merge(dim_purpose, on="purpose", how="left")
    seg_cols = [
        "sub_grade", "home_ownership", "verification_status", "application_type",
        "income_bucket", "dti_bucket", "emp_length_bucket",
    ]
    fact = fact.merge(dim_borrower_segment, on=seg_cols, how="left")

    fact_cols = [
        "date_id", "purpose_id", "segment_id", "loan_amnt", "term", "int_rate",
        "installment", "annual_inc", "dti", "open_acc", "pub_rec", "revol_bal",
        "revol_util", "total_acc", "mort_acc", "pub_rec_bankruptcies",
        "credit_history_years", "loan_to_income", "emp_length_years", "default_flag",
    ]
    fact_loans = fact[fact_cols]

    print("Loading fact_loans into PostgreSQL (this may take a minute)...")
    fact_loans.to_sql("fact_loans", engine, if_exists="append", index=False, chunksize=5000)
    print(f"  fact_loans: {len(fact_loans)} rows")

    print("\nDone. Run a quick check in pgAdmin:")
    print("  SELECT COUNT(*) FROM fact_loans;")


if __name__ == "__main__":
    main()
