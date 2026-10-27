import paramiko

# Konfigurasi koneksi SSH ke MikroTik
host = "192.168.88.1"       # IP MikroTik
username = "user1"          # Username default
password = ""               # Kosong jika belum diset

# Daftar perintah konfigurasi
commands = [
    # IP WAN dan gateway
    "/ip address add address=192.168.1.2/24 interface=ether1",
    "/ip route add gateway=192.168.1.1",

    # IP LAN ether2 dan ether3
    "/ip address add address=196.168.1.1/25 interface=ether2",
    "/ip address add address=192.168.2.1/25 interface=ether3",

    # DHCP Pool untuk ether2
    "/ip pool add name=dhcp_pool_1 ranges=196.168.1.10-196.168.1.100",
    "/ip dhcp-server add name=dhcp1 interface=ether2 address-pool=dhcp_pool_1",
    "/ip dhcp-server network add address=196.168.1.0/25 gateway=196.168.1.1 dns-server=8.8.8.8",

    # DHCP Pool untuk ether3
    "/ip pool add name=dhcp_pool_2 ranges=192.168.2.10-192.168.2.100",
    "/ip dhcp-server add name=dhcp2 interface=ether3 address-pool=dhcp_pool_2",
    "/ip dhcp-server network add address=192.168.2.0/25 gateway=192.168.2.1 dns-server=8.8.8.8",

    # Aktifkan DHCP server
    "/ip dhcp-server enable dhcp1",
    "/ip dhcp-server enable dhcp2",

    # NAT agar client bisa akses internet
    "/ip firewall nat add chain=srcnat action=masquerade out-interface=ether1",

    # Set DNS MikroTik dan aktifkan DNS relay
    "/ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes"
]

# Eksekusi perintah via SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f"✅ Menjalankan: {cmd}")
    error = stderr.read().decode()
    if error:
        print(f"⚠️ Error: {error}")

ssh.close()
print("🎉 Konfigurasi MikroTik selesai.")
