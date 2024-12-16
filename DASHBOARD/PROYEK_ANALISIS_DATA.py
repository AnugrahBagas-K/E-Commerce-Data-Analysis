import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')


df_orders_items = pd.read_csv(r'df_orders_items.csv')
df_product = pd.read_csv(r'df_product.csv')
df_orders = pd.read_csv(r'df_orders.csv')
df_orders_reviews = pd.read_csv(r'df_orders_reviews.csv')

date_column = {
    'df_orders_items': df_orders_items,
    'df_orders_reviews' : df_orders_reviews,
    'df_orders' : df_orders,
}

for name, df in date_column.items() :
  date_column = [col for col in df.columns if 'date' in col.lower() or 'timestamp' in col.lower()]

  for col in date_column :
    df[col] = pd.to_datetime(df[col], errors='coerce')


df_orders_items_product = pd.merge(
    left = df_orders_items,
    right = df_product,
    how = 'left',
    left_on = 'product_id',
    right_on = 'product_id'
)

df_merge = pd.merge(
    left=df_orders_reviews,
    right=df_orders,
    how='left',
    left_on='order_id',
    right_on='order_id'
)

df_merge2= pd.merge(
    left=df_merge,
    right=df_orders_items_product,
    how='left',
    left_on='order_id',
    right_on='order_id'
)

df_annual_sales = pd.merge(
    left=df_orders_items_product,
    right=df_orders,
    how='left',
    left_on='order_id',
    right_on='order_id'
)

# Analisis Total Penjualan Per Tahun
df_annual_sales['year'] = df_annual_sales['order_purchase_timestamp'].dt.year 
annual_sales_df = df_annual_sales.groupby('year').agg(
    annual_sales=('price','sum')
).reset_index()

st.title("Dashboard E-Commerce")

# Memilih Tahun Untuk Menampilkan Total Penjualan
st.header("Analisis Total Penjualan Tiap Tahun")

# Pilih Tahun dengan Multiselect
st.sidebar.header("Total Penjualan Tiap Tahun")
avail_years = sorted(df_annual_sales['year'].unique())
selected_years = st.sidebar.multiselect("Pilih Tahun:", options=avail_years)

# Filter Data Berdasarkan Tahun yang Dipilih
if selected_years:
    filtered_sales_range = df_annual_sales[df_annual_sales["year"].isin(selected_years)]

    # Kelompokkan Total Penjualan per Tahun atau per Kategori Produk
    sales_by_category = filtered_sales_range.groupby("year").agg(
        total_sales=("price", "sum")
    ).reset_index().sort_values("total_sales", ascending=False)

    st.write(f"Penjualan Tahun : {', '.join(map(str, selected_years))}")
    st.dataframe(sales_by_category)

    st.subheader("Grafik Pola Penjualan Berdasarkan Tahun")
    # Plot Barplot
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(
        sales_by_category["year"],
        sales_by_category["total_sales"],
        marker='o',
        linewidth=2,
        color="skyblue",
    )
    ax.set_title(f"Pola Penjualan Berdasarkan Tahun: {', '.join(map(str, selected_years))}", fontsize=16)
    ax.tick_params(axis="x", labelsize=20)
    ax.tick_params(axis="y", labelsize=15)
    # Tampilkan Barplot di Streamlit
    st.pyplot(fig)
else:
    st.warning("Silakan pilih setidaknya satu tahun untuk melihat data.")


# Total Penjualan

st.sidebar.header("Analisis Total Penjualan")
options_totalsales = sorted(["Pilih Kategori","Price", "Unit"])
select_options = st.sidebar.selectbox("Tampilkan Total Penjualan Beradasarkan :", options=options_totalsales)

st.subheader("Total Penjualan")

if select_options == "Pilih Kategori" :
   st.info("Pilih Total Penjualan Berdasarkan Apa Yang Ingin Ditampilkan")


