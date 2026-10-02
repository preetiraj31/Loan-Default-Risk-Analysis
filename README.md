# Loan-Default-Risk-Analysis

End-to-end credit risk analysis on ~395K Lending Club loans using **Python, PostgreSQL and Power BI**. The project cleans the raw data, explores default patterns, models the data in a star schema, and presents the findings in an interactive dashboard.

<img width="1332" height="817" alt="Screenshot 2026-10-02 124802" src="https://github.com/user-attachments/assets/4a79c6f4-748d-447d-afd2-03d5f862fb51" />


## Business Problem

Lenders lose money when borrowers default. This project answers:

- Which loan grades, purposes and borrower segments carry the highest default risk?
- How has default behaviour changed over time?
- Does the interest rate charged reflect the actual risk?

## Dataset

- **Source:** Lending Club Loan Data (Kaggle)
- **Raw size:** 396,030 rows x 27 columns (loans issued Apr 2008 to Sep 2016)
- **Target:** `loan_status` (Fully Paid / Charged Off), converted to a 0/1 default flag
- **Overall default rate:** 19.6%

## Tools and Skills

| Stage | Tools |
|---|---|
| Data cleaning and EDA | Python (pandas, matplotlib, seaborn), Jupyter |
| Data modeling | PostgreSQL, pgAdmin (star schema) |
| ETL | Python (psycopg2) |
| Visualization | Power BI |

## Project Pipeline

```
Raw CSV -> Python cleaning + EDA -> PostgreSQL star schema -> Power BI dashboard -> Insights
```

### 1. Data Cleaning (`data_cleaning.py`)
- Dropped high-cardinality / unused columns (`emp_title`, `title`, `address`, `grade`)
- Imputed missing `mort_acc` using the median within `total_acc` groups
- Dropped 811 rows with missing `revol_util` / `pub_rec_bankruptcies`
- Converted `term`, `emp_length` and date columns to usable formats
- Engineered features: `credit_history_years`, `loan_to_income`, `emp_length_unknown`
- Removed one row with `annual_inc = 0` that produced an infinite `loan_to_income`
- **Final dataset:** 395,218 rows x 26 columns, zero nulls

### 2. Exploratory Data Analysis (`eda.py`, notebook)
Default rate analysed by sub-grade, loan purpose, home ownership, year, and correlation with numeric features.

### 3. SQL Star Schema (`schema.sql`, `load_to_postgres.py`)
- `fact_loans` (395,218 rows)
- `dim_date`
- `dim_purpose`
- `dim_borrower_segment` (bucketed income, DTI, employment length)

### 4. Power BI Dashboard
- **KPIs:** Total Loans (395K), Avg Interest Rate (13.6%), Default Rate (19.6%), Total Loan Amount ($6bn)
- **Charts:** Default rate by sub-grade, loan purpose, income bucket, home ownership and year, plus loan status distribution
- **Interactivity:** Slicers for Year, Home Ownership and Term, with a clear-all-slicers button

## Key Insights

1. **Risk rises steadily with sub-grade.** Default rate climbs from about 3% at A1 to about 51% at G3, so the grading system separates risk well.
2. **Small business loans are the riskiest purpose** (about 29% default). Wedding (12%) and car (13.5%) loans are the safest.
3. **Default rate spiked in 2014-2015** (23-25%) compared with about 13-16% in 2009-2013.
4. **Renters default more than homeowners.** RENT 22.7%, OWN 20.7%, MORTGAGE 17.0%.
5. **Lower income buckets default more**, with default rate falling from Low to High income.
6. **Interest rate tracks risk.** `int_rate` is the numeric feature most correlated with default (0.25), followed by `loan_to_income` (0.13).

## Recommendations

- Apply stricter screening or higher pricing for small business loans and lower sub-grades (E to G).
- Monitor loan quality closely during periods of rapid origination growth, as seen in 2014-2015.
- Use home ownership and income segments as supporting signals in risk assessment.



## How to Run

1. Install dependencies: `pip install pandas numpy matplotlib seaborn psycopg2-binary`
2. Run `python data_cleaning.py` to create `loan_cleaned.csv`
3. Create a PostgreSQL database `loan_default_risk` and run `schema.sql`
4. Run `python load_to_postgres.py` to load the data
5. Open `Loan_Default_Risk_Dashboard.pbix` in Power BI Desktop and refresh the connection

## Limitations

- The dataset only contains loans with a final status of Fully Paid or Charged Off, so ongoing loans are excluded.
- 2016 is a partial year (data ends Sep 2016), so it was excluded from the yearly trend.
- This project is descriptive (EDA + SQL + dashboard) and does not include a predictive model.

## Author

**Preeti Raj**
B.Tech CSE student | Aspiring Data Analyst
