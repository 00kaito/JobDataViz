# Overview

This is a comprehensive Polish job market analysis dashboard built with Dash and Plotly. The application processes job offer data to provide interactive visualizations and insights about skills demand, salary trends, location analysis, and market patterns. It features a multi-tab interface covering skills analysis, experience levels, geographic distribution, company analysis, market trends, salary analysis, and detailed skill-specific breakdowns.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Dash with Bootstrap styling for responsive design
- **UI Components**: Multi-tab layout using Dash Bootstrap Components (dbc)
- **Styling**: Custom CSS with dark theme support and Font Awesome icons
- **Data Storage**: Client-side stores for job data and filtered datasets using dcc.Store
- **File Upload**: Built-in Dash upload component for CSV/Excel data ingestion

## Backend Architecture
- **Main Application**: Flask-based Dash server running on port 5000
- **Data Processing**: Modular design with separate DataProcessor class
- **Visualization Engine**: ChartGenerator class for creating Plotly charts
- **Data Flow**: Upload → Process → Store → Visualize pattern

## Core Data Processing
- **Skills Analysis**: Counter-based skill frequency tracking with level weighting
- **Skill Combinations**: Analysis of commonly paired skills
- **Statistical Calculations**: Weighted scoring system for skill importance
- **Data Transformation**: Pandas-based data manipulation and aggregation

## Visualization System
- **Chart Library**: Plotly Express and Graph Objects for interactive charts
- **Chart Types**: Bar charts, scatter plots, heatmaps, line charts, histograms
- **Color Scheme**: Consistent color palette using Plotly's Set3 qualitative colors
- **Interactivity**: Responsive charts with hover effects and zoom capabilities

## Application Structure
- **Modular Design**: Separation of concerns with dedicated modules for processing and visualization
- **State Management**: Dash callback system for reactive updates
- **Error Handling**: Logging configuration for debugging and monitoring
- **Responsive Layout**: Bootstrap grid system for mobile-friendly design

# External Dependencies

## Core Libraries
- **Dash**: Web application framework for Python analytics
- **Plotly**: Interactive visualization library for charts and graphs
- **Pandas**: Data manipulation and analysis library
- **NumPy**: Numerical computing support

## UI Libraries
- **Dash Bootstrap Components**: Bootstrap integration for Dash
- **Bootstrap Agent Dark Theme**: Custom dark theme CSS from Replit CDN
- **Font Awesome**: Icon library for enhanced UI elements

## Data Processing
- **Collections**: Python standard library for Counter and data structures
- **DateTime**: Time-based data processing and analysis
- **JSON**: Data serialization and configuration handling
- **Base64/IO**: File upload and processing utilities

## Development Dependencies
- **Logging**: Python standard library for application monitoring
- **OS**: System-level operations and environment variables

Note: The application is designed to work with structured job market data containing skills, experience levels, locations, companies, and salary information in CSV or Excel format.