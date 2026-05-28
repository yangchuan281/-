from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    ip = db.Column(db.String(64), nullable=False)
    device_type = db.Column(db.String(32), nullable=False)  # cisco_ios, huawei, etc.
    port = db.Column(db.Integer, default=22)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    enable_secret = db.Column(db.String(128), default="")
    created_at = db.Column(db.DateTime, default=datetime.now)

    backups = db.relationship("ConfigBackup", backref="device", lazy="dynamic")
    monitor_data = db.relationship("MonitorData", backref="device", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "device_type": self.device_type,
            "port": self.port,
        }


class ConfigBackup(db.Model):
    __tablename__ = "config_backups"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class MonitorData(db.Model):
    __tablename__ = "monitor_data"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    cpu = db.Column(db.Float, default=0)
    memory = db.Column(db.Float, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class InterfaceInfo(db.Model):
    __tablename__ = "interface_info"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    name = db.Column(db.String(64))
    status = db.Column(db.String(16))  # up / down
    in_traffic = db.Column(db.String(32), default="0")
    out_traffic = db.Column(db.String(32), default="0")
