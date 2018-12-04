# The script exports the specified table from the specified database
# to the specified format (json, xml, csv, sql) to the specified
# location
import sqlite3
import argparse
import json
import sys
import os

# These are sqlite commands that export a table rows as csv format
csv_commands = '''sqlite3 {database} <<END_COMMANDS
.headers on
.mode csv
.output {path}
SELECT * FROM {table};
.quit
END_COMMANDS
'''

# These are sqlite commands that export a table rows as sql format
sql_commands = '''sqlite3 {database} <<END_COMMANDS
.output {path}
.dump {table}
.quit
END_COMMANDS'''


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", type=str, help="specifies the database")
parser.add_argument("-t", "--table", type=str, help="specifies the table to be exported")
parser.add_argument("-f", "--format", type=str, choices=["xml", "json", "csv", "sql"], help="specifies the export format")
parser.add_argument("-p", "--path", type=str, help="specifies the location of the export file")
args = parser.parse_args()
print(args)

try:
    conn = sqlite3.connect(args.database)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute("SELECT * FROM {}".format(args.table)).fetchall()
    conn.commit()
    conn.close()
except:
    print("Failed to retrieve rows from {}/{}".format(args.database, args.table))
    sys.exit(1)

if (args.format == 'json'):
    with open(args.path, "w+") as f:
        f.write(json.dumps([dict(ix) for ix in rows]))
        
elif (args.format == 'xml'):
    DEFAULT_DATETIME = '1990-01-01T00:00:00'
    BASE_INDENT = "  "
    with open(args.path, "w+") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write('<codeListing xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n')
        for row in rows:
            row_dict = dict(row)
            f.write('{indent}<code>\n'.format(indent=BASE_INDENT))
            f.write('{indent}<locks>{value}</locks>\n'.format(indent=BASE_INDENT*2, value=row["locknums"]))
            f.write('{indent}<code1>{value}</code1>\n'.format(indent=BASE_INDENT*2, value=row["code1"]))
            f.write('{indent}<code2>{value}</code2>\n'.format(indent=BASE_INDENT*2, value=row["code2"]))
            f.write('{indent}<username>{value}</username>\n'.format(indent=BASE_INDENT*2, value=row["description"]))
            f.write('{indent}<question1>{value}</question1>\n'.format(indent=BASE_INDENT*2, value=row["question1"]))
            f.write('{indent}<question2>{value}</question2>\n'.format(indent=BASE_INDENT*2, value=row["question2"]))
            f.write('{indent}<question3>{value}</question3>\n'.format(indent=BASE_INDENT*2, value=row["question3"]))
            f.write('{indent}<startDT>{value}</startDT>\n'.format(indent=BASE_INDENT*2, value=row["starttime"]))
            f.write('{indent}<endDT>{value}</endDT>\n'.format(indent=BASE_INDENT*2, value=row["endtime"]))
            f.write('{indent}<accesstype>{value}</accesstype>\n'.format(indent=BASE_INDENT*2, value=row["access_type"]))
            f.write('{indent}</code>\n'.format(indent=BASE_INDENT))
        f.write('</codeListing>')

elif (args.format == 'csv'):
    os.system(csv_commands.format(database=args.database, path=args.path, table=args.table))

elif (args.format == 'sql'):
    os.system(sql_commands.format(database=args.database, path=args.path, table=args.table))

#--------------------------------------------------------------------------------------------------
# EOF