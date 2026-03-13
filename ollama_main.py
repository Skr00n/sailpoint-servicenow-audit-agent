import mysql.connector
import csv
from langchain.agents import create_agent
from langchain_ollama import ChatOllama


# --------------------------------
# Database Config
# --------------------------------

DB_CONFIG = {
    "host": "127.0.0i8i8 9  .1",
    "user": "root",
    "password": "password",
    "database": "sailpoint_agent",
    "auth_plugin": "caching_sha2_password"
}


# --------------------------------
# Tool: SQL Query
# --------------------------------

def run_mysql_query(query: str) -> str:
    """Execute SQL query and export results to CSV."""

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()

    filename = "AI_Audit_Report.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([i[0] for i in cursor.description])
        writer.writerows(rows)

    cursor.close()
    conn.close()

    return f"Report saved to {filename}"


# --------------------------------
# Ollama Model
# --------------------------------

model = ChatOllama(
    model="llama3.2:3b",
    base_url="http://localhost:11434",
    temperature=0
)


# --------------------------------
# LangChain Agent
# --------------------------------

agent = create_agent(
    model=model,
    tools=[run_mysql_query],
    system_prompt="""
You are an enterprise audit assistant.

Database tables:

sailpoint_audit(action,target,source,date)
svn_audit_change(target,changenumber,importdate)

Generate SQL queries to answer user questions and call the tool.
"""
)


# --------------------------------
# CLI
# --------------------------------

def main():

    print("\nAI Audit Agent (Ollama)\n")

    while True:

        question = input("You: ")

        if question.lower() == "exit":
            break

        result = agent.invoke({
            "messages":[{"role":"user","content":question}]
        })

        print("\nAgent:")
        print(result["messages"][-1]["content"])
        print()


if __name__ == "__main__":
    main()