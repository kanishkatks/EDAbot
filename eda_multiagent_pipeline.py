import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional, Callable

# Ensure static directory exists for saving plots
os.makedirs("static", exist_ok=True)

### 1. Define State Model ###
class EDAState(BaseModel):
    """State for the EDA pipeline."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    data: Any = Field(description="The dataframe to analyze")
    validation: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    anomalies: Dict[str, Any] = Field(default_factory=dict)
    visualizations: Dict[str, Any] = Field(default_factory=dict)
    report: str = Field(default="")

### 2. Define Functions for Each Node ###
def validate_data(state: EDAState) -> EDAState:
    """Checks for missing values and duplicate rows."""
    df = state.data
    state.validation = {
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
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
    report = f"""
    Validation: {state.validation}
    Summary: {state.summary}
    Anomalies: {state.anomalies}
    Visualizations: {state.visualizations}
    """
    state.report = report
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
    
    # Define edges
    workflow.add_edge("validate_data", "generate_summary")
    workflow.add_edge("generate_summary", "create_visualizations")
    workflow.add_edge("create_visualizations", "generate_anomalies")
    workflow.add_edge("generate_anomalies", "generate_report")
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
            summary={},
            anomalies={},
            visualizations={},
            report=""
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
