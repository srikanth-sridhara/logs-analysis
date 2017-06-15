#!/usr/bin/env python
import psycopg2
from datetime import datetime


# Function that connects to the DB and executes a query
def connect_and_execute(query):
    try:
        # Connect to the DB and get a cursor
        connection = psycopg2.connect("dbname=news")
        # Get a cursor
        cursor = connection.cursor()
        # Execute the query
        cursor.execute(query)
        # Get the results
        results = cursor.fetchall()
        # Close the connection
        connection.close()
        return results
    except:
        print("ERROR in DB connection")
        return None


# 1) Query to get the 3 most popular articles of all time
article_results = connect_and_execute("""
    SELECT SUB1.title,SUB2.num FROM (
        SELECT title,'/article/' || slug AS path
        FROM articles
    ) SUB1 JOIN (
        SELECT path, count(*) as num
        FROM log
        WHERE path LIKE '%/article/%'
        GROUP BY path
        ORDER BY num DESC LIMIT 3
    ) SUB2
    ON SUB1.path = SUB2.path
    ORDER BY SUB2.num DESC
""")


# 2) Query to get the most popular authors with their total views
author_results = connect_and_execute("""
    SELECT name,sum(views) AS total FROM (
        SELECT authors.name,'/article/'|| articles.slug AS path FROM
        articles JOIN authors
        ON articles.author = authors.id
    ) SUB1 RIGHT JOIN (
        SELECT path, count(*) AS views FROM log
        WHERE path LIKE '%/article/%'
        GROUP BY path
    ) SUB2
    ON SUB1.path = SUB2.path
    WHERE name IS NOT NULL
    GROUP BY SUB1.name ORDER BY total DESC
""")


# 3) Query to find out on which day > 1% of requests led to errors
log_results = connect_and_execute("""
    SELECT * FROM (
        SELECT tbl1.time::DATE,
        round((100*tbl1.num_errors::decimal/tbl1.num_total),2)
        AS percentage FROM (
            SELECT time::DATE, count(*) AS num_total,
            sum(CASE WHEN status != '200 OK' THEN 1 ELSE 0 END)
            AS num_errors
            FROM log GROUP BY time::DATE
        ) AS tbl1
    ) AS tbl2
    WHERE percentage > 1
""")


# Print the results
print "================================================="
print "1) Most popular 3 articles of all time:"
print "================================================="
if article_results is not None:
    for result in article_results:
        title, views = result[0], result[1]
        print "\"%s\" - %s views" % (title, views)

print "================================================="
print "\n"
print "================================================="
print "2) Most popular authors:"
print "================================================="
if author_results is not None:
    for result in author_results:
        author, views = result[0], result[1]
        print "%s - %s views" % (author, views)

print "================================================="
print "\n"
print "================================================="
print "3) Days on which > 1% of requests led to errors:"
print "================================================="
if log_results is not None:
    for result in log_results:
        date, percentage = result[0], result[1]
        datestring = datetime.strptime(str(date), "%Y-%m-%d")
        datestring = datestring.date().strftime("%B %d, %Y")
        print "%s - %.2f%% errors" % (datestring, percentage)
print "================================================="
