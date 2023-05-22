import streamlit as st
import traceback
import pandas as pd
import psutil
import time
import mysql.connector
from faker import Faker
import sqlite3


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


fake = Faker()

# Define Streamlit app title
st.title("MySQL and CockroachDB Connection Form")

checkmark = '\u2713'
deletion = '\u2718'

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
mysql_conf = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '3306',
}

mysql_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '3306',
    'database': 'demodb'
}

configs = {
    'create_rows': '100',
    'batch_size': '10'
}

# Create a connection to the database
connection = sqlite3.connect("temp.db")

# Create a cursor
cursor = connection.cursor()

# Get the list of tables
dbs = cursor.execute("SELECT name FROM databases").fetchall()
db_array = []
for i in dbs:
    db_array.append(i[0])

# Create a dropdown
dbs_dropdown = st.selectbox("Select a database", db_array)

# If a table is selected, display the table data
if dbs_dropdown:
    dbs_name = dbs_dropdown  # .lower()

    # Get the table data
    cursor.execute(f"SELECT name, host, port, username, password  FROM databases WHERE name = '{dbs_name}'")
    dbs_data = cursor.fetchall()

    # Get the values of the selected record
    record_values = dbs_data[0]
    name = record_values[0]
    host = record_values[1]
    port = record_values[2]
    username = record_values[3]
    password = record_values[4]

    # Prefill the form inputs with the values of the selected record
    #st.text_input("Name", value=name)
    #st.text_input("Host", value=host)
    #st.text_input("Port", value=port)
    #st.text_input("Username", value=username)
    #st.text_input("Password", value=password)

    st.subheader("Seed Database")
    configs['create_rows'] = st.text_input('Seed Max Rows', value=configs['create_rows'])
    configs['batch_size'] = st.text_input('Batch Size', value=configs['batch_size'])
    # Display connection parameters
    st.subheader("MySQL Connection Information")
    mysql_config['name'] = st.text_input('MySQL Username', value=name)
    mysql_config['user'] = st.text_input('MySQL Username', value=username)
    mysql_config['password'] = st.text_input('MySQL Password', value=password, type='password')
    mysql_config['host'] = st.text_input('MySQL Host', value=host)
    mysql_config['port'] = st.text_input('MySQL Port', value=port)
    mysql_config['database'] = st.text_input('MySQL Database', value=mysql_config['database'])

# Close the connection
connection.close()


# Define function to connect to MySQL and CockroachDB
# Define function to connect to MySQL and CockroachDB
def connect_to_databases(action):
    try:
        if 'db-generate' in action:
            # Connect to MySQL and CockroachDB
            mysql_conn = mysql.connector.connect(
                user=mysql_config['user'],
                password=mysql_config['password'],
                host=mysql_config['host'],
                port=mysql_config['port'],
                database=mysql_config['database']
            )
        else:
            mysql_conn = mysql.connector.connect(
                user=mysql_config['user'],
                password=mysql_config['password'],
                host=mysql_config['host'],
                port=mysql_config['port']
            )

        # Return the database connections
        return mysql_conn
    except Exception as e:
        st.error(f"Failed to connect to databases: {e}")
        st.error(traceback.format_exc())


if st.button("Check Database"):
    action = 'db-exists'
    mysql_conn = connect_to_databases(action)
    # mysql_conn = connect_to_databases()
    # mysql_cursor = mysql_conn.cursor()
    st.success(f"[{checkmark}] Established MySQL Connection!")

    # Check if the database exists
    mysql_conn = connect_to_databases(action)
    with mysql_conn.cursor() as cursor:
        # cursor.execute(f"SHOW DATABASES LIKE '{mysql_config['database']}'")
        st.warning(f"Validating if {mysql_config['database']} exists, otherwise creating it now!")
        # If the database does not exist, create it
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_config['database']}")

        # Close the connection
        cursor.close()

