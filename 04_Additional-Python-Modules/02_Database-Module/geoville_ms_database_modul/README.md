**The GeoVille_MS_Database_Modul**

This modul acts as Geoville's Microservice PostgreSQL Database connector.

Author: Wolfgang Kapferer
Version 19.08.1
Date: 2019-08-12

---

## Short overview of all the methods

The provided methods are:

1. read_from_database_one_row -> reads one row from a query
2. read_from_database_all_rows -> reads all rows from a query
3. read_from_database_many_rows -> reads many (size) rows from a query
4. execute_database -> executes commands aigainst DM (insert, update, create, drop, delete, etc.)
5. execute_values_database -> fast batch method for insert, updates and delete


---

## Example calls

###result = database.read_from_database_one_row(sql, 'database.ini', 'postgresql', False)  
####This function is nice to read just one row
    :param sql: The string providing the query  
	:param filename: The Filename to the database.ini file  
	:param section: The section in the credentials files  
	:param autocommit: True...ON, False...Off  
	:return: A tuple with ONE item -> the result  
	
	
###read_from_database_all_rows(sql, filename, section, autocommit)   
####This function is nice to read more data   
    :param sql: The string providing the query  
    :param filename: The Filename to the database.ini file  
    :param section: The section in the credentials files  
    :param autocommit: True...ON, False...Off  
    :return: A tuple holding all the data  

###read_from_database_all_rows(sql, filename, section, autocommit):  
####This function is nice to read more data  
    :param sql: The string providing the query  
    :param filename: The Filename to the database.ini file  
    :param section: The section in the credentials files  
    :param autocommit: True...ON, False...Off 
    :return: A tuple holding all the data	 									
	
###read_from_database_many_rows(sql, size, filename, section, autocommit):  
####This function is nice to read more data  
    :param sql: The string providing the query  
    :param size: How many rows should be returned 
    :param filename: The Filename to the database.ini file  
    :param section: The section in the credentials files  
    :param autocommit: True...ON, False...Off  
    :return: A tuple holding all the data	 
	
	
###execute_database(sql, filename, section, autocommit):  
####This function executes a command against the DB 
    :param sql: The string providing the query 
    :param filename: The Filename to the database.ini file  
    :param section: The section in the credentials files  
    :param autocommit: True...ON, False...Off  
    :return: success	  
	
###execute_values_database(sql, param_list, filename, section, autocommit): 
####This function execute many onto the database (for updates, inserts, del operations)  
    :param sql: The string providing the query 
    :param param_list: The list to execute values 
    :param filename: The Filename to the database.ini file 
    :param section: The section in the credentials files 
    :param autocommit: True...ON, False...Off 
    :return: success	 
	
	
---
## Tests

All the test can be found in the test subdir in the src folder.

---

## Clone a repository

Use these steps to clone from SourceTree, our client for using the repository command-line free. Cloning allows you to work on your files locally. If you don't yet have SourceTree, [download and install first](https://www.sourcetreeapp.com/). If you prefer to clone from the command line, see [Clone a repository](https://confluence.atlassian.com/x/4whODQ).

1. You’ll see the clone button under the **Source** heading. Click that button.
2. Now click **Check out in SourceTree**. You may need to create a SourceTree account or log in.
3. When you see the **Clone New** dialog in SourceTree, update the destination path and name if you’d like to and then click **Clone**.
4. Open the directory you just created to see your repository’s files.

Now that you're more familiar with your Bitbucket repository, go ahead and add a new file locally. You can [push your change back to Bitbucket with SourceTree](https://confluence.atlassian.com/x/iqyBMg), or you can [add, commit,](https://confluence.atlassian.com/x/8QhODQ) and [push from the command line](https://confluence.atlassian.com/x/NQ0zDQ).