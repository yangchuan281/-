import difflib
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify

from config import Config
from models import db, Device, ConfigBackup, MonitorData, InterfaceInfo
from net_utils.ssh_client import test_connect
from net_utils.config_backup import backup_device_config
from net_utils.topology import discover_neighbors
from net_utils.monitor import collect_device_stats

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


# ==================== 设备管理 ====================

@app.route("/")
def index():
    devices = Device.query.all()
    return render_template("devices.html", devices=devices)


@app.route("/device/add", methods=["GET", "POST"])
def add_device():
    if request.method == "POST":
        device = Device(
            name=request.form["name"],
            ip=request.form["ip"],
            device_type=request.form["device_type"],
            port=int(request.form.get("port", 22)),
            username=request.form["username"],
            password=request.form["password"],
            enable_secret=request.form.get("enable_secret", ""),
        )
        db.session.add(device)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("device_form.html", device=None)


@app.route("/device/<int:device_id>/edit", methods=["GET", "POST"])
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    if request.method == "POST":
        device.name = request.form["name"]
        device.ip = request.form["ip"]
        device.device_type = request.form["device_type"]
        device.port = int(request.form.get("port", 22))
        device.username = request.form["username"]
        device.password = request.form["password"]
        device.enable_secret = request.form.get("enable_secret", "")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("device_form.html", device=device)


@app.route("/device/<int:device_id>/delete", methods=["POST"])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/device/<int:device_id>/test")
def test_device(device_id):
    device = Device.query.get_or_404(device_id)
    success, msg = test_connect(device)
    return jsonify({"success": success, "message": msg})


# ==================== 设备详情 / 配置备份 ====================

@app.route("/device/<int:device_id>")
def device_detail(device_id):
    device = Device.query.get_or_404(device_id)
    backups = ConfigBackup.query.filter_by(device_id=device_id).order_by(ConfigBackup.created_at.desc()).all()
    return render_template("device_detail.html", device=device, backups=backups)


@app.route("/device/<int:device_id>/backup", methods=["POST"])
def backup_config(device_id):
    device = Device.query.get_or_404(device_id)
    success, result = backup_device_config(device)

    if success:
        backup = ConfigBackup(device_id=device_id, content=result)
        db.session.add(backup)
        db.session.commit()
        return jsonify({"success": True, "message": "配置备份成功"})
    return jsonify({"success": False, "message": result})


@app.route("/backup/<int:backup_id>")
def view_backup(backup_id):
    backup = ConfigBackup.query.get_or_404(backup_id)
    return render_template("backup_view.html", backup=backup)


@app.route("/device/<int:device_id>/diff/<int:backup_id>")
def config_diff(device_id, backup_id):
    current_backup = ConfigBackup.query.get_or_404(backup_id)
    prev_backup = (
        ConfigBackup.query.filter(ConfigBackup.device_id == device_id, ConfigBackup.id < backup_id)
        .order_by(ConfigBackup.id.desc())
        .first()
    )

    diff = ""
    if prev_backup:
        diff = difflib.HtmlDiff().make_table(
            prev_backup.content.splitlines(),
            current_backup.content.splitlines(),
            context=True,
            numlines=3,
        )
    return render_template("config_diff.html", backup=current_backup, prev=prev_backup, diff=diff)


# ==================== 拓扑发现 ====================

@app.route("/topology")
def topology():
    devices = Device.query.all()
    return render_template("topology.html", devices=devices)


@app.route("/topology/discover")
def discover_topology():
    devices = Device.query.all()
    nodes = []
    edges = []
    seen = set()

    for device in devices:
        if device.ip not in seen:
            nodes.append({"id": device.name, "label": device.name, "ip": device.ip})
            seen.add(device.ip)

        success, neighbors = discover_neighbors(device)
        if success:
            for n in neighbors:
                nid = n["name"]
                if n["ip"] and n["ip"] not in seen:
                    nodes.append({"id": nid, "label": nid, "ip": n["ip"]})
                    seen.add(n["ip"])
                edges.append({"from": device.name, "to": nid, "label": n.get("local_port", "")})

    return jsonify({"nodes": nodes, "edges": edges})


# ==================== 状态监控 ====================

@app.route("/monitor")
def monitor():
    devices = Device.query.all()
    return render_template("monitor.html", devices=devices)


@app.route("/monitor/collect", methods=["POST"])
def collect_now():
    devices = Device.query.all()
    results = []
    for device in devices:
        success, data = collect_device_stats(device)
        if success:
            record = MonitorData(device_id=device.id, cpu=data["cpu"], memory=data["memory"])
            db.session.add(record)
            results.append({"device": device.name, **data})
    db.session.commit()
    return jsonify(results)


@app.route("/monitor/data/<int:device_id>")
def monitor_data(device_id):
    records = (
        MonitorData.query.filter_by(device_id=device_id)
        .order_by(MonitorData.timestamp.desc())
        .limit(20)
        .all()
    )
    records.reverse()
    return jsonify(
        {
            "timestamps": [r.timestamp.strftime("%H:%M") for r in records],
            "cpu": [r.cpu for r in records],
            "memory": [r.memory for r in records],
        }
    )


# ==================== 接口信息 ====================

@app.route("/device/<int:device_id>/interfaces")
def device_interfaces(device_id):
    device = Device.query.get_or_404(device_id)
    success, output = __import__("net_utils.ssh_client", fromlist=["get_interfaces"]).get_interfaces(device)
    if success:
        lines = output.split("\n")
        interfaces = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                interfaces.append({"raw": line})
        return jsonify({"success": True, "interfaces": interfaces})
    return jsonify({"success": False, "message": output})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
