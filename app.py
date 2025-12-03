import streamlit as st
import pandas as pd
import numpy as np
import io
import altair as alt

import tensorflow as tf
from tensorflow.keras import metrics
import math
st.set_page_config(page_title="Customer Analytics Dashboard", layout="wide")
#________________________________________________________________________________
#load saved models DNN and ENCODERMODEL

#dnn_model = tf.keras.models.load_model("model_DNN.h5")
#encoder_model = tf.keras.models.load_model("enc_model_DNN.h5")
@st.cache_resource
def load_models():

    m1 = tf.keras.models.load_model(
        r'model_DNN.h5',
        compile=False,
        custom_objects={'mse': metrics.MeanSquaredError()}
    )
    m2 = tf.keras.models.load_model(
        r"enc_model_DNN.h5",
        compile=False,  
        custom_objects={'mse': metrics.MeanSquaredError()}
    )
    return m1,m2
dnn_model,encoder_model = load_models()
#________________________________________________________________________________


# Page Config




st.sidebar.title("Chose Activite")
c1,c2 = st.sidebar.columns(2)

if "mode" not in st.session_state:
    st.session_state.mode = 'analysis'

with c1:
    rfm_analysis = st.button("Analysis")
with c2:
    model_prediction = st.button("Model Performance")

if rfm_analysis:
    st.session_state.mode = 'analysis'
    st.rerun()
if model_prediction:
    st.session_state.mode = 'model'
    st.rerun()



# Load Data (with error handling)
@st.cache_data
def load_data(path=r"Online Retail.xlsx"):
    try:
        df = pd.read_excel(path)
    except FileNotFoundError:
        return None
    df = df[(df['UnitPrice'] >= 0) & (df['Quantity'] >= 0)] 
    df = df[df['InvoiceNo'].astype('str').str.startswith('C') == False]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    # drop customers with missing ID
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    return df

df = load_data()


if df is None:
    st.error("Data file 'Online Retail.xlsx' not found in the app folder. Place the file next to app.py or upload it.")
    st.stop()


# RFM Calculation

def safe_qcut(series, q=5, labels=None):
    try:
        return pd.qcut(series, q, labels=labels)
    except ValueError:
        # fallback to rank-based bins
        ranks = series.rank(method="first")
        bins = pd.cut(ranks, q, labels=labels)
        return bins
def segment(row):
    if row["RFM_Score"] >= 13:
        return "Champions"
    elif row["RFM_Score"] >= 10:
        return "Loyal Customers"
    elif row["RFM_Score"] >= 7:
        return "Potential"
    else:
        return "At Risk"
    
@st.cache_data
def create_rfm(df):
    st.title("📊 Customer Analytics Dashboard")
    st.markdown("A professional RFM-based customer analytics dashboard — explore segments, run simple ROI simulations, and export targets.")
    st.markdown("_"*40)
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
        "InvoiceNo": "count",
        "TotalPrice": "sum"
    }).reset_index()

    rfm.columns = ["CustomerID", "Recency", "Frequency", "Monetary"]
    rfm["AvgOrderValue"] = rfm["Monetary"] / rfm["Frequency"]

    # RFM Scoring: robust fallback when qcut fails (e.g., many identical values)


    rfm["R_score"] = safe_qcut(rfm["Recency"], 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_score"] = safe_qcut(rfm["Frequency"], 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_score"] = safe_qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_Score"] = rfm[["R_score","F_score","M_score"]].sum(axis=1)



    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm
