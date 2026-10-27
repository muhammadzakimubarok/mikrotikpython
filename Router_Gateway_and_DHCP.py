import paramiko

host = "192.168.88.1"
username = "admin"
password = "smkn4"

commands = [
    # Identitas router
    "/system identity set name=\"Router Utama Zaki\"",

    # Rename interface agar mudah dikenali
    "/interface set [find default-name=ether1] name=ether1-WAN",
    "/interface set [find default-name=ether2] name=ether2-UPLINK",
    "/interface set [find default-name=ether3] name=ether3-SERVER",

    # IP WAN dan gateway internet
    "/ip address add address=172.16.12.182/24 interface=ether1-WAN",
    "/ip route add gateway=172.16.12.1",

    # DNS publik dan aktifkan DNS relay
    "/ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes",

    # IP UPLINK dan DHCP server
    "/ip address add address=192.168.1.9/30 interface=ether2-UPLINK",
    "/ip pool add name=UPLINK-pool ranges=192.168.1.10",
    "/ip dhcp-server add name=dhcp-UPLINK interface=ether2-UPLINK address-pool=UPLINK-pool disabled=no",
    "/ip dhcp-server network add address=192.168.1.8/30 gateway=192.168.1.9",

    # IP SERVER dan DHCP server
    "/ip address add address=192.168.1.1/29 interface=ether3-SERVER",
    "/ip pool add name=SERVER-pool ranges=192.168.1.2-192.168.1.6",
    "/ip dhcp-server add name=dhcp-SERVER interface=ether3-SERVER address-pool=SERVER-pool disabled=no",
    "/ip dhcp-server network add address=192.168.1.1/29 gateway=192.168.1.1",
    
    # NAT agar semua jaringan bisa akses internet
    "/ip firewall nat add chain=srcnat out-interface=ether1-WAN action=masquerade"
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f"✅ Router Utama: {cmd}")
    error = stderr.read().decode()
    if error:
        print(f"⚠️ Error: {error}")

ssh.close()
print("🎉 Konfigurasi Router Utama selesai.")
