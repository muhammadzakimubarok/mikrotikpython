import paramiko

host = "192.168.88.2"  # IP default sebelum DHCP aktif
username = "admin"
password = "rahasiaZaki"

commands = [
    # Identitas router
    "/system identity set name=\"Router Wifi Zaki\"",

    # Rename interface agar mudah dikenali
    "/interface set [find default-name=ether2] name=ether2-UPLINK",
    "/interface set [find default-name=wlan1] name=wlan1-ACCESS",

    # DHCP Client agar ether2 dapat IP dari Router Utama
    "/ip dhcp-client add interface=ether2-UPLINK disabled=no",

    # IP Address untuk WLAN
    "/ip address add address=192.168.2.1/24 interface=wlan1-ACCESS",

    # Pool dan DHCP Server untuk client WiFi
    "/ip pool add name=wifi-pool ranges=192.168.2.10-192.168.2.200",
    "/ip dhcp-server add name=dhcp-WIFI interface=wlan1-ACCESS address-pool=wifi-pool lease-time=1h",
    "/ip dhcp-server network add address=192.168.2.0/24 gateway=192.168.2.1 dns-server=192.168.2.1",

    # Wireless Setup untuk semua smartphone (2.4 GHz band)
    "/interface wireless set wlan1-ACCESS ssid=\"UJI LEVEL ZAKI\" mode=ap-bridge frequency=2412 band=2ghz-b/g/n disabled=no",
    "/interface wireless security-profiles set [ find default=yes ] authentication-types=wpa2-psk wpa2-pre-shared-key=\"SMKBISA\"",

    # NAT agar client WiFi bisa akses internet
    "/ip firewall nat add chain=srcnat out-interface=ether2-UPLINK action=masquerade",

    # Routing ke subnet server (jika perlu akses ke server di Router Utama)
    "/ip route add dst-address=192.168.1.8/29 gateway=192.168.0.1"
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f"✅ Router Wifi: {cmd}")
    error = stderr.read().decode()
    if error:
        print(f"⚠️ Error: {error}")

ssh.close()
print("🎉 Konfigurasi Router Wifi selesai.")
