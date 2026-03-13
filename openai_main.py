import os
import csv
import mysql.connector

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --------------------------------
# Load env
# --------------------------------

load_dotenv()

# --------------------------------
# Database Config
# --------------------------------

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "auth_plugin": "caching_sha2_password"
}

# --------------------------------
# LangChain Model
# --------------------------------

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


# --------------------------------
# Generate Report
# --------------------------------

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

    filename = "Audit_Report_Response.csv"

    with open(filename,"w",newline="",encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "action",
            "target",
            "source",
            "date",
            "changenumber"
        ])

        writer.writerows(rows)

    cursor.close()
    conn.close()

    return filename


# --------------------------------
# Command Parser
# --------------------------------

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


# --------------------------------
# CLI
# --------------------------------

def main():

    print("\nLangChain Audit Assistant\n")

    print("Examples:")
    print(" show Q1 imports")
    print(" show CHG02 workflows")
    print(" show May imports")
    print(" generate full report")
    print(" exit\n")

    while True:

        question = input("You: ")

        if question.lower() == "exit":
            break

        result = chain.invoke({"question":question})

        cmd = result.content.strip()

        print(f"\nDetected command: {cmd}")

        file = process_command(cmd)

        if file:
            print(f"Report generated: {file}\n")
        else:
            print("Could not understand request\n")


if __name__ == "__main__":
    main()