# Instructions/How to Run
To run the MySQL docker container, FastAPI server, and mysqld-exporter, run
```bash
docker compose up -d --build # the -d runs it in detached mode
# OR
docker compose up -d --build ${service name} # rebuilds specific container
# OR
docker compose build --no-cache ${service name} # Force rebuild without using cache
docker compose up -d ${service name}
```

To stop the container, run
```bash
docker compose down
# OR
docker compose down -v # the -v will remove the named volumes (wipe data)
# OR
docker compose down ${service name} # stops specific container
```
 
We can also reattach or see the logs of a docker container using
```bash
# Logging
docker logs ${container_name}
# OR
docker logs -f ${container_name} # livestreaming logs
# OR
docker compose logs -f # logs for all containers

# Attaching
docker exec -it fastapi-server bash # for running commands
# OR
docker attach ${container_name_or_id}
# IF YOU WANT TO DETACH AGAIN PRESS THE FOLLOWING KEY COMBO
# Ctrl + P, then Ctrl + Q
```

We can delete unused images using
```bash
docker image prune
```

To access MySQL, we can do one of the following:
```bash
mysql -h 127.0.0.1 -P 3306 -u root -p # from the host
```
OR
```bash
sudo docker exec -it mysql-db mysql -u root -p  
```

## Docker-compose Notes
The docker-compose.yml file will create
- root user (MYSQL_ROOT_PASSWORD)
- database (MYSQL_DATABASE)
- user (MYSQL_USER / MYSQL_PASSWORD)
when it first runs (/var/lib/mysql is empty)
Then it will run
```sql
CREATE USER 'taskuser'@'%' IDENTIFIED BY 'taskpass';
GRANT ALL PRIVILEGES ON `tasks`.* TO 'taskuser'@'%';
```

You need to manually grant other privileges, such as 
```sql
-- Global privileges (can use these queries on any schema/db and table is mysql server)
GRANT PROCESS, SELECT, REPLICATION CLIENT ON *.* TO 'taskuser'@'%';

-- THE FOLLOWING IS RELEVANT FOR QUERYING SYS IN DOCKER CONTAINERS
-- For recreating the sys.statement_analysis, run
SHOW CREATE VIEW sys.statement_analysis\G
-- Then using this output, recreate the view
DROP VIEW IF EXISTS sys.statement_analysis;
CREATE ALGORITHM=MERGE
SQL SECURITY INVOKER
VIEW sys.statement_analysis (
  query, db, full_scan, exec_count, err_count, warn_count,
  total_latency, max_latency, avg_latency, lock_latency, cpu_latency,
  rows_sent, rows_sent_avg, rows_examined, rows_examined_avg,
  rows_affected, rows_affected_avg, tmp_tables, tmp_disk_tables,
  rows_sorted, sort_merge_passes, max_controlled_memory, max_total_memory,
  digest, first_seen, last_seen
) AS
SELECT
  sys.format_statement(ps.DIGEST_TEXT) AS query,
  ps.SCHEMA_NAME AS db,
  IF((ps.SUM_NO_GOOD_INDEX_USED > 0 OR ps.SUM_NO_INDEX_USED > 0), '*', '') AS full_scan,
  ps.COUNT_STAR AS exec_count,
  ps.SUM_ERRORS AS err_count,
  ps.SUM_WARNINGS AS warn_count,
  format_pico_time(ps.SUM_TIMER_WAIT) AS total_latency,
  format_pico_time(ps.MAX_TIMER_WAIT) AS max_latency,
  format_pico_time(ps.AVG_TIMER_WAIT) AS avg_latency,
  format_pico_time(ps.SUM_LOCK_TIME) AS lock_latency,
  format_pico_time(ps.SUM_CPU_TIME) AS cpu_latency,
  ps.SUM_ROWS_SENT AS rows_sent,
  ROUND(IFNULL(ps.SUM_ROWS_SENT / NULLIF(ps.COUNT_STAR, 0), 0), 0) AS rows_sent_avg,
  ps.SUM_ROWS_EXAMINED AS rows_examined,
  ROUND(IFNULL(ps.SUM_ROWS_EXAMINED / NULLIF(ps.COUNT_STAR, 0), 0), 0) AS rows_examined_avg,
  ps.SUM_ROWS_AFFECTED AS rows_affected,
  ROUND(IFNULL(ps.SUM_ROWS_AFFECTED / NULLIF(ps.COUNT_STAR, 0), 0), 0) AS rows_affected_avg,
  ps.SUM_CREATED_TMP_TABLES AS tmp_tables,
  ps.SUM_CREATED_TMP_DISK_TABLES AS tmp_disk_tables,
  ps.SUM_SORT_ROWS AS rows_sorted,
  ps.SUM_SORT_MERGE_PASSES AS sort_merge_passes,
  format_bytes(ps.MAX_CONTROLLED_MEMORY) AS max_controlled_memory,
  format_bytes(ps.MAX_TOTAL_MEMORY) AS max_total_memory,
  ps.DIGEST AS digest,
  ps.FIRST_SEEN AS first_seen,
  ps.LAST_SEEN AS last_seen
FROM performance_schema.events_statements_summary_by_digest AS ps
ORDER BY ps.SUM_TIMER_WAIT DESC;
-- Grant necessary privileges
GRANT SELECT, SHOW VIEW ON performance_schema.* TO 'taskuser'@'%';
GRANT EXECUTE ON sys.* TO 'taskuser'@'%';
```

