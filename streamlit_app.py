import os
import csv
import pandas as pd
import mysql.connector
import streamlit as st

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# -----------------------------
# Load ENV
# -----------------------------

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "auth_plugin": "caching_sha2_password"
}


# -----------------------------
# LangChain Model
# -----------------------------

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

prompt = ChatPromptTemplate.from_template("""
You are an audit assistant.

Convert the user's request into one of these commands:

report
q1
q2
q3
q4
jan
feb
mar
apr
may
jun
jul
aug
sep
oct
nov
dec
chg01
chg02
chg03

Return ONLY the command.

User request:
{question}
""")

chain = prompt | model


# -----------------------------
# Report Generator
# -----------------------------

def generate_report(filter_type=None, value=None):

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
    SELECT
        sp.action,
        sp.target,
        sp.source,
        sp.date,
        sn.changenumber
    FROM sailpoint_audit sp
    LEFT JOIN svn_audit_change sn
        ON sp.target = sn.target
        AND sp.date = sn.importdate
    """

    params = ()

    if filter_type == "quarter":

        query += " WHERE MONTH(sp.date) BETWEEN %s AND %s"

        if value == 1:
            params = (1,3)
        elif value == 2:
            params = (4,6)
        elif value == 3:
            params = (7,9)
        else:
            params = (10,12)

    elif filter_type == "month":

        query += " WHERE MONTH(sp.date) = %s"
        params = (value,)

    elif filter_type == "change":

        query += " WHERE sn.changenumber = %s"
        params = (value,)

    cursor.execute(query, params)

    rows = cursor.fetchall()

    columns = ["action","target","source","date","changenumber"]

    df = pd.DataFrame(rows, columns=columns)

    cursor.close()
    conn.close()

    return df


# -----------------------------
# Command Parser
# -----------------------------

month_map = {
    "jan":1,"feb":2,"mar":3,
    "apr":4,"may":5,"jun":6,
    "jul":7,"aug":8,"sep":9,
    "oct":10,"nov":11,"dec":12
}


def process_command(cmd):

    cmd = cmd.lower()

    if cmd == "report":
        return generate_report()

    if cmd == "q1":
        return generate_report("quarter",1)

    if cmd == "q2":
        return generate_report("quarter",2)

    if cmd == "q3":
        return generate_report("quarter",3)

    if cmd == "q4":
        return generate_report("quarter",4)

    if cmd in month_map:
        return generate_report("month",month_map[cmd])

    if cmd.startswith("chg"):
        return generate_report("change",cmd.upper())

    return None


# -----------------------------
# Streamlit UI
# -----------------------------

st.title("AI Audit Assistant")

st.write("Ask a question about SailPoint / ServiceNow audit logs.")

question = st.text_input(
    "Example: show Q1 imports, show CHG02 workflows, show imports in May"
)

if st.button("Generate Report"):

    if question:

        result = chain.invoke({"question":question})
        cmd = result.content.strip()

        st.write(f"Detected command: **{cmd}**")

        df = process_command(cmd)

        if df is not None:

            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download CSV",
                csv,
                "audit_report.csv",
                "text/csv"
            )

        else:
            st.error("Could not understand request.")