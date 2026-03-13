import mysql.connector
import csv

from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline


# --------------------------------
# Database Config
# --------------------------------

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "password",
    "database": "sailpoint_agent",
    "auth_plugin": "caching_sha2_password"
}


# --------------------------------
# HuggingFace Model
# --------------------------------

hf = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    max_new_tokens=200,
    temperature=0
)

model = HuggingFacePipeline(pipeline=hf)


# --------------------------------
# Generate SQL
# --------------------------------

def generate_sql(question):

    prompt = f"""
You are a SQL expert.

Database tables:

sailpoint_audit(action,target,source,date)
svn_audit_change(target,changenumber,importdate)

Write a SQL query to answer the question.

Question: {question}

SQL:
"""

    response = model.invoke(prompt)

    sql = response.split("SQL:")[-1].strip()

    return sql


# --------------------------------
# Execute Query
# --------------------------------

def run_query(sql_query):

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute(sql_query)

    rows = cursor.fetchall()

    filename = "AI_Audit_Report.csv"

    with open(filename,"w",newline="") as f:

        writer = csv.writer(f)

        writer.writerow([i[0] for i in cursor.description])
        writer.writerows(rows)

    cursor.close()
    conn.close()

    return filename


# --------------------------------
# CLI
# --------------------------------

def main():

    print("\nAI Audit Assistant (HuggingFace)\n")

    while True:

        question = input("You: ")

        if question.lower() == "exit":
            break

        sql_query = generate_sql(question)

        print("\nGenerated SQL:")
        print(sql_query)

        file = run_query(sql_query)

        print(f"\nReport saved to {file}\n")


if __name__ == "__main__":
    main()