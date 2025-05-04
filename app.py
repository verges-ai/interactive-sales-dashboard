from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Load and prepare data
    df = pd.read_csv("static/data/train.csv")  # Change to read_csv if it's a CSV file
    df.rename(columns={
    'Order Date': 'Order_Date',
    'Ship Date': 'Ship_Date',
    'Sales': 'Sales_Amount'
    }, inplace=True)
    df.columns = df.columns.str.strip()  # remove extra spaces in column names
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], dayfirst=True, errors='coerce')
    df['Ship_Date'] = pd.to_datetime(df['Ship_Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Order_Date'].dt.year
    df['Month'] = df['Order_Date'].dt.to_period('M').astype(str)

    # Get year from query parameters (default to 2017)
    selected_year = request.args.get('year', default=2017, type=int)
    df_year = df[df['Year'] == selected_year]

    # KPIs
    total_sales = df_year['Sales_Amount'].sum()
    total_orders = df_year['Order ID'].nunique()
    estimated_profit = total_sales * 0.20

    # Available years for dropdown
    available_years = sorted(df['Year'].unique())

    # Chart 1: Sales by Region
    fig1 = px.bar(df_year, x='Region', y='Sales_Amount', color='Category',
                  title=f'Sales by Region and Category - {selected_year}')
    chart1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')

    # Chart 2: Monthly Sales Trend
    monthly_sales = df_year.groupby('Month')['Sales_Amount'].sum().reset_index()
    monthly_sales['Month'] = pd.to_datetime(monthly_sales['Month'])
    monthly_sales.sort_values('Month', inplace=True)
    fig2 = px.line(monthly_sales, x='Month', y='Sales_Amount',
                   title=f'Monthly Sales Trend - {selected_year}')
    chart2 = fig2.to_html(full_html=False, include_plotlyjs=False)

    # Chart 3: Top 10 Products
    top_products = (
        df_year.groupby('Product Name')['Sales_Amount']
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    fig3 = px.bar(top_products, x='Sales_Amount', y='Product Name',
                  orientation='h', title='Top 10 Products by Sales')
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
    chart3 = fig3.to_html(full_html=False, include_plotlyjs=False)

    return render_template("dashboard.html",
                           total_sales=f"{total_sales:,.0f}",
                           total_orders=total_orders,
                           estimated_profit=f"{estimated_profit:,.0f}",
                           chart1=chart1,
                           chart2=chart2,
                           chart3=chart3,
                           selected_year=selected_year,
                           available_years=available_years)

if __name__ == '__main__':
    app.run(debug=True)
