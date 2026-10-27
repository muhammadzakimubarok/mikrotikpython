import tkinter as tk
from tkinter import ttk
import paramiko

# Konfigurasi Router Utama
router_utama_cmds = [
    "/system identity set name=\"Router Utama Zaki\"",
    "/interface set [find default-name=ether1] name=ether1-WAN",
    "/interface set [find default-name=ether2] name=ether2-UPLINK",
    "/interface set [find default-name=ether3] name=ether3-SERVER",
    "/ip address add address=172.16.12.2/24 interface=ether1-WAN",
    "/ip route add gateway=172.16.12.1",
    "/ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes",
    "/ip address add address=192.168.0.1/30 interface=ether2-UPLINK",
    "/ip pool add name=UPLINK-pool ranges=192.168.0.2",
    "/ip dhcp-server add name=dhcp-UPLINK interface=ether2-UPLINK address-pool=UPLINK-pool disabled=no",
    "/ip dhcp-server network add address=192.168.0.0/30 gateway=192.168.0.1",
    "/ip address add address=192.168.1.9/29 interface=ether3-SERVER",
    "/ip pool add name=SERVER-pool ranges=192.168.1.10-192.168.1.14",
    "/ip dhcp-server add name=dhcp-SERVER interface=ether3-SERVER address-pool=SERVER-pool disabled=no",
    "/ip dhcp-server network add address=192.168.1.8/29 gateway=192.168.1.9",
    "/ip firewall nat add chain=srcnat out-interface=ether1-WAN action=masquerade"
]

# Konfigurasi Router Wifi
router_wifi_cmds = [
    "/system identity set name=\"Router Wifi Zaki\"",
    "/interface set [find default-name=ether2] name=ether2-UPLINK",
    "/interface set [find default-name=wlan1] name=wlan1-ACCESS",
    "/ip dhcp-client add interface=ether2-UPLINK disabled=no",
    "/ip address add address=192.168.2.1/24 interface=wlan1-ACCESS",
    "/ip pool add name=wifi-pool ranges=192.168.2.10-192.168.2.200",
    "/ip dhcp-server add name=dhcp-WIFI interface=wlan1-ACCESS address-pool=wifi-pool lease-time=1h",
    "/ip dhcp-server network add address=192.168.2.0/24 gateway=192.168.2.1 dns-server=192.168.2.1",
    "/interface wireless set wlan1-ACCESS ssid=\"UJI LEVEL ZAKI\" mode=ap-bridge frequency=2412 band=2ghz-b/g/n disabled=no",
    "/interface wireless security-profiles set [ find default=yes ] authentication-types=wpa2-psk wpa2-pre-shared-key=\"SMKBISA\"",
    "/ip firewall nat add chain=srcnat out-interface=ether2-UPLINK action=masquerade",
    "/ip route add dst-address=192.168.1.8/29 gateway=192.168.0.1"
]

# Fungsi eksekusi konfigurasi
def run_config():
    router_type = router_choice.get()
    ip = ip_entry.get()
    user = user_entry.get()
    pwd = pwd_entry.get()

    cmds = router_utama_cmds if router_type == "Router Utama" else router_wifi_cmds

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=user, password=pwd)

    for cmd in cmds:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        log.insert(tk.END, f"> {cmd}\n{output}{error}\n")

    ssh.close()
    log.insert(tk.END, "🎉 Konfigurasi selesai.\n")

# GUI setup
root = tk.Tk()
root.title("Konfigurasi Router SMKN 4")

ttk.Label(root, text="Pilih Jenis Router:").pack()
router_choice = ttk.Combobox(root, values=["Router Utama", "Router Wifi"])
router_choice.set("Router Utama")
router_choice.pack()

ttk.Label(root, text="IP Router:").pack()
ip_entry = tk.Entry(root)
ip_entry.insert(0, "192.168.88.1")
ip_entry.pack()

ttk.Label(root, text="Username:").pack()
user_entry = tk.Entry(root)
user_entry.insert(0, "admin")
user_entry.pack()

ttk.Label(root, text="Password:").pack()
pwd_entry = tk.Entry(root, show="*")
pwd_entry.insert(0, "rahasiaZaki")
pwd_entry.pack()

tk.Button(root, text="Konfigurasi", command=run_config).pack(pady=10)

log = tk.Text(root, height=20, width=80)
log.pack()

root.mainloop()