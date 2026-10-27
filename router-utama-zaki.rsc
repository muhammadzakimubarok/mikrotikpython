/system identity set name="Router Utama Zaki"

/interface set [find default-name=ether1] name=ether1-WAN
/interface set [find default-name=ether3] name=ether3-LAN
/interface set [find default-name=ether4] name=ether4-TRUNK

/interface wireless enable wlan1
/interface wireless set wlan1 ssid="Uji Level Zaki" mode=ap-bridge
/ip address add address=192.168.0.1/24 interface=wlan1

/ip pool add name=pool-wlan ranges=192.168.0.10-192.168.0.100
/ip dhcp-server add name=dhcp-wlan interface=wlan1 address-pool=pool-wlan disabled=no
/ip dhcp-server network add address=192.168.0.0/24 gateway=192.168.0.1 dns-server=8.8.8.8

/ip hotspot profile add name=hotspot-profile dns-name=hotspot.local hotspot-address=192.168.0.1
/ip hotspot add name=hotspot-wlan interface=wlan1 address-pool=pool-wlan profile=hotspot-profile
/ip hotspot user add name=tkj password=tkj limit-bytes-in=2097152 limit-bytes-out=2097152
/ip hotspot user add name=rpl password=rpl limit-bytes-in=2097152 limit-bytes-out=2097152

/ip address add address=172.16.12.2/24 interface=ether1-WAN
/ip route add gateway=172.16.12.1

/ip dns set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes

/ip address add address=192.168.1.1/29 interface=ether3-LAN
/ip pool add name=lan-pool ranges=192.168.1.2-192.168.1.6
/ip dhcp-server add name=dhcp-lan interface=ether3-LAN address-pool=lan-pool disabled=no
/ip dhcp-server network add address=192.168.1.0/29 gateway=192.168.1.1

/ip address add address=192.168.1.9/30 interface=ether4-TRUNK

/routing ospf instance set [find default=yes] router-id=192.168.1.1
/routing ospf network add network=192.168.1.8/30 area=backbone

/ip firewall nat add chain=srcnat out-interface=ether1-WAN action=masquerade
