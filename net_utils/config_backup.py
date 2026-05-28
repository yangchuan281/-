from net_utils.ssh_client import get_connection


def backup_device_config(device):
    """备份单台设备的配置"""
    try:
        conn = get_connection(device)
        if device.device_type in ("cisco_ios", "cisco_xe"):
            output = conn.send_command("show running-config")
        elif device.device_type in ("huawei",):
            output = conn.send_command("display current-configuration")
        elif device.device_type in ("hp_comware",):
            output = conn.send_command("display current-configuration")
        elif device.device_type in ("vyos", "vyatta_vyos"):
            output = conn.send_command("show configuration")
        else:
            output = conn.send_command("show running-config")
        conn.disconnect()
        return True, output
    except Exception as e:
        return False, str(e)
