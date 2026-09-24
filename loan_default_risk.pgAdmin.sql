-- =====================================================================
-- Loan Default Risk Analysis - Star Schema
-- Database: loan_default_risk
-- =====================================================================

DROP TABLE IF EXISTS fact_loans;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_purpose;
DROP TABLE IF EXISTS dim_borrower_segment;

-- ---------------------------------------------------------------------
-- dim_date: one row per unique loan issue date
-- ---------------------------------------------------------------------
CREATE TABLE dim_date (
    date_id       SERIAL PRIMARY KEY,
    full_date     DATE NOT NULL UNIQUE,
    year          INT NOT NULL,
    quarter       INT NOT NULL,
    month         INT NOT NULL,
    month_name    VARCHAR(15) NOT NULL
);

-- ---------------------------------------------------------------------
-- dim_purpose: one row per loan purpose category
-- ---------------------------------------------------------------------
CREATE TABLE dim_purpose (
    purpose_id    SERIAL PRIMARY KEY,
    purpose       VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE dim_borrower_segment (
    segment_id            SERIAL PRIMARY KEY,
    sub_grade             VARCHAR(5) NOT NULL,
    home_ownership        VARCHAR(20) NOT NULL,
    verification_status   VARCHAR(30) NOT NULL,
    application_type      VARCHAR(20) NOT NULL,
    income_bucket         VARCHAR(15) NOT NULL,
    dti_bucket             VARCHAR(15) NOT NULL,
    emp_length_bucket      VARCHAR(15) NOT NULL,
    UNIQUE (sub_grade, home_ownership, verification_status, application_type,
            income_bucket, dti_bucket, emp_length_bucket)
);

-- ---------------------------------------------------------------------
-- fact_loans: one row per loan
-- ---------------------------------------------------------------------
CREATE TABLE fact_loans (
    loan_id               SERIAL PRIMARY KEY,
    date_id               INT NOT NULL REFERENCES dim_date(date_id),
    purpose_id            INT NOT NULL REFERENCES dim_purpose(purpose_id),
    segment_id            INT NOT NULL REFERENCES dim_borrower_segment(segment_id),
    loan_amnt             NUMERIC(10, 2) NOT NULL,
    term                  INT NOT NULL,
    int_rate              NUMERIC(5, 2) NOT NULL,
    installment           NUMERIC(10, 2) NOT NULL,
    annual_inc            NUMERIC(12, 2) NOT NULL,
    dti                   NUMERIC(6, 2) NOT NULL,
    open_acc              INT NOT NULL,
    pub_rec               INT NOT NULL,
    revol_bal             NUMERIC(12, 2) NOT NULL,
    revol_util            NUMERIC(6, 2) NOT NULL,
    total_acc             INT NOT NULL,
    mort_acc              INT NOT NULL,
    pub_rec_bankruptcies  INT NOT NULL,
    credit_history_years  NUMERIC(5, 1) NOT NULL,
    loan_to_income        NUMERIC(8, 3) NOT NULL,
    emp_length_years      NUMERIC(4, 1) NOT NULL,
    default_flag          SMALLINT NOT NULL CHECK (default_flag IN (0, 1))
);

-- ---------------------------------------------------------------------
-- Indexes for common Power BI / analysis query patterns
-- ---------------------------------------------------------------------
CREATE INDEX idx_fact_loans_date_id     ON fact_loans(date_id);
CREATE INDEX idx_fact_loans_purpose_id  ON fact_loans(purpose_id);
CREATE INDEX idx_fact_loans_segment_id  ON fact_loans(segment_id);
CREATE INDEX idx_fact_loans_default     ON fact_loans(default_flag);

SELECT indexname FROM pg_indexes WHERE tablename = 'fact_loans';