These global privileges should be enough to access the following schemas:
- INFORMATION_SCHEMA: set of views that provide metadata about database system 
- PERFORMANCE_SCHEMA (mostly): set of views that monitor and capture performance metrics
- mysql schema (read_only portions): MySQL system schema that is needed for MySQL to run
- sys schema: set of views built on INFORMATION_SCHEMA and PERFORMANCE_SCHEMA

Note: 
- INFORMATION_SCHEMA and mysql schema have different purposes. INFORMATION_SCHEMA is used to show metadata about databases, tables, columns, users, privileges, processes, etc, while mysql provides core internal configuration and access control of the MySQL server like user accounts, passwords, privileges, server config, time zones, etc. 
- INFORMATION_SCHEMA and PERFORMANCE_SCHEMA are virtual views (no actual stored data) while mysql schema has actual system tables.
- INFORMATION_SCHEMA and PERFORMANCE_SCHEMA cannot be modified (read-only views) while mysql schema can be modified with admin privileges.
- INFORMATION_SCHEMA and PERFORMANCE_SCHEMA are used for monitoring and introspection while mysql schema is used for authentication, privilege enforcement, and server state.

# Python Notes:
Before Python 3, we used to need `__init__.py` for defining a package, but this is no longer needed (though it is recommended).

Python automatically includes the root directory of the project into sys.path, which is how it detects packages/modules (also includes other libraries/pip packages).

That's why we can use
```python
from app import models
from app.db import engine
```
as Python treats app as a top level package.

## Running python as a script
Running 
```python
python app/main.py
```
is running a program like a script. The file is assigned 
```python
__name__ == "__main__"
```
sys.path[0] becomes the directory containing the script, i.e. app/.
Imports are relative to that path — app is NOT on sys.path, so this fails:
```python
from app import models  # ImportError
```
## Running python as a module
Running
```python
python -m app/main.py
```
is running a program like a module. Python runs main.py as part of the app package. The file is still assigned:
```python
__name__ == "__main__"
```
However, sys.path[0] becomes the directory containing the app/ folder, i.e. your project root.
app is now a top-level package, so:
```python
from app import models  # Works
from . import db        # Relative import also works
```

## Yield
In Python, yield is used to turn a function into a generator. Instead of returning a value and ending the function, yield pauses the function and saves its state, allowing it to resume later.

