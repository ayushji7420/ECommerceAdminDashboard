import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine, text
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- Database connection ---
# Replace with your actual connection string
engine = create_engine("mysql+pymysql://root:%40aAyush123@localhost/ecommercedata")

st.title('👥 Customer Segmentation Dashboard')

# --- 1. Load Orders Data ---
with engine.connect() as conn:
    query = text("""
        SELECT 
            user_id,
            order_id,
            order_date,
            total_amount
        FROM orders
        WHERE order_date IS NOT NULL
    """)
    orders_df = pd.read_sql(query, conn)

# Ensure correct date format
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])

# Reference date for Recency
today = orders_df['order_date'].max() + pd.Timedelta(days=1)

# --- 2. Build RFM Table ---
rfm = (
    orders_df.groupby('user_id')
    .agg(
        Recency=('order_date', lambda x: (today - x.max()).days),
        Frequency=('order_id', 'nunique'),
        Monetary=('total_amount', 'sum')
    )
    .reset_index()
)
rfm['AOV'] = rfm['Monetary'] / rfm['Frequency']

# --- 3. K-Means Clustering ---
features = rfm[['Recency', 'Frequency', 'Monetary']]
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=4, random_state=42)
rfm['Segment'] = kmeans.fit_predict(rfm_scaled)

# Custom segment labels (can be tuned)
label_map = {
    0: 'Occasional',
    1: 'Loyal',
    2: 'High-Value',
    3: 'At-Risk'
}
rfm['SegmentName'] = rfm['Segment'].map(label_map)

# --- 4. Streamlit Display ---

# KPIs
col1, col2 = st.columns(2)
col1.metric("Total Customers", len(rfm))
col2.metric("Customer Segments", rfm['SegmentName'].nunique())

# Segment distribution chart
segment_counts = rfm['SegmentName'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'User Count']

bar_chart = alt.Chart(segment_counts).mark_bar().encode(
    x=alt.X('Segment:N', title='Segment'),
    y=alt.Y('User Count:Q'),
    tooltip=['Segment', 'User Count']
).properties(height=400)

st.altair_chart(bar_chart, use_container_width=True)

# Drill-down
selected_segment = st.selectbox("Select Segment to View Users:", segment_counts['Segment'])

st.dataframe(
    rfm[rfm['SegmentName'] == selected_segment]
    .sort_values('Monetary', ascending=False)
    .reset_index(drop=True)
)

# Optional: export CSV
st.download_button("📥 Download Segment Data", data=rfm.to_csv(index=False), file_name="rfm_segments.csv")
