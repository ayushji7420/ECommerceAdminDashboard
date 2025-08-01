import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.metrics.pairwise import cosine_similarity

# DB Connection
engine = create_engine("mysql+pymysql://root:%40aAyush123@localhost/ecommercedata")

st.title("🎯 Product Recommendation System")

# --- 1. Load user-product purchase data ---
with engine.connect() as conn:
    query = text("""
        SELECT 
            o.user_id,
            u.username,
            oi.product_id,
            p.description
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN users u ON o.user_id = u.user_id
    """)
    df = pd.read_sql(query, conn)

# --- 2. Create User-Item Matrix ---
user_item_matrix = pd.crosstab(df['user_id'], df['product_id'])

# --- 3. Compute Item-Item Similarity ---
product_similarity = cosine_similarity(user_item_matrix.T)
similarity_df = pd.DataFrame(product_similarity, 
                             index=user_item_matrix.columns, 
                             columns=user_item_matrix.columns)

# --- 4. Product & User Info ---
product_map = df[['product_id', 'description']].drop_duplicates().set_index('product_id')['description'].to_dict()
users = df['username'].unique()

user_map = df[['user_id', 'username']].drop_duplicates().set_index('username')['user_id'].to_dict()

# --- 5. Streamlit UI ---
selected_username = st.selectbox("Select a User", sorted(user_map.keys()))
selected_user = user_map[selected_username]


if selected_user:
    # Products user has bought
    purchased = user_item_matrix.loc[selected_user]
    purchased_products = purchased[purchased > 0].index.tolist()
    
    st.subheader("🛒 Products Already Purchased:")
    st.write([product_map[pid] for pid in purchased_products])

    # --- 6. Recommend Products ---
    sim_scores = similarity_df[purchased_products].sum(axis=1)
    sim_scores = sim_scores.drop(purchased_products)  # Remove already purchased
    top_recommendations = sim_scores.sort_values(ascending=False).head(5)

    st.subheader("🔮 Recommended Products:")
    for pid in top_recommendations.index:
        st.markdown(f"- **{product_map.get(pid, 'Unknown Product')}** (Score: {top_recommendations[pid]:.2f})")
