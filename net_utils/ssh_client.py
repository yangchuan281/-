from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException


def get_connection(device):
    """根据设备信息创建 Netmiko SSH 连接"""
    params = {
        "device_type": device.device_type,
        "host": device.ip,
        "port": device.port,
        "username": device.username,
        "password": device.password,
    }
    if device.enable_secret:
        params["secret"] = device.enable_secret
    return ConnectHandler(**params)


def test_connect(device):
    """测试 SSH 连接是否成功"""
    try:
        conn = get_connection(device)
        conn.disconnect()
        return True, "连接成功"
    except NetmikoAuthenticationException:
        return False, "认证失败，请检查用户名和密码"
    except NetmikoTimeoutException:
        return False, "连接超时，请检查 IP 和端口"
    except Exception as e:
        return False, f"连接失败: {str(e)}"


def send_command(device, command):
    """向设备发送命令并返回结果"""
    try:
        conn = get_connection(device)
        output = conn.send_command(command)
        conn.disconnect()
        return True, output
    except Exception as e:
        return False, f"命令执行失败: {str(e)}"


def get_interfaces(device):
    """获取设备接口状态"""
    commands = {
        "cisco_ios": "show interfaces",
        "cisco_xe": "show interfaces",
        "huawei": "display interface brief",
        "hp_comware": "display interface brief",
        "vyos": "ip link show",
        "vyatta_vyos": "ip link show",
        "linux": "ip link show",
    }
    cmd = commands.get(device.device_type, "show interfaces")
    return send_command(device, cmd)


def get_cdp_neighbors(device):
    """获取 CDP/LLDP 邻居信息"""
    if device.device_type in ("cisco_ios", "cisco_xe"):
        return send_command(device, "show cdp neighbors detail")
    if device.device_type in ("vyos", "vyatta_vyos", "linux"):
        return send_command(device, "lldpctl")
    return send_command(device, "show lldp neighbors detail")
