CREATE TABLE IF NOT EXISTS clean_sales (
    Store INTEGER,
    Dept INTEGER,
    Date DATE,
    Weekly_Sales DOUBLE PRECISION,
    IsHoliday BOOLEAN,

    Type VARCHAR(5),
    Size INTEGER,

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

-- Add this field after table creation so both new tables and tables created by
-- older versions of the schema contain it exactly once.
ALTER TABLE clean_sales ADD COLUMN IF NOT EXISTS City TEXT;
