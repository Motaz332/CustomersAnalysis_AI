# Customers Analysis AI

Professional-grade solution for Customer Lifetime Value (CLV) prediction and behavioral segmentation based on transactional data. This repository contains the data processing pipeline, feature engineering, model development (including pre-trained models), reproducible notebooks, and an interactive Streamlit dashboard for exploration and inference.

---

Badges
- Build / CI: [status]
- Python: 3.7+
- Notebooks: Jupyter

(Replace the placeholders above with actual badge images if you use a CI service.)

---

Table of contents
- Project summary
- Dataset & key statistics
- Business objectives
- System architecture
- Data processing & feature engineering
- Modeling & evaluation
- Usage: notebooks, CLI, and Streamlit app
- Deployment recommendations
- Visual assets (screenshots & figures)
- Operational & maintenance guidelines
- Privacy, limitations, and assumptions
- License
- Changelog

---

Project summary
This project transforms raw ecommerce transactions into actionable customer intelligence:
- Compute RFM metrics and extended features
- Segment customers and produce operational tiers
- Predict Customer Lifetime Value using a production-ready DNN
- Provide an interactive dashboard for exploration, slices, and exports

Repository composition
- Primary language: Jupyter Notebooks (analysis & modeling)
- Supporting code: Python scripts and Streamlit app
This repo is designed for reproducible research and for hand-off to engineering teams.

---

Dataset & key statistics
Source: "Online Retail" transactional dataset (Excel) — sample period: Dec 2010 — Dec 2011

Key numbers (as used during development):
- Raw transactions: 541,909
- Unique customers: 4,372
- Cleaned transactions: 524,878 (after removing cancellations, duplicates, and invalid entries)
- Geographic coverage: 38 countries

Note: Exact counts depend on the dataset file included in /data or the project root.

---

Business objectives
- Provide accurate CLV estimates to prioritize acquisition and retention spend
- Expose RFM-driven segments to marketing and product teams
- Enable data-driven campaign targeting and revenue forecasting
- Offer a lightweight inference API and an interactive dashboard for business users

Success criteria
- High rank-correlation between predicted and realized CLV
- Stable model generalization across holdout periods (quarterly validation)
- Operational dashboards used by non-technical stakeholders

---

System architecture (high level)

Components:
- Data ingestion: Excel/CSV ingestion + validation
- Preprocessing: cleaning, dedup, filtering cancellations
- Feature engineering: RFM + derived features
- Training pipeline: notebook + reproducible model training
- Model persistence: Keras HDF5 / SavedModel
- Inference: Streamlit dashboard + simple API for batch predictions

---

Data processing & feature engineering

Primary steps
1. Ingest raw transactions (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)
2. Remove cancelled orders (negative quantities) and invalid invoices
3. Drop exact duplicates and reconcile transaction-level anomalies
4. Impute or filter missing CustomerID according to business policy (imputation only when traceable; otherwise exclude)
5. Convert timestamps, normalize currencies/prices if multi-currency present

Core features created
- RFM: Recency (days since last purchase), Frequency (unique transactions), Monetary (total spend)
- Customer tenure: days/months since first purchase
- Average Order Value (AOV): Monetary / Frequency
- Frequency per month: Frequency / tenure_months
- Product diversity: unique StockCode count per customer
- Category flags / ordinal encoding: product category and country-region mapping

Target (CLV)
- CLV is computed as a short-term projected lifetime value using observed behavior and a decay factor on recency. Implementation and projection window are configurable in notebooks.

Quality & validation
- Schema validation and basic anomaly detection are implemented in notebooks
- Unit checks on derived features (e.g., frequency >= 1 for non-filtered customers)
- Data snapshots and distribution checks saved to /assets/figures for reporting

---

Modeling & evaluation

Primary model: Deep Neural Network (DNN) for regression (CLV)
- Input features: engineered numeric features (9–15 features depending on configuration)
- Typical architecture:
  - Input layer (n features)
  - Dense 128 (ReLU) → Dropout 0.2
  - Dense 64 (ReLU) → Dropout 0.2
  - Dense 32 (ReLU)
  - Output Dense 1 (linear)
- Loss: Mean Squared Error (MSE)
- Optimizer: Adam (lr=1e-3)
- Early stopping with validation patience (5–10 epochs)
- Regularization: dropout and optional L2

Baseline & comparative models:
- Linear Regression (OLS)
- Ridge / Lasso
- RandomForestRegressor
- Gradient Boosting (XGBoost / LightGBM)

Evaluation metrics (recommended)
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R²
- Spearman rank correlation (to measure ranking fidelity)
- Calibration plots and residual analysis

