import re
from net_utils.ssh_client import get_connection


def collect_device_stats(device):
    """采集设备 CPU 和内存信息"""
    try:
        conn = get_connection(device)

        cpu = 0
        memory = 0

        if device.device_type in ("cisco_ios", "cisco_xe"):
            cpu_output = conn.send_command("show processes cpu | include CPU utilization")
            mem_output = conn.send_command("show memory statistics")

            # 解析 CPU: "CPU utilization for 5 seconds: 2%/0%"
            match = re.search(r"CPU utilization.*?(\d+)%", cpu_output)
            if match:
                cpu = float(match.group(1))

            # 解析内存
            match = re.search(r"Processor\s+(\d+)\s+(\d+)", mem_output)
            if match:
                used = int(match.group(1))
                free = int(match.group(2))
                total = used + free
                if total > 0:
                    memory = round(used / total * 100, 1)

        elif device.device_type in ("huawei",):
            cpu_output = conn.send_command("display cpu-usage")
            mem_output = conn.send_command("display memory")

            match = re.search(r"(\d+)%", cpu_output)
            if match:
                cpu = float(match.group(1))

            match = re.search(r"Memory Using.*?(\d+)%", mem_output)
            if match:
                memory = float(match.group(1))

        elif device.device_type in ("vyos", "vyatta_vyos", "linux"):
            cpu_output = conn.send_command("cat /proc/stat | grep '^cpu '")
            parts = cpu_output.strip().split()
            if len(parts) >= 5:
                total = sum(int(x) for x in parts[1:])
                idle = int(parts[4])
                cpu = round((1 - idle / total) * 100, 1)

            mem_output = conn.send_command("free | grep Mem")
            parts = mem_output.strip().split()
            if len(parts) >= 3:
                total = int(parts[1])
                used = int(parts[2])
                if total > 0:
                    memory = round(used / total * 100, 1)

        conn.disconnect()
        return True, {"cpu": cpu, "memory": memory}
    except Exception as e:
        return False, {"error": str(e)}
