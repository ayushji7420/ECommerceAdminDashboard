import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:%40aAyush123@localhost/ecommercedata")

#-----Metrics-----

def repcustmetric():
    query = """
    SELECT COUNT(*) FROM (
    SELECT user_id FROM orders
    GROUP BY user_id
    HAVING COUNT(*) > 1
    ) AS repeat_customer"""
    val = pd.read_sql(query, engine)
    return val.iloc[0,0]

def last_month_sales():
    query = """
    SELECT SUM(oi.quantity * p.unitprice) AS last_month_sales
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE DATE_FORMAT(o.order_date, '%%Y-%%m') = DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%%Y-%%m')
    """
    df = pd.read_sql(query, engine)
    return df.iloc[0, 0]


def getproductidvsdesc():
    query = "SELECT product_id, description FROM products;"

    df = pd.read_sql(query, engine)
    return df

def getproducttable():
    query = "SELECT * FROM products;"
    df = pd.read_sql(query, engine)
    return df

def getusertable():
    query = "SELECT * FROM users;"
    df = pd.read_sql(query, engine)
    return df

def getorderstable():
    query = "SELECT * FROM orders;"
    df = pd.read_sql(query, engine)
    return df

def getorderitemstable():
    query = "SELECT * FROM order_items;"
    df = pd.read_sql(query, engine)
    return df

def getproductsales(product_id):
    query = f"""
    SELECT 
    quantity,order_date
    FROM order_items WHERE product_id = {product_id};
    """
    df = pd.read_sql(query, engine)
    return df

def getcategorySales():
    return 

def getordervsorderdate():
    return


#-----Inventory_Management-----

def get_inventory_data():
    query = """
    SELECT product_id, description, category, unitprice, stock_quantity, reorder_level
    FROM products
    """
    return pd.read_sql(query, engine)


#-----Customer Churn-----

def get_churned_customers():
    query = """
    SELECT user_id
    FROM users
    WHERE user_id NOT IN (
        SELECT DISTINCT user_id
        FROM orders
        WHERE order_date >= CURDATE() - INTERVAL 60 DAY
    )
    """
    return pd.read_sql(query, engine)