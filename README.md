# Logs Analysis project.

Created by Srikanth Sridhara on 13th June 2017

This is a python script that connects to a DB and analyzes the logs.
It uses `psycopg2` library to connect to a `PostgreSQL` database.

## Important folders and files:

1. `logs_analyzer.py`:
    This is the main python file that connects to the database, performs queries and prints out the results.

2. `output.txt`:
    This file contains the output seen when the program is run.

## Usage:

To run this project, open `logs_analyzer.py`, having the 'news' database.

    python logs_analyzer.py

## Notes:

This project uses 3 SQL queries to answer 3 questions. No views were used:
*  Most popular 3 articles of all time
*  Most popular authors by views
*  Days on which > 1% of requests led to errors
