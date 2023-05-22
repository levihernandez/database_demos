import streamlit as st
import sqlite3

# Create a connection to the database
connection = sqlite3.connect("temp.db")

# Create a cursor
cursor = connection.cursor()

# Create a table
cursor.execute(
    "CREATE TABLE IF NOT EXISTS databases (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, host TEXT, port  TEXT, username  TEXT, password TEXT)")

# Create a title for the page
st.title("Database Information")
database_name = st.text_input("Enter the database name")
database_host = st.text_input("Enter the database host")
database_port = st.text_input("Enter the database port")
database_username = st.text_input("Enter the database username")
database_password = st.text_input("Enter the database password", type="password")

# Create a button to submit the information
submit_button = st.button("Submit")

# If the submit button is clicked, save the information to a file
if submit_button:
    with open("database_info.txt", "w") as f:
        f.write("Database Name: {}\n".format(database_name))
        f.write("Database Host: {}\n".format(database_host))
        f.write("Database Port: {}\n".format(database_port))
        f.write("Database Username: {}\n".format(database_username))
        f.write("Database Password: {}\n".format(database_password))
    # Insert data into the table
    cursor.execute(f"INSERT INTO databases (name, host, port, username, password) VALUES ('{database_name}', '{database_host}', '{database_port}', '{database_username}', '{database_password}')")
    # Commit the changes to the database
    connection.commit()

    # Close the connection
    connection.close()
    # Display a message to let the user know that the information has been saved
    st.success("Information saved!")
