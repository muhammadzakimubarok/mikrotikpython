import tkinter as tk
from tkinter import messagebox, scrolledtext
import paramiko

# Konfigurasi perangkat
devices = {
    "Router Utama": {
        "host": "192.168.88.1",
        "commands": [
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
    },
    "Router VLAN": {
        "host": "192.168.1.10",
        "commands": [
            "/system identity set name=\"Router VLAN Zaki\"",
            "/interface set [find default-name=ether4] name=ether4-UPLINK",
            "/interface set [find default-name=ether5] name=ether5-TRUNK",
            "/ip address add address=192.168.1.10/30 interface=ether4-UPLINK",
            "/interface vlan add name=vlan-rpl vlan-id=111 interface=ether5-TRUNK",
            "/interface vlan add name=vlan-tkj vlan-id=222 interface=ether5-TRUNK",
            "/interface vlan add name=vlan-mgmt vlan-id=99 interface=ether5-TRUNK",
            "/ip address add address=10.11.0.97/27 interface=vlan-rpl",
            "/ip pool add name=pool-rpl ranges=10.11.0.98-10.11.0.126",
            "/ip dhcp-server add name=dhcp-rpl interface=vlan-rpl address-pool=pool-rpl disabled=no",
            "/ip dhcp-server network add address=10.11.0.96/27 gateway=10.11.0.97",
            "/ip address add address=10.11.0.129/27 interface=vlan-tkj",
            "/ip pool add name=pool-tkj ranges=10.11.0.130-10.11.0.158",
            "/ip hotspot profile add name=hotspot-tkj dns-name=tkj.local hotspot-address=10.11.0.129",
            "/ip hotspot add name=hotspot-tkj interface=vlan-tkj address-pool=pool-tkj profile=hotspot-tkj",
            "/ip hotspot user add name=murid password=murid",
            "/ip hotspot user add name=guru password=guru",
            "/ip firewall filter add chain=forward src-address=10.11.0.128/27 dst-address=172.16.11.0/24 action=drop comment=\"Blok akses TKJ ke server\"",
            "/ip address add address=10.10.10.1/29 interface=vlan-mgmt",
            "/routing ospf instance set [find default=yes] router-id=192.168.1.10",
            "/routing ospf network add network=192.168.1.8/30 area=backbone",
            "/routing ospf network add network=10.11.0.96/27 area=backbone",
            "/routing ospf network add network=10.11.0.128/27 area=backbone",
            "/routing ospf network add network=10.10.10.0/29 area=backbone"
        ]
    }
}

# GUI setup
def run_config():
    device = selected_device.get()
    host = devices[device]["host"]
    commands = devices[device]["commands"]
    username = entry_user.get()
    password = entry_pass.get()

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        output_box.insert(tk.END, f"🔗 Terhubung ke {device} ({host})\n")
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
root.title("Konfigurasi MikroTik Zaki")

tk.Label(root, text="Pilih Perangkat:").grid(row=0, column=0, sticky="w")
selected_device = tk.StringVar(value="Router Utama")
tk.OptionMenu(root, selected_device, *devices.keys()).grid(row=0, column=1, sticky="w")

tk.Label(root, text="Username:").grid(row=1, column=0, sticky="w")
entry_user = tk.Entry(root)
entry_user.insert(0, "admin")
entry_user.grid(row=1, column=1, sticky="w")

tk.Label(root, text="Password:").grid(row=2, column=0, sticky="w")
entry_pass = tk.Entry(root, show="*")
entry_pass.grid(row=2, column=1, sticky="w")

tk.Button(root, text="Jalankan Konfigurasi", command=run_config).grid(row=3, column=0, columnspan=2, pady=10)

output_box = scrolledtext.ScrolledText(root, width=80, height=20)
output_box.grid(row=4, column=0, columnspan=2)

root.mainloop()
