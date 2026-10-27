/system identity set name="Router VLAN Zaki"

/interface set [find default-name=ether4] name=ether4-UPLINK
/interface set [find default-name=ether5] name=ether5-TRUNK

/ip address add address=192.168.1.10/30 interface=ether4-UPLINK

/interface vlan add name=vlan-rpl vlan-id=111 interface=ether5-TRUNK
/interface vlan add name=vlan-tkj vlan-id=222 interface=ether5-TRUNK
/interface vlan add name=vlan-mgmt vlan-id=99 interface=ether5-TRUNK

/ip address add address=10.11.0.97/27 interface=vlan-rpl
/ip pool add name=pool-rpl ranges=10.11.0.98-10.11.0.126
/ip dhcp-server add name=dhcp-rpl interface=vlan-rpl address-pool=pool-rpl disabled=no
/ip dhcp-server network add address=10.11.0.96/27 gateway=10.11.0.97

/ip address add address=10.11.0.129/27 interface=vlan-tkj
/ip pool add name=pool-tkj ranges=10.11.0.130-10.11.0.158
/ip hotspot profile add name=hotspot-tkj dns-name=tkj.local hotspot-address=10.11.0.129
/ip hotspot add name=hotspot-tkj interface=vlan-tkj address-pool=pool-tkj profile=hotspot-tkj
/ip hotspot user add name=murid password=murid
/ip hotspot user add name=guru password=guru

/ip firewall filter add chain=forward src-address=10.11.0.128/27 dst-address=172.16.11.0/24 action=drop comment="Blok akses TKJ ke server"

/ip address add address=10.10.10.1/29 interface=vlan-mgmt

/routing ospf instance set [find default=yes] router-id=192.168.1.10
/routing ospf network add network=192.168.1.8/30 area=backbone
/routing ospf network add network=10.11.0.96/27 area=backbone
/routing ospf network add network=10.11.0.128/27 area=backbone
/routing ospf network add network=10.10.10.0/29 area=backbone
