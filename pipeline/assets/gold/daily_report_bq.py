"""@bruin
name: report.daily_report
type: python
connection: gcp-bigdata

secrets:
  - key: PI_TAILSCALE_HOST
  - key: PI_TAILSCALE_TOKEN

materialization:
  type: table
  strategy: create+replace

columns:
  - name: ts
    type: TIMESTAMP
    description: 'Daily time ts'
  - name: avg_cpu_temp
    type: FLOAT64
    description: 'Average CPU temperature'
  - name: max_cpu_temp
    type: FLOAT64
    description: 'Max CPU temperature'
  - name: avg_mem_usage
    type: FLOAT64
    description: 'Average memory usage percentage'
  - name: min_mem_usage
    type: FLOAT64
    description: 'Min memory usage percentage'
  - name: avg_disk
    type: FLOAT64
    description: 'Average disk usage percentage'
  - name: avg_cpu_usage
    type: FLOAT64
    description: 'Average CPU usage percentage'
  - name: avg_cpu_volt
    type: FLOAT64
    description: 'Average CPU voltage'
  - name: uptime
    type: INT64
    description: 'Latest uptime in seconds'
  - name: rx
    type: INT64
    description: 'Max receive bytes'
  - name: tx
    type: INT64
    description: 'Max transmit bytes'
  - name: ingested_at
    type: TIMESTAMP
    description: 'Ingestion timestamp'
@bruin"""

import bruin
import duckdb
import pandas as pd
from dotenv import load_dotenv
load_dotenv()  # loads .env from WorkingDirectory


def materialize() -> pd.DataFrame:
    host = bruin.get_connection("PI_TAILSCALE_HOST").raw
    token = bruin.get_connection("PI_TAILSCALE_TOKEN").raw

    duck_conn = duckdb.connect(":memory:")

    duck_conn.execute("INSTALL quack;")
    duck_conn.execute("LOAD quack;")
    duck_conn.execute(f"""
        ATTACH 'quack:{host}' AS remote_db (
            DISABLE_SSL true,
            TOKEN '{token}'
        );
    """)

    df = duck_conn.execute("""
        SELECT
            time_bucket(INTERVAL '1 day', CAST(REPLACE(timestamp, 'Z', '') AS TIMESTAMP)) AS ts,
            ROUND(AVG(cpu_temp_c), 2) AS avg_cpu_temp,
            ROUND(MAX(cpu_temp_c), 2) AS max_cpu_temp,
            ROUND(AVG(memory_usage_pct), 2) AS avg_mem_usage,
            ROUND(MIN(memory_usage_pct), 2) AS min_mem_usage,
            ROUND(MAX(disk_usage_pct), 2) AS avg_disk,
            ROUND(AVG(cpu_usage_pct), 2) AS avg_cpu_usage,
            ROUND(AVG(cpu_volt_v), 2) AS avg_cpu_volt,
            CAST(MAX(uptime_seconds) AS INTEGER) AS uptime,
            MAX(rx_bps) AS rx,
            MAX(tx_bps) AS tx,
            CURRENT_TIMESTAMP as ingested_at
        FROM remote_db.raw_data
        GROUP BY ts
        ORDER BY ts ASC
    """).fetchdf()

    duck_conn.execute("DETACH remote_db;")
    duck_conn.close()

    return df