rfm = create_rfm(df)
if st.session_state.mode == 'analysis':
    # KPI Cards

    total_customers = rfm["CustomerID"].nunique()
    total_revenue = rfm["Monetary"].sum()
    avg_aov = rfm["AvgOrderValue"].mean()
    avg_recency = rfm["Recency"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Customers", f"{total_customers:,}")
    k2.metric("Total Revenue", f"${total_revenue:,.2f}")
    k3.metric("Avg Order Value", f"${avg_aov:,.2f}")
    k4.metric("Avg Recency (days)", f"{avg_recency:.1f}")


    # Customer Lookup (numeric safe)

    st.subheader("🔎 Customer Lookup")
    cust_input = st.number_input("Enter CustomerID:", min_value=0, step=1, format="%d")
    if cust_input:
        cust_id = int(cust_input)
        if cust_id in rfm["CustomerID"].values:
            cust_data = rfm.loc[rfm["CustomerID"] == cust_id].iloc[0]
            st.write(f"*CustomerID:* {int(cust_data['CustomerID'])}")
            st.write(f"*Recency (days):* {int(cust_data['Recency'])}")
            st.write(f"*Frequency:* {int(cust_data['Frequency'])}")
            st.write(f"*Monetary (Total Spend):* ${cust_data['Monetary']:.2f}")
            st.write(f"*Average Order Value:* ${cust_data['AvgOrderValue']:.2f}")
            st.write(f"*RFM Score:* {cust_data['RFM_Score']}")
            st.write(f"*Segment:* {cust_data['Segment']}")
        else:
            st.info("CustomerID not found in dataset.")


    # Segmentation Explorer & Visuals

    st.subheader("📊 Segmentation Explorer")
    segment_choice = st.multiselect("Select segment(s)", sorted(rfm["Segment"].unique()), default=sorted(rfm["Segment"].unique()))
    seg_data = rfm[rfm["Segment"].isin(segment_choice)]

    st.markdown("Segment summary statistics for selected segments:")
    st.dataframe(seg_data.describe().T.style.format({
        "mean": "{:.2f}", "std": "{:.2f}", "min": "{:.2f}", "25%": "{:.2f}", "50%": "{:.2f}", "75%": "{:.2f}", "max": "{:.2f}"
    }))

    # Segment counts chart
    segment_counts = rfm.groupby("Segment").size().reset_index(name="count")
    bar = alt.Chart(segment_counts).mark_bar().encode(
        x=alt.X("Segment:N", sort="-y"),
        y="count:Q",
        tooltip=["Segment","count"]
    ).properties(height=300, width=600, title="Customers per Segment")
    st.altair_chart(bar, use_container_width=True)

    # Scatter: Frequency vs Monetary (log scale for monetary)
    scatter = alt.Chart(seg_data).mark_circle(size=60).encode(
        x=alt.X("Frequency:Q"),
        y=alt.Y("Monetary:Q", scale=alt.Scale(type="log")),
        color="Segment:N",
        tooltip=["CustomerID", "Recency", "Frequency", alt.Tooltip("Monetary", format="$,.2f")]
    ).interactive().properties(title="Frequency vs Monetary (log scale)")
    st.altair_chart(scatter, use_container_width=True)


# Filters for RFM (sidebar)

    st.sidebar.header("🔍 RFM Filters")
    recency_min, recency_max = int(rfm["Recency"].min()), int(rfm["Recency"].max())
    frequency_min, frequency_max = int(rfm["Frequency"].min()), int(rfm["Frequency"].max())
    monetary_min, monetary_max = float(rfm["Monetary"].min()), float(rfm["Monetary"].max())

    recency_filter = st.sidebar.slider("Recency (days)", recency_min, recency_max, (recency_min, recency_max))
    frequency_filter = st.sidebar.slider("Frequency", frequency_min, frequency_max, (frequency_min, frequency_max))
    monetary_filter = st.sidebar.slider("Monetary", float(np.floor(monetary_min)), float(np.ceil(monetary_max)), (float(np.floor(monetary_min)), float(np.ceil(monetary_max))))

    filtered_rfm = rfm[
        (rfm["Recency"].between(*recency_filter)) &
        (rfm["Frequency"].between(*frequency_filter)) &
        (rfm["Monetary"].between(*monetary_filter))
    ]

    st.subheader("📌 Filtered Customers")
    st.dataframe(filtered_rfm.sort_values(by="Monetary", ascending=False).reset_index(drop=True).head(250))


    # Campaign ROI Simulator

    st.subheader("💰 Campaign ROI Simulator")
    with st.expander("Open simulator"):
        budget = st.number_input("Enter campaign budget ($):", min_value=0.0, value=1000.0, step=100.0, format="%.2f")
        roi_percent = st.slider("Expected ROI per customer (%)", 0, 500, 50)
        target_segment = st.selectbox("Target segment", sorted(rfm["Segment"].unique()))
        num_customers = int(rfm[rfm["Segment"] == target_segment].shape[0])
        expected_roi = num_customers * (roi_percent/100.0) * budget
        st.write(f"Target Segment: *{target_segment}* — Customers: *{num_customers:,}*")
        st.metric("Expected ROI (total)", f"${expected_roi:,.2f}")


    # Export Targeted Customers (always-available download buttons)
        st.subheader("📤 Export Targeted Customers")
    # Prepare CSV and Excel in memory
        csv_bytes = filtered_rfm.to_csv(index=False).encode("utf-8")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer) as writer:
        filtered_rfm.to_excel(writer, index=False, sheet_name="Filtered_Customers")
    excel_bytes = excel_buffer.getvalue()

    dl_col1, dl_col2 = st.columns(2)
    dl_col1.download_button("Download CSV", data=csv_bytes, file_name="filtered_customers.csv", mime="text/csv")
    dl_col2.download_button("Download Excel", data=excel_bytes, file_name="filtered_customers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


    # Quick Trends

    st.subheader("📈 Customer Behavior Trends (filtered)")
    if filtered_rfm.shape[0] > 0:
        # st.line_chart(filtered_rfm.set_index("CustomerID")[["Recency","Frequency","Monetary"]].sort_index())
        st.title("Recency")
        st.line_chart(filtered_rfm.set_index("CustomerID")[["Recency"]].sort_index())
        st.title("Frequency")
        st.line_chart(filtered_rfm.set_index("CustomerID")[["Frequency"]])
        st.title("Monetary")
        st.line_chart(filtered_rfm.set_index("CustomerID")[["Monetary"]].sort_index())
    else:
        st.info("No customers in the selected filter range to plot.")



#__________________________________________________________________
if st.session_state.mode == 'model':
    st.title("📊 Model Perofrmance Dashboard")
    st.markdown("_"*40)
    #DNN error percentage
    #train-> 4.221045026115981
    #test-> 4.226760458354771

    # encoder error percentage
    #train-> 9.619552944516201
    #test-> 9.594223170402955


    dnn_train_error = 4.221045026115981
    dnn_test_error = 4.226760458354771
    encoder_train_error = 9.619552944516201
    encoder_test_error = 9.594223170402955
    
    features = ['Quantity','UnitPrice','total_price','Frequency', 'Monetary', 'Recency','Country','ProductCategory','ProductDiversity']

    clv_input = []
    countrys = ['United Kingdom', 'France', 'Australia', 'Netherlands', 'Germany',
       'Norway', 'EIRE', 'Switzerland', 'Spain', 'Poland', 'Portugal',
       'Italy', 'Belgium', 'Lithuania', 'Japan', 'Iceland',
       'Channel Islands', 'Denmark', 'Cyprus', 'Sweden', 'Finland',
       'Austria', 'Bahrain', 'Israel', 'Greece', 'Hong Kong', 'Singapore',
       'Lebanon', 'United Arab Emirates', 'Saudi Arabia',
       'Czech Republic', 'Canada', 'Unspecified', 'Brazil', 'USA',
       'European Community', 'Malta', 'RSA']
    countrys_enc = [36., 13.,  0., 24., 14., 25., 10., 33., 31., 26., 27., 19.,  3.,
       22., 20., 17.,  6.,  9.,  7., 32., 12.,  1.,  2., 18., 15., 16.,
       30., 21., 35., 29.,  8.,  5., 37.,  4., 34., 11., 23., 28.]
    products = ['Home', 'Other', 'Fashion', 'Kitchen', 'Stationery', 'Accessories']
    products_enc = [2, 4, 1, 3, 5, 0]
    for f in features:
        if f == 'Country':
            val =  st.sidebar.selectbox('Enter Country',options=countrys)
            val = countrys_enc[countrys.index(val)]
        elif f == 'ProductCategory':
            val =  st.sidebar.selectbox('Enter Country',options=products)
            val = products_enc[products.index(val)]
        else : val = st.sidebar.number_input(f"Enter {f}", min_value=0.0, value=1.0)
        clv_input.append(val)

    input_array = np.array(clv_input).reshape(1,-1)

    # normalize input as training preprocessing
    input_array_log = np.log1p(input_array)  # same as training
    pred = st.sidebar.button('Predict')


    # Predict CLV using both models

    # Confidence Score Calculation
    def confidence_score(pred, model_std=0.35):
        score = math.exp(-model_std * abs(pred))
        return round(score*100,2)
                     
    if pred:
        st.session_state.dnn_pred = dnn_model.predict(input_array_log)[0][0]
        st.session_state.encoder_pred = encoder_model.predict(input_array_log)[0][0]
        pred = False
        st.rerun()


    if 'dnn_pred' in st.session_state:
        dnn_pred = f"{st.session_state.dnn_pred:.2f}"
        encoder_pred = f"{st.session_state.encoder_pred:.2f}"
        confidence_dnn = f"{confidence_score(st.session_state.dnn_pred)}%"
        confidence_encoder = f"{confidence_score(st.session_state.encoder_pred)}%"
    else:
        dnn_pred = '-'
        encoder_pred = '-'
        confidence_dnn = '-'
        confidence_encoder = '-'

    #CLV Prediction & Confidence Cards 
    st.subheader("🤖 CLV Prediction & Confidence")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("**DNN Model**")
        st.write(f"Prediction: {dnn_pred:}")
        st.write(f"Confidence: {confidence_dnn}")

    with col2:
        st.subheader("**Encoder Model**")
        st.write(f"Prediction: {encoder_pred}")
        st.write(f"Confidence: {confidence_encoder}")

    st.write("--------------------------------Modles metrics-------------------------")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Training Error (%)", f"{dnn_train_error}")
        st.metric("Testing Error (%)", f"{dnn_test_error}")

    with col2:
        st.metric("Training Error (%)", f"{encoder_train_error}")
        st.metric("Testing Error (%)", f"{encoder_test_error}")

    # Model Error Comparison Chart
    st.subheader("📊 Model Error Comparison")


    df_errors = pd.DataFrame({
        'Model': ['DNN','DNN','Encoder','Encoder'],
        'Type': ['Training','Testing','Training','Testing'],
        'Error': [dnn_train_error, dnn_test_error, encoder_train_error, encoder_test_error]
    })

    chart = alt.Chart(df_errors).mark_bar().encode(
        x='Model:N',
        y='Error:Q',
        color='Type:N',
        tooltip=['Model','Type','Error']
    ).properties(width=600)

    st.altair_chart(chart)


#________________________________________________________________________________