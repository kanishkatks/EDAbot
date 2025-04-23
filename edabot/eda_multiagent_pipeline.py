import pandas as pd
import numpy as np
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional, Callable
import statsmodels.api as sm
from openai import OpenAI
import re
from scipy.fft import fft, fftfreq


# Ensure static directory exists for saving plots
os.makedirs("static", exist_ok=True)

### 1. Define State Model ###
class EDAState(BaseModel):
    """State for the EDA pipeline."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: Any = Field(description="The dataframe to analyze")
    validation: Dict[str, Any] = Field(default_factory=dict)
    info: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    anomalies: Dict[str, Any] = Field(default_factory=dict)
    visualizations: Dict[str, Any] = Field(default_factory=dict)
    report: Dict[str, Any] = Field(default_factory=dict)
    narrative: str = Field(default="")


### 2. Define Functions for Each Node ###
def validate_data(state: EDAState) -> EDAState:
    """Checks for missing values and duplicate rows."""
    df = state.data
    date_column_patterns = ["date", "published", "issued", "on", "created", "timestamp", "time", "day", "month", "hour"]
    suspicious_date_columns = []

    for col in df.columns:
        col_lower = col.lower()
        if any(re.search(rf"\b{pattern}\b", col_lower) for pattern in date_column_patterns):
            if not np.issubdtype(df[col].dtype, np.datetime64):
                suspicious_date_columns.append(col)

    def detect_cyclical_numeric_with_fft(df: pd.DataFrame) -> list:
        cyclical_cols = []

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Apply Fourier transform
                data = df[col].dropna().values
                N = len(data)
                T = 1.0  # Assume uniform spacing between data points (could be adjusted)
                x = np.linspace(0.0, N*T, N, endpoint=False)
                yf = fft(data)
                xf = fftfreq(N, T)[:N//2]
                amplitude = 2.0/N * np.abs(yf[:N//2])

                # Look for peaks in frequency that might indicate cycles
                if np.max(amplitude) > 0.8:  # Set threshold for significant peak
                    cyclical_cols.append(col)

        return cyclical_cols
    cyclical_cols = detect_cyclical_numeric_with_fft(df)

    state.validation = {
        "missingValues": df.isnull().sum().to_dict(),
        "duplicateRows": df.duplicated().sum(),
        "suspiciousDate": suspicious_date_columns,
        "suspectedCyclical": cyclical_cols

    }
    return state

def summary_info(state: EDAState) -> EDAState:
    """Computes information about the dataframe."""
    df = state.data
    state.info = {
        "rowCount": int(df.shape[0]),
        "columnCount": int(df.shape[1]),
        "columnNames": df.columns.tolist(),
        # "columnTypes": df.dtypes.to_dict()
    }

    return state
def generate_summary(state: EDAState) -> EDAState:
    """Computes basic descriptive statistics."""
    df = state.data
    state.summary = df.describe().to_dict()
    return state

def create_visualizations(state: EDAState) -> EDAState:
    """Creates visualizations and saves them as images."""
    df = state.data
    num_cols = df.select_dtypes(include=["number"]).columns
    plot_paths = {}

    # Ensure static directory exists
    os.makedirs("static", exist_ok=True)

    # Generate histograms
    for col in num_cols:

        fig, ax = plt.subplots(1,3, figsize=(15,5))
        ax[0].set_title(f"Distribution of the {col}")
        sns.histplot(data = df, x = f"{col}", kde = True, ax = ax[0])

        ax[1].set_title(f"Boxplot of the {col}")
        sns.boxplot(data = df, x = f"{col}",  ax = ax[1])

        ax[2].set_title(f"Gaussianity of thet  {col}")
        sm.qqplot(df[f'{col}'], line = 's', ax = ax[2])

        fig.suptitle(f"Distribution of {col}")
        plot_path = f"static/{col}_plots.png"
        plt.savefig(plot_path)
        plt.close()
        plot_paths[f"{col}"] = plot_path

        plt.figure(figsize=(10, 6))
        sns.histplot(df[col], bins=20, kde=True)
        plt.title(f"Histogram of {col}")
        plt.savefig(f"static/{col}_hist.png")
        plt.close()
        plot_paths[f"{col}_hist"] = f"static/{col}_hist.png"

        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x=col)
        plt.title(f"Boxplot of {col}")
        plt.savefig(f"static/{col}_boxplot.png")
        plt.close()
        plot_paths[f"{col}_boxplot"] = f"static/{col}_boxplot.png"

        plt.figure(figsize=(10, 6))
        sm.qqplot(df[col], line='s')
        plt.title(f"QQ Plot of {col}")
        plt.savefig(f"static/{col}_qqplot.png")
        plt.close()
        plot_paths[f"{col}_qqplot"] = f"static/{col}_qqplot.png"



    # Generate correlation heatmap
    if len(num_cols) > 1:  # Only create heatmap if multiple numeric columns exist
        plt.figure(figsize=(10, 6))
        sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Heatmap")
        heatmap_path = "static/correlation_heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()
        plot_paths["correlation_heatmap"] = heatmap_path

    state.visualizations = plot_paths
    return state

def detect_anomalies(state: EDAState) -> EDAState:
    """Detects outliers using IQR method."""
    df = state.data
    anomalies = {}

    for col in df.select_dtypes(include=["number"]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
        anomalies[col] = len(outliers)

    state.anomalies = anomalies
    return state

def generate_report(state: EDAState) -> EDAState:
    """Generates final EDA report combining all insights."""
    report = {
    "Validation": state.validation,
    "Summary_info": state.info,
    "Summary": state.summary,
    "Anomalies": state.anomalies,
    "Narrative": state.narrative,
    "Visualizations": state.visualizations,
    }
    state.report = report
    return state

def generate_narrative(state: EDAState) -> EDAState:
    """
    Uses an LLM  to generate a narrative explanation based on EDA results.
    """
    # Construct the prompt using your EDA results.
    prompt = (
            "Based on the following EDA results, provide a concise narrative explanation in 250 words or less. "
            "Please structure your response in bullet points using HTML tags as plain text:\n\n"
            f"Validation: {state.validation}\n\n"
            f"Summary Information: {state.info}\n\n"
            f"Summary Statistics: {state.summary}\n\n"
            f"Anomalies: {state.anomalies}\n\n"

            "In your explanation, address the following:\n"
            "<ul>\n"
            "<li>Any interesting trends or patterns in the data.</li>\n"
            "<li>Potential data quality issues or outliers.</li>\n"
            "<li>Suggestions for further analysis or next steps.</li>\n"
            "</ul>\n\n"

            "Ensure that the response is formatted as a plain string, with HTML tags (e.g., <ul>, <li>) included as part of the text, "
            "so it can be included in a JSON response and displayed as a plain string with HTML tags."
        )

    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


        # Call the OpenAI Chat Completion API
        response = client.responses.create(
            model="gpt-3.5-turbo",
            input=[
                {"role": "system", "content": "You are an expert data scientist specialized in EDA and data insights."},
                {"role": "user", "content": prompt}
            ],
           max_output_tokens= 300
        )

        narrative_text = response.output_text
    except Exception as e:
        # In case of error, fall back to a basic explanation.
        narrative_text = f"An error occurred while generating narrative: {str(e)}"

    state.narrative = narrative_text
    return state

### 3. Build Multi-Agent Graph ###
def build_graph():
    """Build and return the EDA graph."""

    # Build graph
    workflow = StateGraph(EDAState)

    workflow.add_node("validate_data", validate_data)
    workflow.add_node("generate_summary", generate_summary)
    workflow.add_node("create_visualizations", create_visualizations)
    workflow.add_node("generate_anomalies", detect_anomalies)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("generate_narrative", generate_narrative)
    workflow.add_node("summary_info", summary_info)


    # Define edges
    workflow.add_edge("validate_data", "summary_info")
    workflow.add_edge("summary_info", "generate_summary")
    workflow.add_edge("generate_summary", "create_visualizations")
    workflow.add_edge("create_visualizations", "generate_anomalies")
    workflow.add_edge("generate_anomalies", "generate_narrative")
    workflow.add_edge("generate_narrative", "generate_report")
    workflow.add_edge("generate_report", END)

    # Add state updates
    workflow.set_entry_point("validate_data")

    return workflow.compile()

### 4. Function to Run the Multi-Agent EDA ###
def run_eda(file_path):
    """Runs EDA using the multi-agent workflow."""
    try:
        # Load data directly into DataFrame
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON.")

        # Create initial state
        initial_state = EDAState(
            data=df,
            validation={},
            info={},
            summary={},
            anomalies={},
            visualizations={},
            report={},
            narrative=""
        )

        # Get the compiled workflow
        eda_executor = build_graph()

        # Run the workflow
        final_state = eda_executor.invoke(initial_state)

        # Return the report
        return final_state["report"]

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
