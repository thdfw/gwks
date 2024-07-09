import os
import pandas as pd
import psycopg2

"""
If a table does not exist, run this SQL command first:
CREATE TABLE realtime_LBMP (
    "Time Stamp" TIMESTAMP,
    "Name" VARCHAR(100),
    "PTID" INTEGER,
    "LBMP ($/MWHr)" NUMERIC,
    "Marginal Cost Losses ($/MWHr)" NUMERIC,
    "Marginal Cost Congestion ($/MWHr)" NUMERIC
);
"""

conn = psycopg2.connect(
    dbname = 'newyork',
    user = '',
    password = '',
    host = 'localhost',
    port = '5432'
)

cur = conn.cursor()

csv_files = sorted([file for file in os.listdir('lbmp_data') if file.endswith('.csv')])

for file in csv_files:

    file_path = os.path.join(os.getcwd(), 'lbmp_data', file)
    sql_command = f"COPY realtime_LBMP FROM '{file_path}' DELIMITER ',' CSV HEADER;"
    cur.execute(sql_command)
    print(f"Appended {file} to realtime_LBMP table")

conn.commit()
cur.close()
conn.close()