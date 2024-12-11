# Issue: Reading the data

## Problem Description
- The data was not fetched properly from the database.
- The data should be displayed at the home page and after editing or adding a new recipe
- How was this issue discovered? After trying to open the page for testing the data was not showing up

## Root Cause Analysis
- The database connection was improperly closed
- What assumptions were incorrect? I assumed the tables name in schema was different from the one being used to display in app.py
- What dependencies were involved? The SQLite database schema, the index() route logic, and the index.html template.

## Resolution
- How was it fixed? (or planned fix if unresolved) Added the correct syntax to close the connection.
- What changes were made? Updated the index() route to ensure data was fetched and passed to the template.
- What alternatives were considered? Logging the database results directly to a log file for more persistent debugging

## Prevention
- How can similar issues be prevented?Write unit tests to validate the behavior of database fetching functions.
- What lessons were learned? Always validate the content of the database when debugging display issues.
- What warning signs should be watched for? Empty lists or none values in route handlers