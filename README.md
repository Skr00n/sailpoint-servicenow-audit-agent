# SailPoint ServiceNow AI Audit Assistant

AI-powered audit assistant that analyzes **SailPoint Identity Governance** and **ServiceNow change management logs** using **LangChain, OpenAI, MySQL, and Streamlit**.

The application allows users to ask questions in **natural language** and automatically generate audit reports from enterprise audit data.

---

# What This Project Does

This tool helps security and identity teams analyze audit logs faster.

Instead of manually searching databases, users can ask questions like:

* Show Q1 imports
* Show CHG02 workflows
* Show imports in May
* Generate full report

The system converts the request into a **structured database query** and generates a report.

---

# Architecture

User Question
↓
LangChain LLM Parser (OpenAI)
↓
Command Detection
↓
MySQL Query
↓
Merged SailPoint + ServiceNow Audit Data
↓
Streamlit Dashboard + CSV Export

---

# Database Tables

### SailPoint Audit Table

| Column | Description        |
| ------ | ------------------ |
| action | Type of operation  |
| target | Workflow or object |
| source | System user        |
| date   | Audit timestamp    |

### ServiceNow Change Table

| Column       | Description               |
| ------------ | ------------------------- |
| target       | Workflow                  |
| changenumber | ServiceNow change request |
| importdate   | Date of change import     |

These tables are merged to produce unified audit reports.

---

# Features

AI Query Interface
Users can ask natural language questions.

Automated Report Generation
Combines SailPoint and ServiceNow records.

Smart Filtering

Supported filters include:

| Query | Result                  |
| ----- | ----------------------- |
| Q1    | January–March data      |
| Q2    | April–June data         |
| Q3    | July–September          |
| Q4    | October–December        |
| May   | Specific month          |
| CHG02 | Specific change request |

CSV Export
Generated reports can be downloaded directly.

---

# Tech Stack

Python
LangChain
OpenAI API
MySQL
Streamlit
Pandas

---

# Installation

Clone the repository

```
git clone https://github.com/Skr00n/sailpoint-servicenow-audit-agent.git
cd sailpoint-servicenow-audit-agent
```

Install dependencies

```
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file using the template.

```
cp .env.example .env
```

Fill in your credentials.

```
OPENAI_API_KEY=your_openai_api_key

MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=sailpoint_agent
```

---

# Run the Application

Start the Streamlit dashboard.

```
streamlit run streamlit_app.py
```

Open the browser:

```
http://localhost:8501
```

---

# Example Queries

show Q1 imports

show CHG02 workflows

show imports in May

generate full report

---

# Author

Ritvik Paruchuri
AI / Security Engineering Projects

GitHub:
https://github.com/Skr00n
