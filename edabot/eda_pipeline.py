import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(file_path):
    """Loads CSV or JSON file into a Pandas DataFrame."""
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            return pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or JSON file.")
    except Exception as e:
        return {"error": f"Failed to load data: {str(e)}"}

def validate_data(df):
    """Checks for missing values and duplicate rows."""
    missing_values = df.isnull().sum().to_dict()
    duplicate_rows = df.duplicated().sum()
    return {
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows
    }

def generate_summary(df):
    """Computes basic descriptive statistics."""
    try:
        summary = df.describe().to_dict()
        return summary
    except Exception as e:
        return {"error": f"Failed to generate summary: {str(e)}"}

def create_visualizations(df):
    """Creates basic visualizations and saves them as images."""
    try:
        os.makedirs("static", exist_ok=True)

        # Histogram
        num_cols = df.select_dtypes(include=['number']).columns
        for col in num_cols:
            plt.figure()
            sns.histplot(df[col], bins=20, kde=True)
            plt.title(f"Histogram of {col}")
            plt.savefig(f"static/{col}_hist.png")
            plt.close()

        return {"plots": [f"/static/{col}_hist.png" for col in num_cols]}
    except Exception as e:
        return {"error": f"Failed to create visualizations: {str(e)}"}

def detect_anomalies(df):
    """Detects outliers using the IQR method."""
    anomalies = {}
    try:
        for col in df.select_dtypes(include=['number']).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
            anomalies[col] = len(outliers)
        return anomalies
    except Exception as e:
        return {"error": f"Failed to detect anomalies: {str(e)}"}

def run_eda(file_path):
    """Runs the full EDA pipeline and returns a structured report."""
    df = load_data(file_path)
    if isinstance(df, dict) and "error" in df:
        return df  # Return error message

    report = {
        "validation": validate_data(df),
        "summary": generate_summary(df),
        "anomalies": detect_anomalies(df),
        "visualizations": create_visualizations(df)
    }

    return report
