# 🧠 EDAtool — Multi-Agent LLM-Powered Exploratory Data Analysis

From messy CSV files to clear, insightful reports in minutes.  
**EDAtool** is an intelligent, agentic pipeline that transforms raw datasets into dynamic EDA summaries using the power of LLMs and a multi-agent architecture.

## 🚀 Features

- 🔍 **Automated EDA Pipeline**: Get detailed summary statistics, data validation, and visualizations from your datasets
- 🤖 **Agentic Architecture**: Each stage of analysis is handled by dedicated agents (validation agent, visualization agent, narrative agent)
- 📊 **Visual Reports**: Generate HTML + downloadable PDF reports with summary text and Plotly visualizations
- 🌐 **React Frontend**: Intuitive UI to upload datasets, view EDA results, and chat with your data

## 🧱 How It Works 

```
       ┌─────────────┐       ┌────────────┐       ┌──────────────┐
       │ Upload CSV  │──────▶│   FastAPI  │──────▶│   LangGraph   │
       └─────────────┘       └────┬───────┘       └────┬─────────┘
                                  │                   ┌─▼────────────────┐
                                  │                   │ Multi-Agent LLM  │
                                  │                   ├──────────────────┤
                                  ▼                   │ 🧹 ValidationAgent│
                      🔍 Data Loaded                 │ 📈 StatsAgent     │
                                                      │ 📊 VizAgent       │
                                                      │ 🧠 NarrativeAgent │
                                                      └───────┬───────────┘
                                                              ▼
                                            ◀──── LLM-Powered Report
```

## 📋 Project Overview

EDAtool simplifies data analysis by automating and visualizing essential statistics, making it easy for data scientists and analysts to quickly interpret their datasets. The tool uses a multi-agent system powered by LangGraph and integrates with a React frontend for a seamless user experience.

Users can upload CSV, JSON, XLSX, or XLS files which are processed and analyzed by the backend. The system generates both static and interactive reports, helping users identify key patterns, correlations, and potential issues in their datasets. Reports include visualizations like histograms, boxplots, and QQ plots.

## 💻 Tech Stack

- **Frontend**: React with TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons
- **Backend**: FastAPI, Python
- **Visualization**: Pandas, Seaborn, Plotly, Matplotlib
- **Multi-Agent System**: LangGraph (to handle complex data analysis tasks)

## 🌐 Frontend Development

The frontend is designed to be intuitive and easy to navigate, focusing on usability and visual appeal:

### Key Features

- **File Upload**: Users can upload CSV, JSON, XLSX, or XLS files for processing
- **Tabbed Interface**: Clean, organized display of different data aspects
- **Interactive Visualizations**: Each numerical variable has dedicated visualizations
- **Responsive Design**: Built with Tailwind CSS for adaptability across devices

### Frontend Workflow

1. **File Upload**
   - Users can drag-and-drop or browse for supported files
   - `FileUpload.tsx` handles:
     - File validation (type & size)
     - Upload via `POST` request to `http://localhost:8000/upload`
     - Display of loading and status messages

2. **Report Retrieval**
   - Backend returns structured EDA JSON
   - JSON is passed to `ReportViewer.tsx`, triggering dynamic UI updates

3. **Report Display**
   - Rendered in a clean, tabbed interface:
     - 📄 **Narrative summary** (LLM Generated)
     - 📊 **Summary statistics** (row count, columns)
     - 🕳️ **Missing values** (with visual progress bars)
     - 📈 **Visualizations** (histograms, bar charts, etc.)
   - Each type of report content is separated into tabbed components

### File Structure

```
src/
├── components/
│   ├── FileUpload.tsx                      # Handles file input and upload logic
│   ├── ReportViewer.tsx                    # Renders the full EDA report view
│   ├── SummaryAndDistributionTab.tsx       # Tab for overview stats + narrative
│   └── ...more tabs
├── pages/
│   └── TestUpload.tsx                      # Page where upload and viewing happen
├── types/
│   └── types.ts                            # Contains the ReportData interface
```

## ⚙️ Backend Development

The backend handles all data processing and analysis tasks:

### Processing Pipeline

1. **Data Upload**: Files are received and validated by the FastAPI backend
2. **Data Processing & Multi-Agent System**: 
   - The backend analyzes the data using Pandas, Scikit-learn, and Seaborn
   - The LangGraph multi-agent system orchestrates:
     - Analysis of missing values and outliers
     - Generation of descriptive statistics
     - Creation of appropriate visualizations
     - Production of narrative insights

3. **Visualization Generation**: For each numerical variable, multiple visualizations are created:
   - Histograms for distribution analysis
   - Boxplots for outlier detection
   - QQ Plots for normality assessment
   - Correlation heatmaps for relationship identification

4. **Report Generation**: The backend creates:
   - Interactive reports using Plotly
   - Static reports in markdown, HTML, or PDF formats

## 🔑 Key Features

- **File Upload and Validation**: Support for multiple data formats with automatic validation
- **Comprehensive EDA**:
  - **Summary statistics**: Automatically generates descriptive statistics for numerical columns
  - **Data integrity checks**: Identifies missing values, duplicates, and anomalies
  - **Visualization Generation**: Creates appropriate visualizations based on data types
- **Multi-Agent Intelligence**: LangGraph automates the decision-making and analysis process


## 🛠️ Implementation Details

### Frontend Implementation
- **File Upload Interface**: Drag-and-drop functionality with progress indicators
- **State Management**: React Context API for storing file data and responses
- **Responsive Components**: 
  - SummaryTab for descriptive statistics
  - VisualizationsTab for displaying generated plots
  - Card-based layout for presenting data points and stats
- **Interactive Elements**: Tabbed interface with grid layouts for comparing visualizations

### Backend Implementation
- **FastAPI Endpoints**:
  - `POST /upload`: Accepts datasets and initiates analysis
  - `GET /summary`: Returns structured summary statistics
  - `GET /visualizations`: Serves generated visualizations
- **Data Analysis Pipeline**:
  - Pandas for data manipulation and handling missing values
  - Statistical analysis for outlier detection and correlation assessment
  - Visualization generation with Seaborn, Matplotlib, and Plotly


## 📝 Future ToDo List

### Enhanced Functionality
- **Interactive Data Cleaning**: Add agent-guided data cleaning suggestions and actions
- **Time Series Analysis**: Implement specialized agents for time series data detection and visualization
- **Categorical Data Analysis**: Expand capabilities for more comprehensive categorical variable handling

### Technical Improvements
- **Model Fine-tuning**: Train specialized models for improved domain-specific insights
- **Caching System**: Implement caching for faster repeat analysis of large datasets
- **Parallel Processing**: Optimize for multi-thread processing of large datasets

### User Experience
- **Custom Report Builder**: Allow users to select which analyses and visualizations to include in reports
- **Data Chat Interface**: Implement conversational interface for asking questions about the dataset
- **Insight Bookmarking**: Enable users to save and annotate important findings

### Infrastructure
- **Containerization**: Create Docker setup for easy deployment
- **API Documentation**: Complete OpenAPI documentation with examples
- **Testing Suite**: Implement comprehensive test coverage for all components

