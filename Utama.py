import paramiko

host = "192.168.88.1"
username = "admin"
password = "rahasiaZaki"

commands = [
    # Identitas router
    "/system identity set name=\"Router Utama Zaki\"",

    # Rename interface agar mudah dikenali
    "/interface set [find default-name=ether1] name=ether1-WAN",
    "/interface set [find default-name=ether3] name=ether3-LAN",
    "/interface set [find default-name=ether4] name=ether4-TRUNK",

    # Aktifkan WLAN dan set SSID
    "/interface wireless enable wlan1",
    "/interface wireless set wlan1 ssid=\"Uji Level Zaki\" mode=ap-bridge",

    # IP WLAN
    "/ip address add address=192.168.0.1/24 interface=wlan1",

    # DHCP untuk WLAN
    "/ip pool add name=pool-wlan ranges=192.168.0.10-192.168.0.100",
    "/ip dhcp-server add name=dhcp-wlan interface=wlan1 address-pool=pool-wlan disabled=no",
    "/ip dhcp-server network add address=192.168.0.0/24 gateway=192.168.0.1 dns-server=8.8.8.8",

    # Hotspot untuk WLAN
    "/ip hotspot profile add name=hotspot-profile dns-name=hotspot.local hotspot-address=192.168.0.1",
    "/ip hotspot add name=hotspot-wlan interface=wlan1 address-pool=pool-wlan profile=hotspot-profile",
    "/ip hotspot user add name=tkj password=tkj limit-bytes-in=2097152 limit-bytes-out=2097152",
    "/ip hotspot user add name=rpl password=rpl limit-bytes-in=2097152 limit-bytes-out=2097152",

    # IP WAN dan gateway internet
    "/ip address add address=172.16.12.2/24 interface=ether1-WAN",
    "/ip route add gateway=172.16.12.1",

    # DNS publik dan aktifkan DNS relay
    "/ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes",

    # IP LAN dan DHCP server
    "/ip address add address=192.168.1.1/29 interface=ether3-LAN",
    "/ip pool add name=lan-pool ranges=192.168.1.2-192.168.1.6",
    "/ip dhcp-server add name=dhcp-lan interface=ether3-LAN address-pool=lan-pool disabled=no",
    "/ip dhcp-server network add address=192.168.1.0/29 gateway=192.168.1.1",

    # IP trunk ke router VLAN
    "/ip address add address=192.168.1.9/30 interface=ether4-TRUNK",

    # Routing OSPF
    "/routing ospf instance set [find default=yes] router-id=192.168.1.1",
    "/routing ospf network add network=192.168.1.8/30 area=backbone",

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
