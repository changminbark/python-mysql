import requests
import os
import datetime
import csv

mysql_metrics = [
    # Connection Metrics
    "mysql_global_status_threads_connected",
    "mysql_global_status_max_used_connections",
    "mysql_global_variables_max_connections",

    # Query Throughput
    "mysql_global_status_questions",
    "mysql_global_status_queries",
    "mysql_global_status_com_select",
    "mysql_global_status_com_insert",
    "mysql_global_status_com_update",
    "mysql_global_status_com_delete",

    # Slow Queries
    "mysql_global_status_slow_queries",
    "mysql_global_variables_long_query_time",

    # InnoDB Buffer Pool
    "mysql_global_status_innodb_buffer_pool_reads",
    "mysql_global_status_innodb_buffer_pool_read_requests",
    "mysql_global_status_innodb_buffer_pool_pages_data",
    "mysql_global_status_innodb_buffer_pool_pages_free",

    # Thread & Locking
    "mysql_global_status_threads_running",
    "mysql_global_status_threads_created",
    "mysql_global_status_table_locks_waited",
    "mysql_global_status_table_locks_immediate",

    # Replication (optional, if using replicas)
    "mysql_slave_status_slave_io_running",
    "mysql_slave_status_slave_sql_running",
    "mysql_slave_status_seconds_behind_master",
]


def get_mysql_metrics():
    # Define URL for MySQLexporter
    url = "http://localhost:9104/metrics"
    resp = requests.get(url)
    metrics = {}

    for line in resp.text.splitlines():
        if line.startswith("#") or line.strip() == "":
            continue
        
        parts = line.split()
        metric_name = parts[0]
        value = parts[1] if len(parts) > 1 else None

        if metric_name in mysql_metrics and value is not None:
            try:
                value = float(value)
            except ValueError:
                pass
            
            metrics[metric_name] = value

    return metrics

if __name__ == "__main__":
    print(get_mysql_metrics())

