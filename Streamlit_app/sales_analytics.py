import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine


engine = create_engine("mysql+pymysql://root:%40aAyush123@localhost/ecommercedata")

#-----Metrics And Sales Trend-----
query_daily = """
SELECT 
    DATE(o.order_date) as order_day,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.unitprice * oi.quantity) as total_sales,
    COUNT(DISTINCT o.user_id) as unique_customers
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_date)
ORDER BY order_day;
"""
df_daily = pd.read_sql(query_daily, con=engine)



st.title("📈 Sales Analytics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${df_daily['total_sales'].sum():,.2f}")
col2.metric("Total Orders", f"{df_daily['total_orders'].sum()}")
col3.metric("Unique Customers", f"{df_daily['unique_customers'].sum()}")
aov = df_daily['total_sales'].sum() / df_daily['total_orders'].sum()
col4.metric("🧾 Avg Order Value", f"${aov:.2f}")


df_prophet = df_daily[['order_day', 'total_sales']].rename(columns={
    'order_day': 'ds',
    'total_sales': 'y'
})

from prophet import Prophet

model = Prophet()
model.fit(df_prophet)

future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

forecast_df = forecast[['ds', 'yhat']].copy()
forecast_df['type'] = 'Predicted'

actual_df = df_prophet.copy()
actual_df.rename(columns={'y': 'yhat'}, inplace=True)
actual_df['type'] = 'Actual'

combined = pd.concat([actual_df, forecast_df], ignore_index=True)

st.subheader("📈 Daily Sales Trend")
line_chart = alt.Chart(combined).mark_line().encode(
    x=alt.X('ds:T', title="Time"),
    y=alt.Y('yhat:Q', sort='-x', title="Total Sales"),
    color=alt.Color('type:N',
        scale=alt.Scale(
            domain=['Actual', 'Predicted'],       
            range=["#0d4b77", "#18c930"]           
        ),
        legend=alt.Legend(title="Sales Type")
    )
).properties(
    title='Actual vs Forecasted Sales'
)

st.altair_chart(line_chart, use_container_width=True)


#-----Top 5 Products -----

query_top5 = """
SELECT 
    p.description AS product,
    SUM(oi.unitprice * oi.quantity) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 5;
"""

df_top5 = pd.read_sql(query_top5, con=engine)

st.subheader("🏆 Top 5 Products by Revenue")
bar_top = alt.Chart(df_top5).mark_bar().encode(
    x=alt.X('revenue:Q', title="Revenue"),
    y=alt.Y('product:N', sort='-x', title="Product")
).properties(height=300)
st.altair_chart(bar_top, use_container_width=True)


#-----Category Sales-----

query_bycategory = """
SELECT 
    p.category,
    SUM(oi.unitprice * oi.quantity) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales DESC;
"""

df_bycategory = pd.read_sql(query_bycategory, con=engine)

st.subheader("📂 Sales by Category")
bar_cat = alt.Chart(df_bycategory).mark_bar().encode(
    x=alt.X('category:N', title="Category", sort='-y'),
    y=alt.Y('total_sales:Q', title="Total Sales")
).properties(height=300)
st.altair_chart(bar_cat, use_container_width=True)