# MySQL/SQL Notes:
To list all databases, we can use
```sql
SHOW DATABASES;
```

To list all tables in a database, we can use
```sql
USE mydatabase;
SHOW TABLES;
```

To list all the columns in MySQL (not SQL Server), we can use 
```sql
DESCRIBE name_of_table;
-- OR
SHOW COLUMNS FROM table_name;
```

To list all the columns in SQL Server, we can use
```sql
SELECT COLUMN_NAME
FROM information_schema.columns
WHERE table_name = 'tableName';
```

Find users in the server
```sql
SELECT User, Host FROM mysql.user;
```

Check privileges of users
```sql
-- As any user
SHOW GRANTS FOR CURRENT_USER; 
SHOW GRANTS FOR 'username'@'host';

-- As root
SELECT * FROM mysql.user WHERE User = 'taskuser' AND Host = '%';
```

Make sure to grant privileges to the user
```sql
GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO 'your_user'@'%';
```

Note: 
- SELECT Privilege allows you to read data from tables, (system) views, and read-only metadata tables.
- PROCESS Privilege allows you to view all active threads, query text of other users' queries, and query certain tables in performance_schema and sys
- REPLICATION CLIENT Privilege allows you to run `SHOW MASTER STATUS`. `SHOW SLAVE STATUS`, and query `performance_schema.replication_*` tables

