📊 Customer Analytics Dashboard

A professional RFM-based customer analytics dashboard with predictive Customer Lifetime Value (CLV) models, built with Python, Streamlit, and TensorFlow. Designed to help businesses analyze customer behavior, segment their audience, simulate campaign ROI, and make data-driven decisions.

Table of Contents

Project Overview

Features

Technologies & Libraries

Installation

Usage

Project Structure

Screenshots

Future Improvements

Author

Project Overview

This dashboard allows businesses to:

Calculate RFM metrics (Recency, Frequency, Monetary) and score customers.

Segment customers into categories like Champions, Loyal, Potential, and At-Risk.

Explore interactive visualizations for customer behavior and segment statistics.

Simulate marketing campaign ROI based on selected segments.

Predict Customer Lifetime Value (CLV) using DNN and Encoder models with confidence scores.

Export targeted customer lists to CSV or Excel.

The project demonstrates end-to-end data analytics workflow: from raw data preprocessing to machine learning predictions and visualization.

Features
🔹 Analysis Mode

KPI cards: total customers, total revenue, average order value, average recency.

Customer lookup by CustomerID with full RFM metrics and segment information.

Segment explorer with filtering by RFM metrics.

Interactive charts:

Customers per segment (bar chart)

Frequency vs. Monetary (scatter chart with log scale)

Trends over time for Recency, Frequency, and Monetary.

Filtered customer view with export options (CSV & Excel).

🔹 Model Performance Mode

Predict Customer Lifetime Value (CLV) using two pre-trained models: DNN and Encoder.

Confidence scores for predictions.

Visual comparison of training vs. testing errors.

Interactive sidebar input for features: Quantity, UnitPrice, Frequency, Monetary, Recency, Country, ProductCategory, ProductDiversity.

Technologies & Libraries

Python 3.x

Streamlit – Interactive web dashboard

Pandas & NumPy – Data manipulation

Altair – Interactive charts

TensorFlow / Keras – CLV prediction models

Excel & CSV – Export functionality

Installation

Clone this repository:

git clone <your-repo-url>
cd customer-analytics-dashboard


Create a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows


Install required packages:

pip install -r requirements.txt


Place the dataset Online Retail.xlsx in the project folder.

Ensure the pre-trained models model_DNN.h5 and enc_model_DNN.h5 are in the project folder.

Usage

Run the Streamlit app:

streamlit run app.py


Use the sidebar to switch between Analysis and Model Performance modes.

Enter CustomerID to explore individual customer metrics.

Use filters and segmentation options to analyze specific groups.

Run CLV predictions in Model Performance mode.

Export targeted customer lists for campaigns.

Project Structure
customer-analytics-dashboard/
│
├─ app.py                     # Main Streamlit dashboard
├─ Online Retail.xlsx          # Sample dataset
├─ model_DNN.h5               # Pre-trained DNN model
├─ enc_model_DNN.h5           # Pre-trained Encoder model
├─ requirements.txt           # Python dependencies
└─ README.md                  # Project documentation

Screenshots

(Add your screenshots here to make the project visually appealing)

KPI Cards & Customer Lookup

Segment Explorer & Interactive Charts

Model Performance & CLV Predictions

Future Improvements

Add user authentication and multi-user support.

Deploy as a cloud web application using Heroku or AWS.

Integrate more advanced ML models (e.g., XGBoost, CatBoost) for CLV prediction.

Add real-time data streaming for continuous analytics.

Support dynamic product and country categories from dataset instead of hard-coded values.

Author

Moataz Essam – Computer Science Student | AI & Data Analytics Enthusiast

GitHub: [Your GitHub URL]

LinkedIn: [Your LinkedIn URL]