# Create Streamlit button to connect to MySQL
if st.button("Generate Schema in MySQL"):
    action = 'db-generate'
    num_rows = configs['create_rows']
    sequence = f"""
      SELECT ones.num + 10*tens.num + 100*hundreds.num + 1000*thousands.num AS num
  FROM (SELECT 0 AS num UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) ones
  CROSS JOIN (SELECT 0 AS num UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) tens
  CROSS JOIN (SELECT 0 AS num UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) hundreds
  CROSS JOIN (SELECT 0 AS num UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) thousands
  WHERE ones.num + 10*tens.num + 100*hundreds.num + 1000*thousands.num BETWEEN 1 AND {num_rows}
  """
    # mysql_conn = connect_to_mysql()
    mysql_conn = connect_to_databases(action)
    # mysql_conn = connect_to_databases()
    # mysql_cursor = mysql_conn.cursor()
    st.success(f"[{checkmark}] Established MySQL Connection!")

    # Start with a fresh database
    with mysql_conn.cursor() as cursor:
        table_result = cursor.execute(f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{mysql_config['database']}';
        """)
        tables = cursor.fetchall()

        if tables is not None:
            for t in tables:
                st.error(f"[{deletion}] Deleting {t[0]} table")
                with mysql_conn.cursor() as c:
                    c.execute("TRUNCATE TABLE " + t[0])
                    c.execute("DROP TABLE IF EXISTS " + t[0] + " CASCADE")
                    st.success(f"[{checkmark}] Deleted {t[0]} table")

    with mysql_conn.cursor(buffered=True) as cursor:
        try:
            # List all stored procedures
            cursor.execute("SHOW PROCEDURE STATUS WHERE Db = %s", (mysql_config['database'],))
            procedures = cursor.fetchall()

            # Loop over procedures and drop them
            for procedure in procedures:
                st.error(f"[{deletion}] Deleting stored procedure `{procedure}` ")
                procedure_name = procedure[1]
                cursor.execute("DROP PROCEDURE IF EXISTS {}".format(procedure_name))
                for result in cursor.stored_results():
                    result.fetchall()
                    st.success(f"[{checkmark}] Deleted procedure: `{result}` ")

        except mysql.connector.errors.InternalError as e:
            # Handle unread result error
            if "Unread result found" in str(e):
                st.warning("No Procedures Found...", str(e))
                # Consume unread results
                for result in cursor.stored_results():
                    result.fetchall()
            else:
                raise e

    # Create 'users' table
    with mysql_conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT NOT NULL AUTO_INCREMENT,
                name VARCHAR(50),
                last VARCHAR(50),
                address VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(100),
                zip_code VARCHAR(50),
                country VARCHAR(100),
                login VARCHAR(50),
                email VARCHAR(50),
                PRIMARY KEY (id)
            )
        """)
        st.success(f"[{checkmark}]  Created `users` table!")

    # Insert records into 'users' table
    with mysql_conn.cursor() as cursor:
        # Number of records to insert
        users_to_insert = int(num_rows)
        batch_size = int(configs['batch_size'])
        st.warning(f" Inserting {users_to_insert} records into `users` table!")
        # Create a progress bar
        progress_bar = st.progress(0)

        # Create a timer
        start_time = time.time()

        # Create a progress counter
        progress_counter = st.empty()

        # Create a batch insert loop
        for i in range(users_to_insert // batch_size):
            # Get the current batch
            batch = []
            counter = 0
            for j in range(batch_size):
                counter = counter + 1
                batch.append({

                    "name": f"{fake.name()}",
                    "last": f"{fake.last_name()}",
                    "address": f"{fake.street_address()}",
                    "city": f"{fake.city()}",
                    "state": f"{fake.state()}",
                    "country": f"{fake.country()}",
                    "zip_code": f"{fake.postcode()}",
                    "login": f"{fake.user_name()}",
                    "email": f"{fake.email()}"
                })
            # Insert the batch into the database
            # cursor = mysql_conn.cursor()
            sql = """
            INSERT INTO users ( name, last, address, city, state, country, zip_code, login, email)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            percentage = int(((i+1) / (users_to_insert // batch_size)) * 100)
            progress_counter.text(f"{(i + 1) * batch_size} of {users_to_insert}")
            progress_bar.progress(percentage)
            for row in batch:
                # st.write(f"Inserting batch {len(batch)}")
                # st.write(f"{list(row.values())} JSON Payload")
                row_list = list(row.values())
                cursor.execute(sql, row_list)
            mysql_conn.commit()
        # Close the progress counter
        # progress_counter.empty()
        st.success(f"[{checkmark}]  Inserted {num_rows} records into `users` table!")
        # Get the end time
        end_time = time.time()
        # Calculate the total time
        total_time = end_time - start_time

        # Print the total time
        st.text(f"Total Insert Time in Seconds: {total_time}")
    # Create 'logins' table
    with mysql_conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logins (
                id INT PRIMARY KEY,
                user_id INT,
                login_time DATETIME
            );
        """)
        st.success(f"[{checkmark}]  Created `logins` table!")
    # Insert sample data into 'logins' table
    with mysql_conn.cursor() as cursor:
        cursor.execute(f"""
            INSERT INTO logins (id, user_id, login_time)
            SELECT num as id, FLOOR(RAND() * {num_rows}) + 1 as user_id, now() as login_time
            FROM (
            {sequence}
            ) AS nums;
        """)
        st.success(f"[{checkmark}]  Inserted {num_rows} records into `logins` table!")

    # Create 'login_counts' table
    with mysql_conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_counts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                count INT,
                timestamp DATETIME
            );
        """)
        st.success(f"[{checkmark}]  Created `login_counts` table!")

    # Create stored procedure to count logins in last 5 minutes and store results in 'login_counts' table
    with mysql_conn.cursor() as cursor:
        cursor.execute("""
            CREATE PROCEDURE count_logins()
            BEGIN
                DECLARE curr_time DATETIME;
                DECLARE start_time DATETIME;
                DECLARE login_count INT;
                SET curr_time = NOW();
                SET start_time = current_time - INTERVAL 5 MINUTE;
                SELECT COUNT(*) INTO login_count FROM logins WHERE login_time BETWEEN start_time AND current_time;
                INSERT INTO login_counts (count, timestamp) VALUES (login_count, curr_time);
            END;
        """)
        st.success(f"[{checkmark}]  Created `count_logins` store procedure!")

    # Call stored procedure to count logins
    with mysql_conn.cursor() as cursor:
        cursor.execute("CALL count_logins()")
        st.success(f"[{checkmark}]  Executed `count_logins` stored procedure!")
        st.success(f"[{checkmark}]  Inserted `count_logins` into `login_counts` table!")
    # Commit changes to database
    mysql_conn.commit()

    st.success("Successfully created tables, inserted data, and counted logins!")

    action = 'db-generate'
    st.subheader("Database Tables")
    mysql_conn = connect_to_databases(action)
    if connect_to_databases(action):
        st.success(f"[{checkmark}]  MySQL Connection!")
        # Start with a fresh database
        st.write("Database Tables")
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

        st.subheader("Sample Data")
        mysql_conn = connect_to_databases(action)
        st.success(f"[{checkmark}]  MySQL Connection!")
        with mysql_conn.cursor(buffered=True) as cursor:
            columns = ["id", "name", "last", "address", "city", "state", "zip_code", "country", "login", "email"]
            users_rs = cursor.execute(f"""SELECT * FROM users LIMIT 5""")
            users = pd.DataFrame(cursor.fetchall())
            users.columns = columns
            users = users.reset_index(drop=True)

            st.table(users)
