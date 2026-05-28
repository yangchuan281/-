# Network Auto Console · 网络自动化管理平台

基于 Python Flask 的网络设备管理 Web 应用，支持配置备份、拓扑发现和状态监控。

## 功能

| 模块 | 功能 |
|---|---|
| 设备管理 | 添加/编辑/删除网络设备，测试 SSH 连接 |
| 配置备份 | 一键备份运行配置，版本对比 Diff |
| 网络拓扑 | CDP/LLDP 邻居发现，vis.js 可视化拓扑图 |
| 状态监控 | 设备 CPU/内存采集，Chart.js 趋势图表 |

## 技术栈

- **后端**: Python 3, Flask, SQLAlchemy
- **前端**: Bootstrap 5, Chart.js, vis.js
- **网络交互**: Netmiko (SSH)
- **数据库**: SQLite

## 快速开始

```bash
pip install -r requirements.txt
python app.py
```

访问 http://localhost:5000

## 支持的设备类型

Cisco IOS / Cisco XE / 华为 / VyOS / Linux

## 项目结构

```
├── app.py               # Flask 主应用
├── config.py             # 配置文件
├── models.py             # 数据库模型
├── net_utils/
│   ├── ssh_client.py     # Netmiko SSH 连接
│   ├── config_backup.py  # 配置备份
│   ├── topology.py       # 拓扑发现
│   └── monitor.py        # 状态采集
└── templates/            # HTML 模板
```
