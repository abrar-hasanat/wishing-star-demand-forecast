# INTERNAL OPERATIONS MEMO: Wishing Star Demand & Supply Chain Analytics

## 1. Executive Summary
During the peak Q4 seasons of 2022 and 2023, Wishing Star experienced critical supply chain failures resulting in total stockouts of our Flagship product lines. While top-line customer acquisition grew at a healthy **12% YoY**, the failure to predict compounding seasonal demand resulted in lost revenue and degraded customer experience. 

To address this, we engineered an end-to-end predictive data pipeline. By training a time-series forecasting model (Prophet) on our historical transaction data and surfacing the insights through an **IBM Cognos Analytics** executive dashboard, we have transitioned our procurement strategy from reactive to predictive. **If this model had been live in 2023, operations would have received an automated stockout alert 3 weeks prior to inventory depletion.**

## 2. Technical Architecture & Methodology
This project demonstrates a full-stack enterprise analytics workflow, moving from raw transactional data to C-suite strategic visualization.

* **Data Engineering (Python & PostgreSQL):** * Simulated over 3.5 years of chaotic daily D2C e-commerce data (25,000+ orders).
    * Engineered a relational database schema (Orders, Items, Customers, Products, Inventory).
    * Developed a PostgreSQL pipeline to aggregate daily line-item transactions against historical inventory logs, establishing a boolean `is_stockout` daily tracker.
* **Predictive Demand Modeling (Python & Prophet):**
    * Trained a Facebook Prophet model on historical demand (2020-2022), isolating yearly and weekly seasonality.
    * Implemented an early-detection algorithm: Instead of tracking standard daily demand, the model calculates a **rolling 21-day forecast** (matching exact supplier lead times). If the 21-day rolling demand exceeds our 600-unit reorder threshold, the system triggers a critical failure flag.
* **Enterprise Business Intelligence (IBM Cognos Analytics):** * Rather than utilizing entry-level BI tools, the final data models and visual infrastructure were built in **IBM Cognos Analytics** to demonstrate true enterprise-level capability. 
    * Engineered relational conditional expressions directly within the Cognos Data Module (e.g., `NULLIF` handling for YoY growth division, hardcoded zero-inventory logical flags).
    * Leveraged Cognos' built-in NLP AI Assistant to generate McKinsey-style visualization assets.

## 3. The IBM Cognos Executive Dashboard

*(The interactive dashboard deployed to leadership for daily monitoring of supply chain health.)*
<img width="1547" height="770" alt="image" src="https://github.com/user-attachments/assets/e2797194-2b57-4d62-81bd-49a124516916" />

<img width="1561" height="760" alt="image" src="https://github.com/user-attachments/assets/86c43793-151d-4cba-912f-612b1a0c5ce3" />

<img width="1332" height="776" alt="image" src="https://github.com/user-attachments/assets/139b7732-2d56-4a6a-84c5-ab6fd59db40d" />


## 4. Strategic Findings & Recommendations
Based on the backtested predictive model and Cognos data analysis, we recommend the following immediate operational shifts:

1.  **Dynamic Reorder Thresholds:** The standard 600-unit maximum reorder quantity is mathematically insufficient for Q4. The Prophet model proves that early November velocity outpaces the 21-day supplier lead time. Q4 reorder points must be raised by 185% strictly between Oct 15 and Dec 10.
2.  **Supplier Renegotiation:** The 21-day and 14-day lead times for Flagship Products 1 and 2 are the root cause of the bottleneck. Procurement must negotiate expedited shipping SLAs (Target: <10 days) during the Q4 spike, even at a premium freight cost, as the margin loss from zero-stock days heavily outweighs expedited logistics costs.
3.  **Automated Cognos Alerting:** Integrate the Python Prophet script's `stockout_alert_flag` directly into the IBM Cognos daily refresh schedule so the Operations team receives automated email alerts when rolling demand breaches safety stock limits.

## 5. Repository Navigation
For technical review of the pipeline and model architecture, please reference the source files below:

* `generate_wishing_star_data.py`: The Python simulation engine utilizing Poisson distributions to generate 25,000+ realistic e-commerce transactions and relational tables.
* `data_pipeline.sql`: The PostgreSQL script handling daily aggregation, JOINs, and anomaly extraction.
* `demand_forecast.py`: The time-series predictive model (Prophet) and rolling lead-time logic.

---
*Built by Abrar Hasanat — Strategy, Operations & Enterprise Data Analytics.*
