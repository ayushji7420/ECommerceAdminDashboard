import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Assuming engine is already defined
engine = create_engine("mysql+pymysql://root:%40aAyush123@localhost/ecommercedata")

st.title("📦 Inventory Forecasting & Management")

# Step 1: Category selection
category_query = "SELECT DISTINCT category FROM products"
categories = pd.read_sql(category_query, engine)['category'].tolist()

selected_category = st.selectbox("Select a Category", categories)

# Step 2: Product selection with search
product_query = f"""
SELECT DISTINCT product_id, description 
FROM products 
WHERE category = '{selected_category}'
"""
products_df = pd.read_sql(product_query, engine)

product_options = {
    f"{row['product_id']} - {row['description']}": row['product_id']
    for _, row in products_df.iterrows()
}

product_display_list = ["All Products"] + list(product_options.keys())
selected_product_display = st.selectbox("🔍 Select a Product", product_display_list)
selected_product_id = product_options.get(selected_product_display)

# Step 3: Query order + inventory data
base_query = f"""
SELECT 
    p.product_id,
    p.description,
    p.stock_quantity,
    p.reorder_level,
    p.category,
    o.order_date,
    oi.quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE p.category = '{selected_category}'
"""


if selected_product_id:
    base_query += f" AND p.product_id = '{selected_product_id}'"

df = pd.read_sql(base_query, engine)
df['order_date'] = pd.to_datetime(df['order_date'])

if df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# Step 4: Forecast demand (7-day average)
forecast_horizon = 7
inventory_data = []

for product_id in df['product_id'].unique():
    prod_data = df[df['product_id'] == product_id]
    daily_sales = prod_data.groupby('order_date')['quantity'].sum().resample('D').sum().fillna(0)
    
    avg_daily_demand = daily_sales[-7:].mean()  # Use last 7 days
    forecast_demand = int(np.round(avg_daily_demand * forecast_horizon))

    prod_info = prod_data.iloc[0]
    stock = prod_info['stock_quantity']
    reorder_level = prod_info['reorder_level']
    description = prod_info['description']
    category = prod_info['category']

    reorder_alert = "✅ OK" if stock >= forecast_demand else "⚠️ Reorder Needed"

    inventory_data.append({
        "Product ID": product_id,
        "Description": description,
        "Category": category,
        "Current Stock": stock,
        "Forecasted Demand (7d)": forecast_demand,
        "Reorder Level": reorder_level,
        "Status": reorder_alert
    })

inventory_df = pd.DataFrame(inventory_data)

total_products = inventory_df.shape[0]
reorder_needed = inventory_df[inventory_df['Status'] != "✅ OK"].shape[0]
out_of_stock = inventory_df[inventory_df['Current Stock'] == 0].shape[0]

col1,col2,col3 = st.columns(3)
col1.metric("🛒 Total Products", total_products)
col2.metric("⚠️ Reorder Needed", reorder_needed)
col3.metric("❌ Out of Stock", out_of_stock)

# Step 5: Display Results
st.subheader(f"📊 Inventory Status for Category: {selected_category}")
st.dataframe(
    inventory_df.sort_values(by='Forecasted Demand (7d)', ascending=False).reset_index(drop=True),
    use_container_width=True
)

# product_display_list = ["All Products"] + list(product_options.keys()) + ["➕ Add New Product"]
selected_product_display = st.button("Add New Product")

if selected_product_display:
    st.subheader("📦 Add a New Product")

    with st.form("add_product_form"):
        new_product_id = st.text_input("Product ID")
        new_description = st.text_input("Product Description")
        new_unitprice = st.number_input("Unit Price", min_value=0.0)
        new_stock = st.number_input("Stock Quantity", min_value=0)
        new_category = st.text_input("Category")
        new_reorder_level = st.number_input("Reorder Level", min_value=0)

        submitted = st.form_submit_button("Add Product")

        if submitted:
            # Validate inputs (simple)
            if not all([new_product_id, new_description, new_category]):
                st.warning("Please fill all required fields.")
            else:
                insert_query = f"""
                INSERT INTO products (product_id, description, unitprice, stock_quantity, category, reorder_level)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    new_product_id,
                    new_description,
                    new_unitprice,
                    new_stock,
                    new_category,
                    new_reorder_level
                )

                with engine.begin() as conn:
                    conn.execute(insert_query, values)

                st.success(f"✅ Product '{new_product_id}' added successfully!")

