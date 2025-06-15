#!/usr/bin/env python3
"""
create_datalake.py – bootstrap a local DuckLake catalog for the
“Diabetes Hospital Readmission” dataset.

Usage
-----
python create_datalake.py --base-dir /path/to/project/root

Dependencies
------------
pip install duckdb>=0.10.0
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from string import Template

import duckdb

###############################################################################
# Unmodified SQL template (verbatim from your working script)
###############################################################################

_SQL_TEMPLATE = Template(
    r"""
--------------------------------------------------------------------
-- 0) extensions & catalog
--------------------------------------------------------------------
INSTALL ducklake;
INSTALL sqlite;
LOAD ducklake;

ATTACH 'ducklake:sqlite:$metadata_path' AS ducklake
       (DATA_PATH '$data_path');
USE ducklake;

--------------------------------------------------------------------
-- 1) diabetes.patient_records
--------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS diabetes;

CREATE TABLE IF NOT EXISTS diabetes.patient_records  AS
SELECT *
FROM read_csv(
    '$diabetic_csv',
    delim   = ',',
    header  = true,
    nullstr = '?',        -- convert '?' → NULL
    columns = {
        -- identifiers
        'encounter_id':             'BIGINT',
        'patient_nbr':              'BIGINT',

        -- demographics
        'race':                     'VARCHAR',
        'gender':                   'VARCHAR',
        'age':                      'VARCHAR',
        'weight':                   'VARCHAR',

        -- admission & discharge meta-data
        'admission_type_id':        'INTEGER',
        'discharge_disposition_id': 'INTEGER',
        'admission_source_id':      'INTEGER',
        'time_in_hospital':         'INTEGER',

        -- payer / speciality
        'payer_code':               'VARCHAR',
        'medical_specialty':        'VARCHAR',

        -- counts & utilisation
        'num_lab_procedures':       'INTEGER',
        'num_procedures':           'INTEGER',
        'num_medications':          'INTEGER',
        'number_outpatient':        'INTEGER',
        'number_emergency':         'INTEGER',
        'number_inpatient':         'INTEGER',

        -- diagnoses
        'diag_1':                   'VARCHAR',
        'diag_2':                   'VARCHAR',
        'diag_3':                   'VARCHAR',
        'number_diagnoses':         'INTEGER',

        -- lab results
        'max_glu_serum':            'VARCHAR',
        'A1Cresult':                'VARCHAR',

        -- medications (single agents)
        'metformin':                'VARCHAR',
        'repaglinide':              'VARCHAR',
        'nateglinide':              'VARCHAR',
        'chlorpropamide':           'VARCHAR',
        'glimepiride':              'VARCHAR',
        'acetohexamide':            'VARCHAR',
        'glipizide':                'VARCHAR',
        'glyburide':                'VARCHAR',
        'tolbutamide':              'VARCHAR',
        'pioglitazone':             'VARCHAR',
        'rosiglitazone':            'VARCHAR',
        'acarbose':                 'VARCHAR',
        'miglitol':                 'VARCHAR',
        'troglitazone':             'VARCHAR',
        'tolazamide':               'VARCHAR',
        'examide':                  'VARCHAR',
        'citoglipton':              'VARCHAR',
        'insulin':                  'VARCHAR',

        -- combination therapies
        'glyburide-metformin':      'VARCHAR',
        'glipizide-metformin':      'VARCHAR',
        'glimepiride-pioglitazone': 'VARCHAR',
        'metformin-rosiglitazone':  'VARCHAR',
        'metformin-pioglitazone':   'VARCHAR',

        -- other flags
        'change':                   'VARCHAR',
        'diabetesMed':              'VARCHAR',

        -- target
        'readmitted':               'VARCHAR'
    }
);

--------------------------------------------------------------------
-- 2) diabetes.mappings
--------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diabetes.mappings AS
WITH labeled AS (
    SELECT
        row_number() OVER ()             AS ln,
        split_part(line, ',', 1)         AS col1,
        split_part(line, ',', 2)         AS col2
    FROM read_csv(
        '$ids_csv',
        delim   = '\n',
        header  = false,
        columns = {'line':'VARCHAR'}
    )
), with_header AS (
    SELECT
        ln,
        col1,
        col2,
        CASE
            WHEN col1 IN (
                 'admission_type_id',
                 'discharge_disposition_id',
                 'admission_source_id')
            THEN col1
        END                               AS header_flag
    FROM labeled
), filled AS (
    SELECT
        last_value(header_flag IGNORE NULLS)
            OVER (ORDER BY ln ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                                            AS mapping_name,
        col1,
        col2
    FROM with_header
), tidy AS (
    SELECT
        mapping_name,
        CAST(col1 AS INTEGER)             AS id,
        CAST(col2 AS VARCHAR)             AS description
    FROM filled
      WHERE regexp_matches(col1, '^[0-9]+$$')   -- numeric IDs only
)
SELECT * FROM tidy;

--------------------------------------------------------------------
-- 3) idc_9.diagnosis
--------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS idc_9;

CREATE TABLE IF NOT EXISTS idc_9.diagnosis AS
WITH raw_string AS (
    SELECT *
    FROM read_csv(
        '$icd_txt',
        header   = false,
        delim    = '',
        encoding = 'latin-1',
        columns  = {'line':'VARCHAR'}
    )
)
SELECT
    TRIM(SUBSTR(line, 0, 6))    AS diagnosis_id,
    TRIM(SUBSTR(line, 6, 1000)) AS diagnosis_name
FROM raw_string;
"""
)

###############################################################################
# Helpers
###############################################################################

def build_sql(base: Path) -> str:
    """Fill the template with absolute POSIX paths."""
    lake = base / "lakehouse"
    return _SQL_TEMPLATE.substitute(
        metadata_path=(lake / "metadata.sqlite").as_posix(),
        data_path=(lake / "ducklake").as_posix(),
        diabetic_csv=(lake / "diabetes/unzipped/diabetic_data.csv").as_posix(),
        ids_csv=(lake / "diabetes/unzipped/IDS_mapping.csv").as_posix(),
        icd_txt=(lake / "icd_9/unzipped/CMS32_DESC_LONG_DX.txt").as_posix(),
    )


def ensure_dirs(base: Path) -> None:
    """Make sure lakehouse/ducklake exists."""
    (base / "lakehouse/ducklake").mkdir(parents=True, exist_ok=True)


###############################################################################
# Main
###############################################################################

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a DuckLake datalake")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Project root containing the 'lakehouse' folder (default: CWD)",
    )
    base = parser.parse_args().base_dir.resolve()

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s  %(message)s",
                        stream=sys.stderr)

    logging.info("🏗  Preparing directories under %s", base)
    ensure_dirs(base)

    logging.info("🔌 Connecting to in-memory DuckDB …")
    with duckdb.connect(":memory:") as con:
        logging.info("🚀 Executing bootstrap SQL …")
        con.execute(build_sql(base))

    logging.info(
        "✅ Datalake initialised!\n"
        "   ├─ Catalog : %s\n"
        "   └─ Data    : %s",
        base / "lakehouse/metadata.sqlite",
        base / "lakehouse/ducklake",
    )


if __name__ == "__main__":
    main()
