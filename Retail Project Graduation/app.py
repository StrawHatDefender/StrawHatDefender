import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt

# Load the trained model (Random Forest in this case)
rf_model = joblib.load('random_forest_model11.pkl')

# Streamlit UI - Title and Intro
st.title("Retail Sales Forecasting - Predict Future Sales")

st.markdown("""
This app predicts the sales for the next 4 weeks based on your product's recent sales data. 
Enter the sales from the past weeks and see the predicted future sales. 
""")

# Sidebar for Inputs (This makes the interface cleaner)
st.sidebar.header("Input Parameters")
sales_lag1 = st.sidebar.number_input("Sales from last week (Sales Lag 1):", min_value=0.0, value=100.0)
sales_lag2 = st.sidebar.number_input("Sales from 2 weeks ago (Sales Lag 2):", min_value=0.0, value=95.0)
sales_lag3 = st.sidebar.number_input("Sales from 3 weeks ago (Sales Lag 3):", min_value=0.0, value=90.0)
sales_lag4 = st.sidebar.number_input("Sales from 4 weeks ago (Sales Lag 4):", min_value=0.0, value=85.0)

year = st.sidebar.number_input("Year:", min_value=2020, max_value=2025, value=2023)
month = st.sidebar.number_input("Month (1-12):", min_value=1, max_value=12, value=6)
week = st.sidebar.number_input("Week number:", min_value=1, max_value=52, value=24)
day = st.sidebar.number_input("Day of the week (0=Monday, 6=Sunday):", min_value=0, max_value=6, value=3)


# Check if all inputs are 0 (which could be unrealistic)
if sales_lag1 == 0.0 and sales_lag2 == 0.0 and sales_lag3 == 0.0 and sales_lag4 == 0.0:
    st.warning("Warning: You entered all sales values as 0. Predictions based on zero sales data may not be reliable.")
    st.markdown("""
    Please provide realistic sales data for the last few weeks to get accurate predictions. 
    If your product has not sold before, it may not be suitable for prediction at this stage.
    """)
    # Stop the execution here, don't run the prediction part
    st.stop()  # This stops further code execution

# Create a DataFrame from the user input
latest_data = pd.DataFrame({
    'Sales Lag1': [sales_lag1],
    'Sales Lag2': [sales_lag2],
    'Sales Lag3': [sales_lag3],
    'Sales Lag4': [sales_lag4],
    'Year': [year],
    'Month': [month],
    'Week': [week],
    'Day': [day]
})

# Function to reset inputs
def reset_inputs():
    st.session_state.sales_lag1 = 100.0
    st.session_state.sales_lag2 = 95.0
    st.session_state.sales_lag3 = 90.0
    st.session_state.sales_lag4 = 85.0
    st.session_state.year = 2023
    st.session_state.month = 6
    st.session_state.week = 24
    st.session_state.day = 3

# Add Reset button to clear inputs
if st.button("Clear Inputs"):
    reset_inputs()

# Display the prediction process with a progress bar and spinner
if st.button('Predict Future Sales'):
    with st.spinner('Predicting sales...'):
        # Show progress bar while making predictions
        progress_bar = st.progress(0)
        future_sales = []

        # Predict the sales for the next 4 weeks
        for i in range(4):
            prediction = rf_model.predict(latest_data)
            future_sales.append(prediction[0])

            # Update the lag features for the next prediction
            latest_data['Sales Lag4'] = latest_data['Sales Lag3']
            latest_data['Sales Lag3'] = latest_data['Sales Lag2']
            latest_data['Sales Lag2'] = latest_data['Sales Lag1']
            latest_data['Sales Lag1'] = prediction[0]

            # Update progress bar
            progress_bar.progress((i + 1) * 25)

    # Predictions completed
    st.success('Predictions completed!')

    # Display the predictions
    st.write("### Predicted Sales for the Next 4 Weeks:")
    for i, sales in enumerate(future_sales, 1):
        st.write(f"**Week {i}: {sales:.2f} units**")

    # Plotting the sales as a bar chart
    st.write("### Sales Prediction Bar Chart")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar([f'Week {i}' for i in range(1, 5)], future_sales, color='skyblue')
    ax.set_xlabel('Week')
    ax.set_ylabel('Units Sold')
    ax.set_title('Predicted Sales for the Next 4 Weeks')
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Analyzing Sales Trend
    st.write("### Sales Trend Analysis")

    # Week-to-week comparison to determine if sales are increasing or decreasing
    sales_increasing = True  # Assume increasing unless proven otherwise

    for i in range(1, len(future_sales)):
        if future_sales[i] < future_sales[i - 1]:  # Sales dropped between weeks
            sales_increasing = False
            break

    # If sales are increasing
    if sales_increasing:
        st.success("Sales are predicted to increase in the coming weeks! 🎉")
    else:
        st.warning("Sales are predicted to decrease in the coming weeks. ⚠️")

    # Provide tailored tips based on the trend
    if sales_increasing:
        st.write("#### Tips to Maintain and Enhance Sales:")
        st.write("""
        - **Optimize Inventory**: Ensure that your stock levels align with increased demand.
        - **Run Promotions**: Leverage discounts or limited-time offers to attract more customers.
        - **Improve Marketing**: Focus on advertising to reinforce the sales trend.
        """)
    else:
        st.write("#### Tips to Improve Sales:")
        st.write("""
        - **Promote Bestsellers**: Focus on top-performing products and run targeted marketing campaigns.
        - **Improve Customer Experience**: Analyze customer feedback to improve product offerings.
        - **Adjust Pricing**: Review your pricing strategy to stay competitive in the market.
        """)

    # **Historical Sales Visualization - Only Display After Prediction**
    st.write("### Historical Sales Trend")
    historical_sales = [sales_lag4, sales_lag3, sales_lag2, sales_lag1]  # Example historical sales data

    # Plot historical sales data
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([4, 3, 2, 1], historical_sales, marker='o', linestyle='-', color='green')
    ax.set_xlabel('Weeks Ago')
    ax.set_ylabel('Units Sold')
    ax.set_title('Historical Sales Trend')
    plt.xticks([4, 3, 2, 1], ['4 Weeks Ago', '3 Weeks Ago', '2 Weeks Ago', 'Last Week'])
    st.pyplot(fig)

    # Convert the results into a DataFrame for download
    sales_data = {
        'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'Predicted Sales (Units)': future_sales
    }

    # Create a DataFrame for the predicted sales
    sales_df = pd.DataFrame(sales_data)

    # Provide download button for the user to download the results
    csv = sales_df.to_csv(index=False)
    st.download_button(
        label="Download Prediction Results",
        data=csv,
        file_name="sales_predictions.csv",
        mime="text/csv"
    )
