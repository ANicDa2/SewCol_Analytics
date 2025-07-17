import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

@st.cache_data
def load_data(file_path):
    df = pd.read_csv("https://raw.githubusercontent.com/ANicDa2/SewCol_Analytics/refs/heads/main/app_data/data.csv")
    df['ItemCreationDate'] = pd.to_datetime(df['ItemCreationDate'], format='%d/%m/%Y')
    return df

# Calculate metrics
def calculate_metrics(df):
    current_month = datetime.now().month
    last_month = current_month - 1 if current_month > 1 else 12
    current_year = datetime.now().year
    last_month_year = current_year if last_month != 12 else current_year - 1

    this_month_data = df[(df['ItemCreationDate'].dt.month == current_month) & (df['ItemCreationDate'].dt.year == current_year)]
    last_month_data = df[(df['ItemCreationDate'].dt.month == last_month) & (df['ItemCreationDate'].dt.year == last_month_year)]

    avg_price_this_month = this_month_data['Price'].mean()
    avg_price_last_month = last_month_data['Price'].mean()
    num_items_this_month = this_month_data.shape[0]
    num_items_last_month = last_month_data.shape[0]

    avg_price_change = ((avg_price_this_month - avg_price_last_month) / avg_price_last_month * 100) if avg_price_last_month else 0
    num_items_change = ((num_items_this_month - num_items_last_month) / num_items_last_month * 100) if num_items_last_month else 0

    return avg_price_this_month, avg_price_change, num_items_this_month, num_items_change

# Main app
def main():
    st.title("Ebay Market Research")

    # Load data
    df = load_data('app_data\\data.csv')

    # Filter by Brand
    brands = df['Brand'].unique()
    selected_brand = st.selectbox("Select a Brand", brands)
    filtered_df = df[df['Brand'] == selected_brand]

    # Display metrics
    avg_price, avg_price_change, num_items, num_items_change = calculate_metrics(filtered_df)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Average Price This Month", value=f"${avg_price:.2f}", delta=f"{avg_price_change:.2f}%")
    with col2:
        st.metric(label="Number of Items This Month", value=num_items, delta=f"{num_items_change:.2f}%")

    # Plot number of items over time
    items_over_time = filtered_df.groupby(filtered_df['ItemCreationDate'].dt.to_period('M')).size().reset_index(name='Number of Items')
    items_over_time['ItemCreationDate'] = items_over_time['ItemCreationDate'].dt.to_timestamp()
    fig_items = px.line(items_over_time, x='ItemCreationDate', y='Number of Items', title='Number of Items Over Time')
    st.plotly_chart(fig_items)

    # Plot average price over time
    fig_price = px.scatter(filtered_df, x='ItemCreationDate', y='Price', title='Price Over Time')
    st.plotly_chart(fig_price)

    # Plot price distribution grouped by $100
    max_price = int(filtered_df['Price'].max()) + 100
    number_bins = int(max_price/100)
    fig_price_dist = px.histogram(filtered_df, x="Price", nbins = number_bins, title='Price Buckets')
    st.plotly_chart(fig_price_dist)
if __name__ == "__main__":
    main()
