# Sales Demand Forecasting Dashboard

Streamlit app for visualizing historical sales trends and forecasting future sales using a machine learning model.

## Run Locally

1. Create and activate a virtual environment.
2. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

3. Run the app:

	```bash
	streamlit run app.py
	```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to Streamlit Community Cloud: <https://share.streamlit.io/>
3. Click **New app** and select this repository.
4. Use these settings:
	- **Branch:** `main`
	- **Main file path:** `app.py`
5. Click **Deploy**.

The app reads data from `data/processed/featured_sales_data.csv`, which is already committed in this repository.