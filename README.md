# 🛒 Retail Analytics Suite

A comprehensive, interactive dashboard built with **Streamlit**, **SQLAlchemy**, and **Python** for analyzing and managing key retail operations including:

- 📈 Sales Analytics  
- 📦 Inventory Forecasting & Management  
- 🎯 Product Recommendation System  

This end-to-end data science project is backed by a simulated e-commerce dataset and provides valuable insights for data-driven retail decisions.

---

## 🔍 Features

### 📈 Sales Analytics
- Visualize total revenue, orders, and quantity sold
- Analyze daily sales trends and top-selling products
- Category-wise performance metrics

### 📦 Inventory Management & Forecasting
- Track stock levels and reorder alerts
- Forecast future demand using time series modeling (e.g., ARIMA)
- Add/update products from within the dashboard

### 🎯 Recommendation System
- Personalized product recommendations based on user purchase history
- Enhanced product lookup and search features

---

## 🧑‍💻 Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Data processing and backend logic |
| **Streamlit** | Web application and dashboard UI |
| **SQLAlchemy** | Database connection and queries |
| **MySQL** | Relational data storage |
| **Pandas, NumPy, Scikit-learn, Statsmodels** | Data analysis & modeling |

---

## 🧱 Project Structure
```bash
E Commerce Admin Dashboard/
│
├── main.py                        # Streamlit entry point (Home page)
├── pages/                         # Individual dashboard pages
│   ├── 1_Sales_Analytics.py
│   ├── 2_Inventory_Management_And_Forecasting.py
│   ├── 3_Product_Recommendation.py
│   ├── 4_Customer_Segmentation.py
│
├── data/                          # Sample data files or seed CSVs
│
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation

```
---

## 🗃️ Database Schema

- **users(user_id, username, contact, password, location)**
- **products(product_id, unitprice, description, stock_quantity, category, reorder_level)**
- **orders(order_id, user_id, total_amount, delivery_status, payment_status, order_date)**
- **order_items(order_item_id, order_id, product_id, unitprice, quantity)**

---

## 🚀 How to Run Locally

1. Clone the repo  
```bash
git clone https://github.com/ayushji7420/ECommerceAdminDashboard
cd EcommerceAdminDashboard

