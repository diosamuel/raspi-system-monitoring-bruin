import json
import os
import socket
import subprocess
from datetime import datetime, timezone

def getCpuUsage():
    with open("/proc/stat") as f:
        parts = f.readline().split()
    total = sum(int(parts[i]) for i in range(1, 9))
    idle = int(parts[4])
    return round(100 * (1 - idle / total), 2)


def getMemoryUsage():
    with open("/proc/meminfo") as f:
        lines = f.readlines()
    mem = {l.split()[0].rstrip(":"): int(l.split()[1]) for l in lines}
    available = mem.get("MemAvailable", mem.get("MemFree", 0))
    return round((mem["MemTotal"] - available) / mem["MemTotal"] * 100, 2)


def getDiskUsage():
    s = os.statvfs("/")
    return int((s.f_blocks - s.f_bfree) / s.f_blocks * 100)


def getTemp():
    try:
        r = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True, timeout=5)
        return float(r.stdout.strip().split("=")[1].rstrip("'C"))
    except Exception:
        return 0.0


def getVolt():
    try:
        r = subprocess.run(["vcgencmd", "measure_volts"], capture_output=True, text=True, timeout=5)
        return float(r.stdout.strip().split("=")[1].rstrip("V"))
    except Exception:
        return 0.0


def getThrottled():
      r = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=5)
      result = r.stdout.strip().split("=")[1]
      if result != "0x0":
        return 'Error'
      return 'Normal'


def getUptime():
    with open("/proc/uptime") as f:
        return int(float(f.readline().split()[0]))


def getNetStats():
    with open(f"/sys/class/net/wlan0/statistics/rx_bytes") as f:
        rx = int(f.read())
    with open(f"/sys/class/net/wlan0/statistics/tx_bytes") as f:
        tx = int(f.read())
    return rx, tx


def ingest():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    host = socket.gethostname()
    cpu_usage = getCpuUsage()
    mem_usage = getMemoryUsage()
    disk_usage = getDiskUsage()
    cpu_temp = getTemp()
    cpu_volt = getVolt()
    throttled = getThrottled()
    uptime = getUptime()
    rx, tx = getNetStats()

    return json.dumps({
        "timestamp": now,
        "hostname": host,
        "cpu_usage_pct": cpu_usage,
        "memory_usage_pct": mem_usage,
        "disk_usage_pct": disk_usage,
        "cpu_temp_c": cpu_temp,
        "cpu_volt_v": cpu_volt,
        "throttled": throttled,
        "uptime_seconds": uptime,
        "net_iface": "wlan0",
        "rx_bps": rx,
        "tx_bps": tx
    })
ingest()