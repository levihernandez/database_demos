import streamlit as st
import mysql.connector
import cockroachdb

# Get the MySQL database name from the user
mysql_database_name = st.text_input("MySQL database name:")
st.write(f"Selected `{mysql_database_name}`")
# Connect to the MySQL server
mysql_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root"
)

# Get the list of MySQL tables in the database
mysql_tables = mysql_connection.cursor().execute("SHOW TABLES IN {}".format(mysql_database_name)).fetchall()

# Connect to the CockroachDB server
cockroachdb_connection = cockroachdb.connect(
    host="localhost",
    port=26257,
    user="root",
    password="",
)

# Create a CockroachDB database for the MySQL database
cockroachdb_connection.execute("CREATE DATABASE {}".format(mysql_database_name))

# Create CockroachDB tables for the MySQL tables
for mysql_table in mysql_tables:
    table_name = mysql_table[0]
    columns = mysql_connection.cursor().execute("SHOW COLUMNS IN {}".format(table_name)).fetchall()
    cockroachdb_table_definition = "CREATE TABLE {} ( ".format(table_name)
    for column in columns:
        column_name = column[0]
        column_type = column[1]
        cockroachdb_table_definition += "{} {}, ".format(column_name, column_type)
    cockroachdb_table_definition = cockroachdb_table_definition[:-2] + " );"
    cockroachdb_connection.execute(cockroachdb_table_definition)

# Close the connections to the MySQL and CockroachDB servers
mysql_connection.close()
cockroachdb_connection.close()

# Print the DDL schema to the screen
st.code(cockroachdb_table_definition)
