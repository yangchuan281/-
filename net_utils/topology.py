import re
from net_utils.ssh_client import get_connection


def discover_neighbors(device):
    """通过 CDP/LLDP 发现邻居设备"""
    try:
        conn = get_connection(device)
        if device.device_type in ("cisco_ios", "cisco_xe"):
            output = conn.send_command("show cdp neighbors detail")
        else:
            output = conn.send_command("show lldp neighbors detail")
        conn.disconnect()

        neighbors = parse_cdp(output) if "cisco" in device.device_type else parse_lldp(output)
        return True, neighbors
    except Exception as e:
        return False, str(e)


def parse_cdp(output):
    """解析 CDP 输出"""
    neighbors = []
    entries = output.split("Device ID:")[1:] if "Device ID:" in output else []

    for entry in entries:
        lines = entry.strip().split("\n")
        name = lines[0].strip()
        ip = ""
        local_port = ""
        remote_port = ""

        for line in lines:
            if "IP address:" in line:
                ip = line.split(":")[-1].strip()
            elif "Interface:" in line and "Port ID:" in line:
                parts = line.split(",")
                local_port = parts[0].split(":")[-1].strip()
                remote_port = parts[1].split(":")[-1].strip()

        if name and ip:
            neighbors.append({
                "name": name,
                "ip": ip,
                "local_port": local_port,
                "remote_port": remote_port,
            })

    return neighbors


def parse_lldp(output):
    """解析 LLDP 输出"""
    neighbors = []
    entries = output.split("Local Intf:")[1:] if "Local Intf:" in output else []

    for entry in entries:
        lines = entry.strip().split("\n")
        local_port = ""
        remote_port = ""
        name = ""
        ip = ""

        for line in lines:
            if "Local Intf:" in line:
                local_port = line.split(":")[-1].strip()
            elif "Port id:" in line:
                remote_port = line.split(":")[-1].strip()
            elif "System Name:" in line:
                name = line.split(":")[-1].strip()
            elif "Management Addresses:" in line:
                ip = line.split(":")[-1].strip()

        if name:
            neighbors.append({
                "name": name,
                "ip": ip,
                "local_port": local_port,
                "remote_port": remote_port,
            })

    return neighbors