[Other privileges](https://dev.mysql.com/doc/refman/8.4/en/privileges-provided.html)

## Privileges Example
```
mysql> SHOW GRANTS FOR 'taskuser'@'%';
+--------------------------------------------------------------------+
| Grants for taskuser@%                                              |
+--------------------------------------------------------------------+
| GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO `taskuser`@`%` |
| GRANT ALL PRIVILEGES ON `tasks`.* TO `taskuser`@`%`                |
+--------------------------------------------------------------------+
```
GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO 'taskuser'@'%'
This gives global privileges (on all databases, indicated by *.*):
- SELECT: Can read from any table in any database.
- PROCESS: Can see all threads in SHOW PROCESSLIST and query performance_schema process-related tables.
- REPLICATION CLIENT: Can run SHOW MASTER STATUS, SHOW SLAVE STATUS, and similar replication-related queries (read-only).

GRANT ALL PRIVILEGES ON 'tasks'.* TO 'taskuser'@'%'
Grants full privileges (like SELECT, INSERT, UPDATE, DELETE, etc.) on all tables in the tasks database only.
These privileges don't apply to other databases like mysql, information_schema, etc.

## Different types of replication
1. Classic Asynchronouse Replication
2. Semi-Synchronous Replication
3. MySQL Group Replication
4. MySQL InnoDB Cluster
5. NDB Cluster

## Failure detection in replication
We can detect failures in a group of nodes by sending out heartbeats between nodes and seeing how long it takes for them to hear back from the primary/leader node. This is done automatically in MySQL with Group Replication and InnoDB Clusters (which are built on top of Group Replication). 

We can set the MySQL Group Replication configurations, such as the timeouts using this command on ALL nodes:
```sql
-- On all nodes
SET GLOBAL group_replication_member_expel_timeout = 5000; -- 5 seconds
SET GLOBAL group_replication_unreachable_majority_timeout = 5000;
```

We can also manually query this replication information using
```sql
SELECT * FROM performance_schema.replication_group_members;
```
where performance_schema is a system database that contains system schemas/tables related to database performance.

[INFORMATION_SCHEMA](https://dev.mysql.com/doc/refman/8.4/en/information-schema.html)
[PERFORMANCE_SCHEMA](https://dev.mysql.com/doc/refman/8.4/en/performance-schema.html)
[SYS_SCHEMA](https://dev.mysql.com/doc/refman/8.4/en/sys-schema.html)

## Showing table metadata
We can show a table's metadata, such as primary key constraint, using one of the following options:
1. Using SHOW KEYS to Find Primary Key
```sql
SHOW KEYS FROM table_name WHERE Key_name = 'PRIMARY';
```
2. Use information_schema
```sql
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'database_name'
AND TABLE_NAME = 'table_name'
AND CONSTRAINT_NAME = 'PRIMARY';
```
or
```sql
SELECT *
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = 'database_name'
AND TABLE_NAME = 'table_name';
```
3. Describe table
```sql
DESCRIBE table_name;
```
4. Show table structure
```sql
SHOW CREATE TABLE table_name;
```

## INFORMATION_SCHEMA

The information_schema is a virtual database in MySQL that provides metadata about your database system — i.e., it tells you about the structure, definitions, and status of the database objects, not the data itself.

The SELECT ... FROM INFORMATION_SCHEMA statement is intended as a more consistent way to provide access to the information provided by the various SHOW statements that MySQL supports (SHOW DATABASES, SHOW TABLES, and so forth).

For most INFORMATION_SCHEMA tables, each MySQL user has the right to access them, but can see only the rows in the tables that correspond to objects for which the user has the proper access privileges. In some cases (for example, the ROUTINE_DEFINITION column in the INFORMATION_SCHEMA ROUTINES table), users who have insufficient privileges see NULL. Some tables have different privilege requirements; for these, the requirements are mentioned in the applicable table descriptions. For example, InnoDB tables (tables with names that begin with INNODB_) require the PROCESS privilege. 

[Optimizing INFORMATION_SCHEMA queries](https://dev.mysql.com/doc/refman/8.0/en/information-schema-optimization.html)

## PERFORMANCE_SCHEMA

[Documentation](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-quick-start.html)

The Performance Schema provides a way to inspect internal execution of the server at runtime. It is implemented using the PERFORMANCE_SCHEMA storage engine and the performance_schema database. The Performance Schema focuses primarily on performance data. This differs from INFORMATION_SCHEMA, which serves for inspection of metadata. 

The Performance Schema monitors server events. An “event” is anything the server does that takes time and has been instrumented so that timing information can be collected. In general, an event could be a function call, a wait for the operating system, a stage of an SQL statement execution such as parsing or sorting, or an entire statement or group of statements. Event collection provides access to information about synchronization calls (such as for mutexes) file and table I/O, table locks, and so forth for the server and for several storage engines. 

Performance Schema events are specific to a given instance of the MySQL Server. Performance Schema tables are considered local to the server, and changes to them are not replicated or written to the binary log. 

Performance Schema configuration can be modified dynamically by updating tables in the performance_schema database through SQL statements. Configuration changes affect data collection immediately. 

Tables in the Performance Schema are in-memory tables that use no persistent on-disk storage. The contents are repopulated beginning at server startup and discarded at server shutdown. 

The Performance Schema is intended to provide access to useful information about server execution while having minimal impact on server performance.

It is easy to add new instrumentation points.

Instrumentation is versioned. If the instrumentation implementation changes, previously instrumented code continues to work. This benefits developers of third-party plugins because it is not necessary to upgrade each plugin to stay synchronized with the latest Performance Schema changes. 

The name of the performance_schema database is lowercase, as are the names of tables within it. Queries should specify the names in lowercase. 

To enable all instruments and consumers, we need to run the following commands:
```sql
UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES';
UPDATE performance_schema.setup_consumers SET ENABLED = 'YES';
```

To see what the server is doing at the moment, examine the events_waits_current table. It contains one row per thread showing each thread's most recent monitored event.

### Instruments and Consumers

Instruments are specific points in the MySQL server where performance data can be collected — such as function calls, file I/O operations, mutex usage, etc. They are like sensors/probes embedded in server code.

Each instrument has a name (like wait/io/file/sql/FRM or statement/sql/select) and a corresponding row in performance_schema.setup_instruments.

Some common instrument classes:
- wait/io/… – File or socket I/O
- wait/synch/… – Locks like mutexes and condition variables
- stage/… – Query execution stages
- statement/sql/… – SQL statement types

Example
```sql
UPDATE performance_schema.setup_instruments 
SET ENABLED = 'YES', TIMED = 'YES' 
WHERE NAME LIKE 'wait/io/file/%';
```

Consumers determine where the collected data from instruments is stored in the performance_schema.

Each row in performance_schema.setup_consumers enables/disables a target data destination (table).

Examples of consumers:
- events_statements_history
- events_waits_current
- events_stages_history

If a consumer is disabled, even if the instrument is enabled, no data is stored.

Example
```sql
UPDATE performance_schema.setup_consumers 
SET ENABLED = 'YES' 
WHERE NAME = 'events_statements_history';
```

### Tables in PERFORMANCE_SCHEMA

[Types of Tables in performance_schema](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-table-descriptions.html)

The history tables contain the same kind of rows as the current-events table but have more rows and show what the server has been doing “recently” rather than “currently.” The events_waits_history and events_waits_history_long tables contain the most recent 10 events per thread and most recent 10,000 events, respectively.

Summary tables provide aggregated information for all events over time.

Instance tables document what types of objects are instrumented. An instrumented object, when used by the server, produces an event. These tables provide event names and explanatory notes or status information. For example, the file_instances table lists instances of instruments for file I/O operations and their associated files.

Setup tables are used to configure and display monitoring characteristics. For example, setup_instruments lists the set of instruments for which events can be collected and shows which of them are enabled.

The Performance Schema uses collected events to update tables in the performance_schema database, which act as “consumers” of event information. The setup_consumers table lists the available consumers and which are enabled.

Specific Performance Schema features can be enabled at runtime to control which types of event collection occur. This can be done by modifying the setup tables in PERFORMANCE_SCHEMA.

### Start-up/Runtime configuration

[Configuration information](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-runtime-configuration.html)

We can modify what sort of metrics/instruments to collect by modifying the setup tables as stated in the Instruments and Consumers section.

If there are Performance Schema configuration changes that must be made at runtime using SQL statements and you would like these changes to take effect each time the server starts, put the statements in a file and start the server with the init_file system variable set to name the file. This strategy can also be useful if you have multiple monitoring configurations, each tailored to produce a different kind of monitoring, such as casual server health monitoring, incident investigation, application behavior troubleshooting, and so forth. Put the statements for each monitoring configuration into their own file and specify the appropriate file as the init_file value when you start the server. 

Filtering can be done at different stages of performance monitoring:
- **Pre-filtering**: This is done by modifying Performance Schema configuration so that only certain types of events are collected from producers, and collected events update only certain consumers. To do this, enable or disable instruments or consumers. Pre-filtering is done by the Performance Schema and has a global effect that applies to all users. 
- **Post-filtering**: This involves the use of WHERE clauses in queries that select information from Performance Schema tables, to specify which of the available events you want to see. Post-filtering is performed on a per-user basis because individual users select which of the available events are of interest. 

[Optimizing PERFORMANCE_SCHEMA queries](https://dev.mysql.com/doc/refman/8.0/en/performance-schema-optimization.html)

### Problem Diagnosis using PERFORMANCE_SCHEMA

[Methodologies/Documentation](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-examples.html)

1. Run the use case.

2. Using the Performance Schema tables, analyze the root cause of the performance problem. This analysis relies heavily on post-filtering.

3. For problem areas that are ruled out, disable the corresponding instruments. For example, if analysis shows that the issue is not related to file I/O in a particular storage engine, disable the file I/O instruments for that engine. Then truncate the history and summary tables to remove previously collected events.

4. Repeat the process at step 1. With each iteration, the Performance Schema output, particularly the events_waits_history_long table, contains less and less “noise” caused by nonsignificant instruments, and given that this table has a fixed size, contains more and more data relevant to the analysis of the problem at hand. With each iteration, investigation should lead closer and closer to the root cause of the problem, as the “signal/noise” ratio improves, making analysis easier.

5. Once a root cause of performance bottleneck is identified, take the appropriate corrective action, such as:

    - Tune the server parameters (cache sizes, memory, and so forth).

    - Tune a query by writing it differently,

    - Tune the database schema (tables, indexes, and so forth).

    - Tune the code (this applies to storage engine or server developers only). 

6. Start again at step 1, to see the effects of the changes on performance. 

The mutex_instances.LOCKED_BY_THREAD_ID and rwlock_instances.WRITE_LOCKED_BY_THREAD_ID columns are extremely important for investigating performance bottlenecks or deadlocks. 

### Restrictions on PERFORMANCE_SCHEMA

[Restrictions](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-restrictions.html)

## sys_schema (INFORMATION_SCHEMA/PERFORMANCE_SCHEMA in a digestible form)

[Documentation](https://dev.mysql.com/doc/refman/8.4/en/sys-schema.html)

MySQL 8.4 includes the sys schema, a set of objects that helps DBAs and developers interpret data collected by the Information Schema and Performance Schema. sys schema objects can be used for typical tuning and diagnosis use cases. Objects in this schema include:
- Views that summarize Performance Schema data into more easily understandable form.
- Stored procedures that perform operations such as Performance Schema configuration and generating diagnostic reports.
- Stored functions that query Performance Schema configuration and provide formatting services. 

sys schema objects have a DEFINER of 'mysql.sys'@'localhost'. Use of the dedicated mysql.sys account avoids problems that occur if a DBA renames or removes the root account. 

Note: There may be a problem accessing the sys schema inside a docker container because of the DEFINER rights/security of the sys schema.

[Workaround for this](#docker-compose-notes)

### Prerequisites for sys_schema

The PERFORMANCE_SCHEMA must be enabled. A user must also have the following privileges:
- SELECT on all sys tables and views
- EXECUTE on all sys stored procedures and functions
- INSERT and UPDATE for the sys_config table, if changes are to be made to it
- Additional privileges for certain sys schema stored procedures and functions, as noted in their descriptions (for example, the ps_setup_save() procedure) 
- SELECT on any Performance Schema tables accessed by sys schema objects, and UPDATE for any tables to be updated using sys schema objects
- PROCESS for the INFORMATION_SCHEMA INNODB_BUFFER_PAGE table 

We also need to enable the following PERFORMANCE_SCHEMA instruments and consumers to allow for full sys_schema capabilities:
- All wait instruments
- All stage instruments
- All statement instruments
- xxx_current and xxx_history_long consumers for all events 

Another way to do this:
```sql
CALL sys.ps_setup_enable_instrument('wait');
CALL sys.ps_setup_enable_instrument('stage');
CALL sys.ps_setup_enable_instrument('statement');
CALL sys.ps_setup_enable_consumer('current');
CALL sys.ps_setup_enable_consumer('history_long'); 
```

For many uses of the sys schema, the default Performance Schema is sufficient for data collection. Enabling all the instruments and consumers just mentioned has a performance impact, so it is preferable to enable only the additional configuration you need. Also, remember that if you enable additional configuration, you can easily restore the default configuration like this: 
```sql
CALL sys.ps_setup_reset_to_default(TRUE);
```

### Using the sys_schema

The sys schema contains many views that summarize Performance Schema tables in various ways. Most of these views come in pairs, such that one member of the pair has the same name as the other member, plus a x$ prefix. For example, the host_summary_by_file_io view summarizes file I/O grouped by host and displays latencies converted from picoseconds to more readable values (with units). The x$host_summary_by_file_io view summarizes the same data but displays unformatted picosecond latencies: 
```sql
SELECT * FROM sys.host_summary_by_file_io;
SELECT * FROM sys.x$host_summary_by_file_io;
```
The view without the x$ prefix is intended to provide output that is more user friendly and easier for humans to read. The view with the x$ prefix that displays the same values in raw form is intended more for use with other tools that perform their own processing on the data.

To examine sys schema object definitions, use the appropriate SHOW statement or INFORMATION_SCHEMA query. For example, to examine the definitions of the session view and format_bytes() function, use these statements: 
```sql
SHOW CREATE VIEW sys.session;
SHOW CREATE FUNCTION sys.format_bytes;
```

However, those statements display the definitions in relatively unformatted form. To view object definitions with more readable formatting, access the individual .sql files found under the scripts/sys_schema directory in MySQL source distributions. 

### Progress Reporting

The following sys schema views provide progress reporting for long-running transactions:
- processlist
- session
- x$processlist
- x$session

Assuming that the required instruments and consumers are enabled, the progress column of these views shows the percentage of work completed for stages that support progress reporting. 

Stage progress reporting requires that the events_stages_current consumer be enabled, as well as the instruments for which progress information is desired. Instruments for these stages currently support progress reporting: 
- stage/sql/Copying to tmp table
- stage/innodb/alter table (end)
- stage/innodb/alter table (flush)
- stage/innodb/alter table (insert)
- stage/innodb/alter table (log apply index)
- stage/innodb/alter table (log apply table)
- stage/innodb/alter table (merge sort)
- stage/innodb/alter table (read PK and internal sort)
- stage/innodb/buffer pool load

For stages that do not support estimated and completed work reporting, or if the required instruments or consumers are not enabled, the progress column is NULL. 

### sys_schema Object Reference

[Reference](https://dev.mysql.com/doc/refman/8.4/en/sys-schema-reference.html)

[Full list of objects](https://dev.mysql.com/doc/refman/8.4/en/sys-schema-object-index.html)

## mysql schema

[Documentation](https://dev.mysql.com/doc/refman/8.4/en/system-schema.html)

The mysql schema is the system schema. It contains tables that store information required by the MySQL server as it runs. A broad categorization is that the mysql schema contains data dictionary tables that store database object metadata, and system tables used for other operational purposes.

Tables in mysql schema:
- Data Dictionary: Contains metadata about database objects
    - Data dictionary tables are invisible. They cannot be read with SELECT, do not appear in the output of SHOW TABLES, are not listed in the INFORMATION_SCHEMA.TABLES table, and so forth. 
    - However, in most cases there are corresponding INFORMATION_SCHEMA tables that can be queried.
- Grant System: Contains grant information about user accounts and privileges held by them
    - The MySQL 8.4 grant tables are InnoDB (transactional) tables. Account-management statements are transactional and either succeed for all named users or roll back and have no effect if any error occurs. 
- Object Information System: Contains information about components, loadable functions, and server-side plugins
- Log Systems: Used for logging
    - Use the CSV storage engine
- Server-Side Help System: Contains server-side help information
- Time Zone System: Contains time zone information
- Replication System: Used to support replication
    - Uses InnoDB storage engine
- Optimizer System: Used for optimization
- Misc. System: Tables that do not fit in previous categories

## Misc. Notes

Tables and views are both database objects that store or present data, but they are fundamentally different.

Tables:
- Physical storage: Tables store data physically on disk.
- CRUD operations: You can INSERT, UPDATE, DELETE, and SELECT data.
- Schema definition: You define the structure (columns and data types), and then populate it with data.
- Persistent: Data remains until explicitly deleted.

Views:
- Virtual tables: Views are stored SQL queries, not data. They dynamically present data from one or more tables.
- No physical storage: Views do not store data themselves (unless it's a materialized view, which MySQL doesn't support natively).
- Read-only by default: Most views are read-only unless they meet certain criteria (e.g., no joins, no aggregates, etc.).
- Use cases: Simplify complex queries, restrict access to specific columns/rows, or abstract underlying schema.