elif select_options == "Price" :
  sales = df_orders_items_product.groupby(['product_id','product_category_name']).agg(
     total_sales=('price','sum')
    ).sort_values('total_sales', ascending=False)
  total_sales_df = df_orders_items_product.groupby(['product_id','product_category_name']).agg(
     total_sales=('price','sum')
    ).reset_index()
  st.write("Tabel Total Penjualan Berdasarkan Harga:")
  st.dataframe(sales.head(10))

  highest_sales = total_sales_df.nlargest(5, 'total_sales')
  lowes_sales = total_sales_df.nsmallest(5, 'total_sales')

  result_sales = pd.concat([highest_sales, lowes_sales])

  result_sales['label_sales'] = result_sales['product_category_name'].fillna("Unknown")
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.bar(
     result_sales["label_sales"], 
     result_sales["total_sales"],
     color='skyblue'
     )
  ax.set_title("Total Penjualan", loc="center", fontsize=30)
  ax.set_ylabel('Total Penjualan')
  ax.set_xlabel('Product Category Name')
  ax.tick_params(axis='y')
  ax.tick_params(rotation=40, axis='x')
  st.pyplot(fig)


elif select_options == "Unit" :
  units = df_orders_items_product.groupby(['product_id','product_category_name']).agg(
     total_units=('order_item_id','count')
     ).sort_values('total_units',ascending=False).reset_index()
  st.write("Tabel Total Unit Terjual:")
  st.dataframe(units.head(10)) 

  highest_units = units.nlargest(3, 'total_units')
  lowest_units = units.nsmallest(4, 'total_units')
  
  result = pd.concat([highest_units, lowest_units])
  
  result['label'] = result['product_category_name'].fillna("Unknown")
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.bar(
     result["label"], 
     result["total_units"],
     color='skyblue'
     )
  ax.set_title("Total Unit Terjual", loc="center", fontsize=30)
  ax.set_ylabel('Total Unit Terjual')
  ax.set_xlabel('Product Category Name')
  ax.tick_params(axis='y')
  ax.tick_params(rotation=40, axis='x')
  st.pyplot(fig)


# Analisis Total Review

st.subheader("Analisis Score Review")

df_merge2['shipping_time'] = (df_merge2['shipping_limit_date'] - df_merge2['order_purchase_timestamp']).dt.days
review_summary = df_merge2.groupby('review_score').agg(
    total_reviews=('order_id','count'),
    average_time =('shipping_time','mean')
).reset_index()

options_reviews = sorted(review_summary["review_score"].unique())
selected_score = st.sidebar.multiselect("Pilih Skor Review Untuk Ditampilkan : ", options=options_reviews, default=[])

if selected_score :
   filtered_score_review = review_summary[review_summary["review_score"].isin(selected_score)]
   st.dataframe(filtered_score_review)

   fig, ax = plt.subplots(figsize=(8,5))
   ax.bar(
      filtered_score_review["review_score"],
      filtered_score_review["total_reviews"],
      color="skyblue"
   )
   ax.set_title("Total Review Setiap Skor", fontsize=16)
   ax.set_ylabel("Jumlah Review")
   ax.set_xlabel("Skor Review")
   ax.set_xticks(filtered_score_review["review_score"])
   ax.tick_params(axis='y')
   ax.tick_params(axis='x')
   st.pyplot(fig)


   fig, ax = plt.subplots(figsize=(8, 5))
   ax.bar(
      filtered_score_review["review_score"],
      filtered_score_review["average_time"],
      color="orange",
      )
   ax.set_title("Review Skor dan Rata-rata Waktu Pengiriman",  fontsize=16)
   ax.set_ylabel('Rata-rata Waktu Pengiriman')
   ax.set_xlabel('Skor Review')
   ax.set_xticks(filtered_score_review["review_score"])
   ax.tick_params(axis='y')
   ax.tick_params(axis='x')
   # Tampilkan Barplot di Streamlit
   st.pyplot(fig)

else :
   st.info("Pilih Skor 1-5 Untuk Menampilkan Total Review")
