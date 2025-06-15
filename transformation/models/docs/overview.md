{% docs __overview__ %}
# 🩺 Power BI Patient Dashboard: Diabetes Monitoring & Insights

Welcome to the **Power BI Patient Dashboard** project powered by `DuckLake`, `dbt`, `DuckDB`, `Python` and `Power BI`!  
This project is designed to process, transform, and surface valuable insights into diabetes patient care using modern data practices.

---

## 🚀 Project Overview

This dbt project transforms raw healthcare data into curated, analysis-ready datasets that power a comprehensive **Power BI dashboard** for monitoring patient admissions, diagnoses, and discharge patterns with a focus on **diabetes**.

Using dbt's modular and testable approach, the project spans from raw ingestion to analytical marts, enabling reliable data exports and automated reporting.

---

## 🧱 Data Architecture & Lineage

### Source Systems:
- **`diabetes`**: [Diabetes 130-US Hospitals for Years 1999-2008 dataset](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008)

- **`idc_9`**: [ICD-9-CM Diagnosis and Procedure Codes](https://www.cms.gov/medicare/coding-billing/icd-10-codes/icd-9-cm-diagnosis-procedure-codes-abbreviated-and-full-code-titles)

### Exposures:
- 📊 **Power BI Patient Dashboard** — primary consumer of the marts.
- 📤 `export_diabetes_stats` — exports `.csv` file to external storage... simulates reverse etl/data provision to external partner

📌 *See the lineage graph (lower right button) for a complete view of how each model contributes to the final analytics layer.*

---

## 🔎 Use Cases

- Analyze **admission sources** and **types** by diabetes patients.
- Track **discharge outcomes** for chronic conditions.
- Drill into ICD-9-coded **diagnosis trends**.
- Export and share summary statistics for **public health teams** or internal stakeholders.


---

## ✅ Highlights

- 🔄 Automated lineage & testing
- 📐 Consistent dimensional model
- 🦆 Superb data catalog with **DuckLake**
- ⚡ Lightweight analytics with **DuckDB**
- 🎯 Designed for small/medium data volumes
- 🛡️ dbt's data quality tests integrated across stages

---

## 🧠 Tech Stack

- **Python** for data ingestion
- **dbt** for transformation
- **DuckLake** as the analytics engine/catalog
- **sqlite** as DuckLake's db
- **Power BI** for data visualization and storytelling

---

## 📣 Contact

For questions, feedback, or collaboration opportunities, reach out to [me](https://github.com/999999333).



{% enddocs %}