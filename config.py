import datetime

# Where should your production JSON files go for the widgets to find?
# jsonpath = "/var/www/html/misc/dorian/"
jsonpath = "/var/www/html/misc//20200729-isaias/"

# Do you want to start publishing JSON to your jsonpath?
WantJson = True

# What's the oldest your power widgets should go back? You can pick year, month, day, hour, minute
earliestdate = datetime.datetime(2020, 8, 1) # Filter by date

# What's the path to your Python executable?
# pythonpath = "/usr/bin/python3"
pythonpath = "/usr/bin/python3"

# What power scrapers do you want to run?
powerscripts = [
    "dukereport.py",
    "fplreport.py",
    "fplreport2.py"
#    "ncemcreport.py"
    ]
