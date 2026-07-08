/* @bruin
name: report.hourly_report
type: duckdb.sql
connection: duckdb-inmemory

hooks:
  pre:
    - query: "INSTALL quack"
    - query: "LOAD quack"
    - query: "ATTACH 'quack:quack.virdio.my.id:443' AS remote_db (TOKEN '{{ var.quack_token }}')"
  post:
    - query: "CREATE OR REPLACE TABLE remote_db.hourly_report AS SELECT * FROM report.hourly_report"

materialization:
  type: table
  strategy: create+replace

columns:
  - name: ts
    type: TIMESTAMP
    description: 'Hourly time ts'
  - name: avg_cpu_temp
    type: DOUBLE
    description: 'Average CPU temperature'
  - name: max_cpu_temp
    type: DOUBLE
    description: 'Max CPU temperature'
  - name: avg_mem_usage
    type: DOUBLE
    description: 'Average memory usage percentage'
  - name: min_mem_usage
    type: DOUBLE
    description: 'Min memory usage percentage'
  - name: avg_disk
    type: DOUBLE
    description: 'Average disk usage percentage'
  - name: avg_cpu_usage
    type: DOUBLE
    description: 'Average CPU usage percentage'
  - name: avg_cpu_volt
    type: DOUBLE
    description: 'Average CPU voltage'
  - name: uptime
    type: BIGINT
    description: 'Latest uptime in seconds'
  - name: rx
    type: BIGINT
    description: 'Max receive bytes'
  - name: tx
    type: BIGINT
    description: 'Max transmit bytes'
  - name: ingested_at
    type: TIMESTAMP
    description: 'Ingestion timestamp'
@bruin */

SELECT
    time_bucket(INTERVAL '1 hour', CAST(REPLACE(timestamp, 'Z', '') AS TIMESTAMP)) AS ts,
    ROUND(AVG(cpu_temp_c), 2) AS avg_cpu_temp,
    ROUND(MAX(cpu_temp_c), 2) AS max_cpu_temp,
    ROUND(AVG(memory_usage_pct), 2) AS avg_mem_usage,
    ROUND(MIN(memory_usage_pct), 2) AS min_mem_usage,
    ROUND(MAX(disk_usage_pct), 2) AS avg_disk,
    ROUND(AVG(cpu_usage_pct), 2) AS avg_cpu_usage,
    ROUND(AVG(cpu_volt_v), 2) AS avg_cpu_volt,
    CAST(MAX(uptime_seconds) AS BIGINT) AS uptime,
    MAX(rx_bps) AS rx,
    MAX(tx_bps) AS tx,
    CURRENT_TIMESTAMP AS ingested_at
FROM remote_db.raw_data
GROUP BY ts
ORDER BY ts ASC