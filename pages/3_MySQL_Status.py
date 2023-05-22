import mysql.connector
import streamlit as st
import traceback
from faker import Faker
import pandas as pd
import psutil
import ast


def get_system_info():
    # Get CPU usage as a percentage
    cpu_percent = psutil.cpu_percent()
    cpu_cores = psutil.cpu_count()

    # Get memory usage as a percentage
    memory_percent = psutil.virtual_memory().percent
    vmemory_mb = psutil.virtual_memory()

    # Get number of threads used by the current process
    num_threads = psutil.Process().num_threads()

    return cpu_percent, memory_percent, num_threads, cpu_cores, vmemory_mb


# Get system information
cpu_percent, memory_percent, num_threads, cpu_cores, vmemory_mb = get_system_info()

infra = {
    "CPU Used": cpu_percent,
    "CPU Cores": cpu_cores,
    "Num Threds": num_threads,
    "Mem Used": memory_percent
}

# Display system information in Streamlit app
st.write(infra)
st.write("Mem Stats", vmemory_mb)

# Define MySQL connection parameters
mysql_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '3306',
    'database': 'tododb'
}
checkmark = '\u2713'

# Define function to connect to MySQL and CockroachDB
# Define function to connect to MySQL and CockroachDB
def connect_to_databases():
    try:
        # Connect to MySQL and CockroachDB
        mysql_conn = mysql.connector.connect(
            user=mysql_config['user'],
            password=mysql_config['password'],
            host=mysql_config['host'],
            port=mysql_config['port'],
            database=mysql_config['database']
        )

        # Return the database connections
        return mysql_conn
    except Exception as e:
        st.error(f"Failed to connect to databases: {e}")
        st.error(traceback.format_exc())

if connect_to_databases():
    st.subheader("Count records created")
    mysql_conn = connect_to_databases()
    st.success(f"[{checkmark}]  MySQL Connection!")
    # Start with a fresh database
    with mysql_conn.cursor(buffered=True) as cursor:
        columns = ['table_name', 'table_rows', 'data_length', 'index_length']
        selec_columns = ",".join(columns)
        table_result = cursor.execute(f"""
            SELECT {selec_columns}
            FROM information_schema.tables
            WHERE table_schema = '{mysql_config['database']}';
        """)
        tables = pd.DataFrame(cursor.fetchall())
        tables = tables.reset_index(drop=True)
        tables.columns = columns

        st.table(tables)
    with mysql_conn.cursor() as cursor:
        # Execute the SQL statement
        cursor.execute("SHOW PROCESSLIST")

        # Get the results
        results = cursor.fetchall()

        # Create a table to display the results
        st.table(results)