Example (how to load the model)
```python
from tensorflow.keras.models import load_model
import pandas as pd

model = load_model('models/model_DNN.h5')
X = pd.read_csv('data/sampled_features.csv')  # prepared & scaled
preds = model.predict(X)
```

Feature scaling & leakage prevention
- Use MinMaxScaler or StandardScaler fitted on training data only
- Persist scaler objects to models/scalers/ and reuse them during inference

Model validation strategy
- Temporal split (train on earlier months, test on later months) recommended to simulate production
- 5-fold cross validation for stability checks on non-temporal experiments

---

Model performance (example summary from development runs)
- Train R²: ~0.91
- Test R²: ~0.89
- MAE: usage-dependent (report values from your training run)
- Rank correlation with actual CLV: > 0.85

Include precise metrics from your final run in the "Performance" subsection.

---

Customer segmentation & actionable tiers

Example segmentation (business-driven)
- VIP — top 20% by predicted CLV
- Premium — next 30%
- Core — middle 35%
- Low-value — bottom 15%

Each tier should have tailored marketing actions:
- VIP: personalized offers, retention specialists
- Premium: loyalty campaigns and cross-sell
- Core: automated engagement
- Low-value: cost-efficient acquisition vs. retention analysis

Store segmentation outputs as CSV for downstream campaign systems:
```
customer_id, predicted_clv, segment_label
```

---

Interactive dashboard (Streamlit)
- app.py provides an interactive overview: KPI cards, RFM distribution, segment explorer, CLV prediction UI
- Requirements: streamlit, pandas, numpy, tensorflow
- Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
---

Usage examples

Notebook-driven reproducibility
- Open notebooks in `notebooks/` in the listed order to replicate data preparation, modeling, and reporting
- Parameterize the notebooks (date ranges, projection window, model hyperparams) for reproducible experiments

Programmatic inference (batch)
```python
import pandas as pd
from tensorflow.keras.models import load_model
from joblib import load

scaler = load('models/scaler.joblib')
model = load_model('models/model_DNN.h5')

df = pd.read_csv('data/customers_features_to_score.csv')
X = scaler.transform(df[feature_columns])
df['predicted_clv'] = model.predict(X).flatten()
df.to_csv('outputs/customer_predictions.csv', index=False)
```

Single-customer inference (example)
```python
# Use the same preprocessing pipeline used during training
single_customer = pd.DataFrame([{
    'recency': 45, 'frequency': 6, 'monetary': 340.5, 'aov': 56.75,
    'product_diversity': 4, 'tenure_months': 12, ...
}])
X = scaler.transform(single_customer)
predicted_clv = model.predict(X)[0][0]
print(f"Predicted CLV: ${predicted_clv:,.2f}")
```

---

Deployment recommendations
- Export model as SavedModel or HDF5; include scaler and encoder artifacts
- Wrap inference in a lightweight Flask/FastAPI service or deploy as a serverless function for low-volume use
- For higher throughput, containerize (Docker) and serve behind an autoscaling endpoint (Kubernetes / EKS / GKE)
- Add a small feature-validation microservice to reject malformed inputs

Security and governance
- Do not include raw PII in outputs. Store customer identifiers using secure keys.
- Use role-based access to model predictions and dashboards.
- Anonymize or mask sensitive values in exported CSVs.

---

Operational & maintenance guidelines

Retraining cadence
- Quarterly retraining recommended or when population metrics shift >5%
- Maintain training logs, model versions, and validation dashboards

Monitoring
- Record prediction distributions and monitor drift vs. recent realized CLV
- Alerts for data pipeline failures and sudden metric shifts

Versioning
- Keep models and scalers alongside dataset snapshot identifiers
- Tag releases with semantic versioning and a CHANGELOG entry

---

Privacy, limitations, and assumptions

Privacy
- The repository and artifacts should not contain raw personal data for public sharing.
- Use hashed customer identifiers in public artifacts.

Limitations
- Dataset is historically constrained (one-year sample); seasonal effects and macro changes may be underrepresented
- Geographic concentration (majority of transactions from a single market) may bias predictions for international expansion

Assumptions
- CLV projection window and decay factor are configurable; adjust to your business lifetime assumptions

---

Appendix: images & reporting
- Include generated figures from notebooks into /assets/figures for reports
- Recommended figures:
  - RFM heatmap
  - CLV predicted vs actual scatter
  - Segment composition by revenue share
  - Dashboard screenshots for stakeholder reports

---

License
This repository is provided under the MIT license. See LICENSE file for details.

---

Changelog
- 2025-12-01 — v1.0 — Professional documentation, notebooks, and initial models

---

Notes
- The notebooks are the primary source of truth; they contain code, rationale, and intermediate outputs. Use them for traceability and to regenerate figures.
- This file intentionally does not include personal contact information or general contribution requests.
