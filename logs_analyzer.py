#!/usr/bin/env python
import psycopg2
from datetime import datetime

# Connect to the DB and get a cursor
connection = psycopg2.connect("dbname=news")
cursor = connection.cursor()

# 1) Query to get the 3 most popular articles of all time
cursor.execute("""
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
    ORDER BY SUB2.num DESC;
""")
article_results = cursor.fetchall()

# 2) Query to get the most popular authors with their total views
cursor.execute("""
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
author_results = cursor.fetchall()

# 3) Query to find out on which day > 1% of requests led to errors
cursor.execute("""
    SELECT time::DATE, status, count(*) AS num_requests
    FROM log GROUP BY time::DATE,status;
""")
log_results = cursor.fetchall()

# Close the connection
connection.close()

# Print the results
print "================================================="
print "1) Most popular 3 articles of all time:"
print "================================================="
for result in article_results:
    title, views = result[0], result[1]
    print "\"%s\" - %s views" % (title, views)

print "================================================="
print "\n"
print "================================================="
print "2) Most popular authors:"
print "================================================="
for result in author_results:
    author, views = result[0], result[1]
    print "%s - %s views" % (author, views)

print "================================================="
print "\n"
print "================================================="
print "3) Days on which > 1% of requests led to errors:"
print "================================================="
total = {}
bad = {}
dates = []
for result in log_results:
    date, status, num_requests = result[0], result[1], result[2]
    if str(date) not in dates:
        dates.append(str(date))
    if '200' not in status:
        bad[str(date)] = int(num_requests)
    if str(date) not in total:
        total[str(date)] = int(num_requests)
    else:
        total[str(date)] += int(num_requests)

for single_date in dates:
    percentage = 100 * float(bad[single_date])/float(total[single_date])
    if percentage > 1:
        datestring = datetime.strptime(single_date, "%Y-%m-%d")
        datestring = datestring.date().strftime("%B %d, %Y")
        print "%s - %.2f%% errors" % (datestring, percentage)
print "================================================="
