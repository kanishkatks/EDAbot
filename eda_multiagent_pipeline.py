import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from langchain.schema import Document
from langgraph.graph import StateGraph
from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel
from typing import Dict, Any

# Ensure static directory exists for saving plots
os.makedirs("static", exist_ok=True)

### 1. Define State Model ###
class EDAState(BaseModel):
    data: pd.DataFrame
    validation: Dict[str, Any] = {}
    summary: Dict[str, Any] = {}
    anomalies: Dict[str, Any] = {}
    visualizations: Dict[str, Any] = {}

### 2. Define Agents (Tools) ###

@tool
def load_data(file_path: str) -> EDAState:
    """Loads CSV or JSON file into a Pandas DataFrame."""
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON.")

        return EDAState(data=df)
    except Exception as e:
        raise ValueError(f"Failed to load data: {str(e)}")

@tool
def validate_data(state: EDAState) -> EDAState:
    """Checks for missing values and duplicate rows."""
    df = state.data
    state.validation = {
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
    }
    return state

@tool
def generate_summary(state: EDAState) -> EDAState:
    """Computes basic descriptive statistics."""
    df = state.data
    state.summary = df.describe().to_dict()
    return state

@tool
def create_visualizations(state: EDAState) -> EDAState:
    """Creates visualizations and saves them as images."""
    df = state.data
    num_cols = df.select_dtypes(include=["number"]).columns
    plot_paths = []

    # Ensure static directory exists
    os.makedirs("static", exist_ok=True)

    # Generate histograms
    for col in num_cols:
        plt.figure()
        sns.histplot(df[col], bins=20, kde=True)
        plt.title(f"Histogram of {col}")
        plot_path = f"static/{col}_hist.png"
        plt.savefig(plot_path)
        plt.close()
        plot_paths.append(plot_path)

    # Generate correlation heatmap
    if len(num_cols) > 1:  # Only create heatmap if multiple numeric columns exist
        plt.figure(figsize=(10, 6))
        sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Heatmap")
        heatmap_path = "static/correlation_heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()
        plot_paths.append(heatmap_path)

    # Generate boxplots for numerical columns
    for col in num_cols:
        plt.figure(figsize=(6, 4))
        sns.boxplot(y=df[col])
        plt.title(f"Boxplot of {col}")
        boxplot_path = f"static/{col}_boxplot.png"
        plt.savefig(boxplot_path)
        plt.close()
        plot_paths.append(boxplot_path)

    state.visualizations = {"plots": plot_paths}
    return state

@tool
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

@tool
def generate_report(state: EDAState) -> Dict[str, Any]:
    """Generates final EDA report combining all insights."""
    return {
        "validation": state.validation,
        "summary": state.summary,
        "anomalies": state.anomalies,
        "visualizations": state.visualizations,
    }

### 3. Build Multi-Agent Graph ###
eda_graph = StateGraph(EDAState)

eda_graph.add_node("load_data", load_data)
eda_graph.add_node("validate", validate_data)
eda_graph.add_node("summary", generate_summary)
eda_graph.add_node("visualizations", create_visualizations)
eda_graph.add_node("anomalies", detect_anomalies)
eda_graph.add_node("report", generate_report)

# Define workflow sequence
eda_graph.add_edge("load_data", "validate")
eda_graph.add_edge("validate", "summary")
eda_graph.add_edge("summary", "visualizations")
eda_graph.add_edge("visualizations", "anomalies")
eda_graph.add_edge("anomalies", "report")

# Set Entry and Exit points
eda_graph.set_entry_point("load_data")
eda_graph.add_conditional_edges("report", lambda state: None)  # End processing

eda_executor = eda_graph.compile()

### 4. Function to Run the Multi-Agent EDA ###
def run_eda(file_path):
    """Runs EDA using the multi-agent workflow."""
    initial_state = eda_executor.invoke(file_path)
    return generate_report(initial_state)
