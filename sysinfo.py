#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, render_template_string
import socket
import psutil
import platform
import time

app = Flask(__name__)

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_mac_address():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_LINK:
                return addr.address
    return "N/A"

def get_system_info():
    system_info = {
        "Operating System": platform.system(),
        "Version": platform.version(),
        "Hostname": socket.gethostname(),
        "IP Address": get_ip_address(),
        "MAC Address": get_mac_address()
    }
    return system_info

def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = []
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info.append({
            "Device": partition.device,
            "Mountpoint": partition.mountpoint,
            "File System Type": partition.fstype,
            "Total Size": usage.total,
            "Used Space": usage.used,
            "Free Space": usage.free
        })
    return disk_info

def get_network_info():
    addrs = psutil.net_if_addrs()
    net_info = {}
    for interface, addresses in addrs.items():
        for addr in addresses:
            if addr.family == socket.AF_INET:
                net_info[interface] = {
                    "IP Address": addr.address,
                    "Netmask": addr.netmask,
                    "Broadcast IP": addr.broadcast
                }
    return net_info

def get_cpu_info():
    return {
        "CPU Usage": psutil.cpu_percent(interval=1),
        "CPU Count": psutil.cpu_count()
    }

def get_memory_info():
    virtual_mem = psutil.virtual_memory()
    return {
        "Total": virtual_mem.total,
        "Available": virtual_mem.available,
        "Used": virtual_mem.used,
        "Percentage": virtual_mem.percent
    }

def get_system_uptime():
    return time.time() - psutil.boot_time()

@app.route('/')
def system_info():
    system_info = get_system_info()
    network_info = get_network_info()
    disk_info = get_disk_info()
    cpu_info = get_cpu_info()
    memory_info = get_memory_info()
    uptime_seconds = get_system_uptime()
    uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

    html_template = """
    <html>
    <head>
        <title>System Information</title>
    </head>
    <body>
        <h1>System Information</h1>

        <h2>Host Name</h2>
        <p>{{ system_info['Hostname'] }}</p>

        <h2>Network Information</h2>
        {% for interface, info in network_info.items() %}
            <h3>Interface: {{ interface }}</h3>
            <p>IP Address: {{ info['IP Address'] }}</p>
            <p>Netmask: {{ info['Netmask'] }}</p>
            <p>Broadcast IP: {{ info['Broadcast IP'] }}</p>
        {% endfor %}

        <h2>Wired Network Information</h2>
        <p>IP Address (IPv4): {{ system_info['IP Address'] }}</p>

        <h2>Operating System (OS) Information</h2>
        {% for key, value in system_info.items() %}
            <p>{{ key }}: {{ value }}</p>
        {% endfor %}

        <h2>Disk Information</h2>
        {% for info in disk_info %}
            <h3>Device: {{ info['Device'] }}</h3>
            <p>Mountpoint: {{ info['Mountpoint'] }}</p>
            <p>File System Type: {{ info['File System Type'] }}</p>
            <p>Total Size: {{ (info['Total Size'] / (1024**3))|round(2) }} GB</p>
            <p>Used Space: {{ (info['Used Space'] / (1024**3))|round(2) }} GB</p>
            <p>Free Space: {{ (info['Free Space'] / (1024**3))|round(2) }} GB</p>
        {% endfor %}

        <h2>CPU Information</h2>
        <p>CPU Usage: {{ cpu_info['CPU Usage'] }}%</p>
        <p>CPU Count: {{ cpu_info['CPU Count'] }}</p>

        <h2>Memory Information</h2>
        <p>Total: {{ (memory_info['Total'] / (1024**3))|round(2) }} GB</p>
        <p>Available: {{ (memory_info['Available'] / (1024**3))|round(2) }} GB</p>
        <p>Used: {{ (memory_info['Used'] / (1024**3))|round(2) }} GB</p>
        <p>Percentage: {{ memory_info['Percentage'] }}%</p>

        <h2>System Uptime</h2>
        <p>System Uptime: {{ uptime_string }}</p>
    </body>
    </html>
    """
    return render_template_string(html_template, system_info=system_info, network_info=network_info, disk_info=disk_info, cpu_info=cpu_info, memory_info=memory_info, uptime_string=uptime_string)

if __name__ == '__main__':
    app.run(debug=True)

