import tkinter as tk
from tkinter import messagebox, scrolledtext
import paramiko
import subprocess

# IP Router Utama
host = "192.168.88.1"

# Daftar perintah konfigurasi
commands = [
    "/system identity set name=\"Router Utama Zaki\"",
    "/interface set [find default-name=ether1] name=ether1-WAN",
    "/interface set [find default-name=ether3] name=ether3-LAN",
    "/interface set [find default-name=ether4] name=ether4-TRUNK",
    "/interface wireless enable wlan1",
    "/interface wireless set wlan1 ssid=\"Uji Level Zaki\" mode=ap-bridge",
    "/ip address add address=192.168.0.1/24 interface=wlan1",
    "/ip pool add name=pool-wlan ranges=192.168.0.10-192.168.0.100",
    "/ip dhcp-server add name=dhcp-wlan interface=wlan1 address-pool=pool-wlan disabled=no",
    "/ip dhcp-server network add address=192.168.0.0/24 gateway=192.168.0.1 dns-server=8.8.8.8",
    "/ip hotspot profile add name=hotspot-profile dns-name=hotspot.local hotspot-address=192.168.0.1",
    "/ip hotspot add name=hotspot-wlan interface=wlan1 address-pool=pool-wlan profile=hotspot-profile",
    "/ip hotspot user add name=tkj password=tkj limit-bytes-in=2097152 limit-bytes-out=2097152",
    "/ip hotspot user add name=rpl password=rpl limit-bytes-in=2097152 limit-bytes-out=2097152",
    "/ip address add address=172.16.12.2/24 interface=ether1-WAN",
    "/ip route add gateway=172.16.12.1",
    "/ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes",
    "/ip address add address=192.168.1.1/29 interface=ether3-LAN",
    "/ip pool add name=lan-pool ranges=192.168.1.2-192.168.1.6",
    "/ip dhcp-server add name=dhcp-lan interface=ether3-LAN address-pool=lan-pool disabled=no",
    "/ip dhcp-server network add address=192.168.1.0/29 gateway=192.168.1.1",
    "/ip address add address=192.168.1.9/30 interface=ether4-TRUNK",
    "/routing ospf instance set [find default=yes] router-id=192.168.1.1",
    "/routing ospf network add network=192.168.1.8/30 area=backbone",
    "/ip firewall nat add chain=srcnat out-interface=ether1-WAN action=masquerade"
]

# Fungsi ping sebelum SSH
def ping_router(ip):
    try:
        result = subprocess.run(["ping", "-n", "2", ip], capture_output=True, text=True)
        return "Received = 2" in result.stdout or "Received = 1" in result.stdout
    except:
        return False

# Fungsi eksekusi konfigurasi
def run_config():
    username = entry_user.get()
    password = entry_pass.get()

    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, f"🔍 Tes koneksi ke {host}...\n")

    if not ping_router(host):
        output_box.insert(tk.END, f"❌ Router tidak merespons ping ke {host}. Pastikan kabel/WiFi terhubung.\n")
        return

    output_box.insert(tk.END, f"✅ Ping berhasil. Mencoba koneksi SSH...\n")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)

        output_box.insert(tk.END, f"🔗 Terhubung ke Router Utama ({host})\n")
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output_box.insert(tk.END, f"✅ {cmd}\n")
            error = stderr.read().decode()
            if error:
                output_box.insert(tk.END, f"⚠️ Error: {error}\n")

        ssh.close()
        output_box.insert(tk.END, "🎉 Konfigurasi selesai.\n\n")
    except Exception as e:
        messagebox.showerror("Gagal", f"Gagal konek ke {host}\n{str(e)}")

# GUI layout
root = tk.Tk()
root.title("Konfigurasi Router Utama Zaki")

tk.Label(root, text="Username:").grid(row=0, column=0, sticky="w")
entry_user = tk.Entry(root)
entry_user.insert(0, "admin")
entry_user.grid(row=0, column=1, sticky="w")

tk.Label(root, text="Password:").grid(row=1, column=0, sticky="w")
entry_pass = tk.Entry(root, show="*")
entry_pass.grid(row=1, column=1, sticky="w")

tk.Button(root, text="Jalankan Konfigurasi", command=run_config).grid(row=2, column=0, columnspan=2, pady=10)

output_box = scrolledtext.ScrolledText(root, width=80, height=20)
output_box.grid(row=3, column=0, columnspan=2)

root.mainloop()
