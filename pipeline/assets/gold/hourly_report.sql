/*@bruin
name: gold.hourly_report
connection: duckdb-inmemory
type: duckdb.sql

hooks:
  pre: 
    - query: | 
        INSTALL quack;
        LOAD quack;
        ATTACH 'quack:{{ var.host }}' AS remote_db (
          DISABLE_SSL true,
          TOKEN {{ var.token }}
        );

materialization:
  type: table
  strategy: create+replace

columns:
  - name: bucket
    type: TIMESTAMP
    description: '30-second time bucket'
  - name: avg_cpu_temp
    type: FLOAT
    description: 'Average CPU temperature'
  - name: max_cpu_temp
    type: FLOAT
    description: 'Max CPU temperature'
  - name: avg_mem_usage
    type: FLOAT
    description: 'Average memory usage percentage'
  - name: min_mem_usage
    type: FLOAT
    description: 'Min memory usage percentage'
  - name: max_mem_usage
    type: FLOAT
    description: 'Max memory usage percentage'
  - name: avg_disk
    type: FLOAT
    description: 'Average disk usage percentage'
  - name: avg_cpu_usage
    type: FLOAT
    description: 'Average CPU usage percentage'
  - name: avg_cpu_volt
    type: FLOAT
    description: 'Average CPU voltage'
  - name: uptime
    type: INTEGER
    description: 'Latest uptime in seconds'
  - name: rx
    type: BIGINT
    description: 'Max receive bytes'
  - name: tx
    type: BIGINT
    description: 'Max transmit bytes'
@bruin*/

SELECT
    time_bucket(INTERVAL '1 hour', timestamp) AS ts,
    ROUND(AVG(cpu_temp_c), 2) AS avg_cpu_temp,
    ROUND(MAX(cpu_temp_c), 2) AS max_cpu_temp,
    ROUND(AVG(memory_usage_pct), 2) AS avg_mem_usage,
    ROUND(MIN(memory_usage_pct), 2) AS min_mem_usage,
    ROUND(MAX(memory_usage_pct), 2) AS max_mem_usage,
    ROUND(AVG(disk_usage_pct), 2) AS avg_disk,
    ROUND(MAX(disk_usage_pct), 2) AS max_disk,
    ROUND(AVG(cpu_usage_pct), 2) AS avg_cpu_usage,
    ROUND(AVG(cpu_usage_pct), 2) AS max_cpu_usage,
    ROUND(AVG(cpu_volt_v), 2) AS avg_cpu_volt,
    ROUND(AVG(cpu_volt_v), 2) AS max_cpu_volt,
    CAST(MAX(uptime_seconds) AS INTEGER) AS uptime,
    MAX(rx_bps) AS rtx_byte,
    MAX(tx_bps) AS tx_byte,
    NOW() as ingested_at
FROM remote_db.raw_data
GROUP BY ts
ORDER BY ts ASC
