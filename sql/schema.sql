CREATE TABLE IF NOT EXISTS clean_sales (
    Store INTEGER,
    Dept INTEGER,
    Date DATE,
    Weekly_Sales DOUBLE PRECISION,
    IsHoliday BOOLEAN,

    Type VARCHAR(5),
    Size INTEGER,
    City TEXT,

    Temperature DOUBLE PRECISION,
    Fuel_Price DOUBLE PRECISION,

    MarkDown1 DOUBLE PRECISION,
    MarkDown2 DOUBLE PRECISION,
    MarkDown3 DOUBLE PRECISION,
    MarkDown4 DOUBLE PRECISION,
    MarkDown5 DOUBLE PRECISION,

    CPI DOUBLE PRECISION,
    Unemployment DOUBLE PRECISION
);

-- `CREATE TABLE IF NOT EXISTS` does not add columns to a table created by an
-- older version of this schema. PostgreSQL safely skips this migration when
-- the column already exists.
ALTER TABLE clean_sales ADD COLUMN IF NOT EXISTS City TEXT;
