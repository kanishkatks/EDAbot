# EDA (Exploratory Data Analysis) Tool

Welcome to the **Exploratory Data Analysis Tool**! This project aims to simplify the process of data analysis by automating and visualizing essential statistics, making it easy for data scientists and analysts to quickly interpret their datasets. The tool uses a multi-agent system powered by LangGraph and integrates with a **React** frontend for a seamless user experience.

### Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Frontend Development](#frontend-development)
4. [Backend Development](#backend-development)
5. [Key Features](#key-features)
6. [Detailed Steps Taken](#detailed-steps-taken)

---

## Project Overview

This tool was built to automate the **Exploratory Data Analysis (EDA)** process. It allows users to upload CSV or JSON data, which is processed and analyzed by the backend (using FastAPI). The system generates both **static and interactive reports**, helping users identify key patterns, correlations, and potential issues in their datasets. The reports are accompanied by visualizations like histograms, boxplots, and QQ plots.

---

## Tech Stack

- **Frontend**: React with TypeScript
- **Backend**: FastAPI, Python
- **Visualization**: Pandas, Seaborn, Plotly, Matplotlib
- **Reports**: Jinja2 (for report templates)
- **Multi-Agent System**: LangGraph (to handle complex data analysis tasks)

---

## Frontend Development

The frontend was designed to be intuitive and easy to navigate, focusing on usability and visual appeal. The following features were implemented:

- **File Upload**: Users can upload CSV or JSON files for processing.
- **Tabs for Numerical Variables**: Each tab corresponds to a numerical variable. The user can select any tab to view the associated plots.
- **Plot Grid for Each Variable**: For each variable, the user is shown three types of plots—Histogram, Boxplot, and QQ Plot—arranged in a grid layout for easy comparison.
- **Heatmap Tab**: A dedicated tab displays a correlation heatmap to help users visualize correlations across numerical variables.

The frontend is built using **React** with TypeScript to ensure scalability and type safety. We've also incorporated CSS frameworks to make the layout responsive and easy to maintain.

---

## Backend Development

The backend handles all the data processing and analysis tasks. Here's how it works:

1. **Data Upload**: Users can upload their datasets (CSV/JSON format). This data is received and validated in the FastAPI backend.
2. **Data Processing & Multi-Agent System**: The backend analyzes the data using various libraries like Pandas, Scikit-learn, and Seaborn. The multi-agent system orchestrated by LangGraph automates the analysis of missing values, outliers, and other statistics.
3. **Plot Generation**: For each numerical variable, the backend generates three types of plots:
    - **Histograms**
    - **Boxplots**
    - **QQ Plots**
4. **Reports**: The backend generates reports in various formats:
    - **Interactive reports**: Using Plotly or Dash to show data visualizations.
    - **Static reports**: Markdown, HTML, or PDF reports containing the summary statistics, visualizations, and data insights.

These reports are then served to the frontend, which displays them to the user.

---

## Key Features

- **File Upload and Validation**: Upload CSV or JSON files, and the backend ensures proper data format and validation.
- **Exploratory Data Analysis (EDA)**:
  - **Summary statistics**: Automatically generates descriptive statistics (mean, std, min, max, etc.) for numerical columns.
  - **Data integrity checks**: Identifies missing values, duplicates, and anomalies.
  - **Visualization Generation**: Generates and serves visualizations like histograms, boxplots, QQ plots, and heatmaps.
- **Multi-Agent System**: LangGraph automates the decision-making and analysis process, ensuring that all data anomalies and insights are captured efficiently.
- **Downloadable Reports**: Both static and interactive reports are provided for easy viewing and sharing.

---

## Detailed Steps Taken

### 1. **Frontend Development**
   - **File Upload**: Created an upload interface where users can drag-and-drop CSV or JSON files.
   - **State Management**: Managed the state using React's Context API to store the file data and responses.
   - **Data Display**: Developed components to display summary statistics and visualizations in an organized and clean format:
     - **SummaryTab** for showing descriptive statistics.
     - **VisualizationsTab** for displaying generated plots (Histogram, Boxplot, QQ Plot) and the correlation heatmap.
     - Used a **Card-based layout** to present different data points and stats.
   - **Tabs for Numerical Variables**: Designed tabs for each numerical variable, enabling users to click through and view associated plots (histogram, boxplot, QQ plot).
   - **Grid Layout for Plots**: For each tab, organized the three plots into a grid layout, allowing users to compare the visualizations side by side.

### 2. **Backend Development**
   - **FastAPI Endpoints**: Set up multiple endpoints to handle the data analysis and plotting tasks:
     - **POST /upload**: Accepts the dataset and initiates the analysis.
     - **GET /summary**: Returns the summary statistics in a structured format.
     - **GET /visualizations**: Serves the path of generated images (plots) stored in a static folder.
   - **Data Analysis**:
     - Used **Pandas** for data manipulation (handling missing values, outliers).
     - Generated summary statistics using built-in Pandas functions.
     - Used **Seaborn** and **Matplotlib** to generate histograms, boxplots, and QQ plots.
     - Saved these visualizations as PNG files in a static directory for easy retrieval.

---
