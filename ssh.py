# -*- coding: utf-8 -*-
import paramiko
import re

def run_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode()

def check_router(ip, user, password, router_name):
    detail = {}
    correct_items = 0
    client_ip = None

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, username=user, password=password)
        print(f"[OK] Koneksi SSH {router_name} berhasil.\n")

        ip_output = run_cmd(ssh, "/ip address print detail")
        route_output = run_cmd(ssh, "/ip route print detail")
        dns_output = run_cmd(ssh, "/ip dns print")
        leases_output = run_cmd(ssh, "/ip dhcp-server lease print detail")

        if router_name == "Router1":
            wan = re.search(r'address=(192\.168\.43\.\d+/24)', ip_output)
            detail["WAN ether1"] = f"[OK] {wan.group(1)}" if wan else "[X] WAN tidak ditemukan"
            if wan: correct_items += 1

            uplink = re.search(r'address=(10\.10\.10\.1/30)', ip_output)
            detail["Uplink ether2"] = f"[OK] {uplink.group(1)}" if uplink else "[X] Uplink tidak ditemukan"
            if uplink: correct_items += 1

            lan = re.search(r'address=(172\.16\.9\.(1|6)/29)', ip_output)
            detail["LAN ether3"] = f"[OK] {lan.group(0)}" if lan else "[X] LAN tidak ditemukan"
            if lan: correct_items += 1

            static = re.search(r'dst-address=172\.16\.10\.8/29', route_output)
            detail["Static Route ke LAN R2"] = "[OK] 172.16.10.8/29" if static else "[X] tidak ada"
            if static: correct_items += 1

            default = re.search(r'dst-address=0\.0\.0\.0/0.*gateway=192\.168\.43\.1', route_output)
            detail["Default Route"] = "[OK] 0.0.0.0/0 via 192.168.43.1" if default else "[X] tidak ada"
            if default: correct_items += 1

        elif router_name == "Router2":
            uplink = re.search(r'address=(10\.10\.10\.2/30)', ip_output)
            detail["Uplink ether2"] = f"[OK] {uplink.group(1)}" if uplink else "[X] Uplink tidak ditemukan"
            if uplink: correct_items += 1

            lan = re.search(r'address=(172\.16\.10\.(9|14)/29)', ip_output)
            detail["LAN ether4"] = f"[OK] {lan.group(0)}" if lan else "[X] LAN tidak ditemukan"
            if lan: correct_items += 1

            static = re.search(r'dst-address=172\.16\.9\.0/29', route_output)
            detail["Static Route ke LAN R1"] = "[OK] 172.16.9.0/29" if static else "[X] tidak ada"
            if static: correct_items += 1

            default = re.search(r'dst-address=0\.0\.0\.0/0.*gateway=10\.10\.10\.1', route_output)
            detail["Default Route"] = "[OK] 0.0.0.0/0 via 10.10.10.1" if default else "[X] tidak ada"
            if default: correct_items += 1

        dns_list = re.findall(r'(\d+\.\d+\.\d+\.\d+)', dns_output)
        detail["DNS Server"] = f"[OK] {', '.join(dns_list)}" if dns_list else "[X] tidak ada"
        if dns_list: correct_items += 1

        ping_output = run_cmd(ssh, "ping 8.8.8.8 count=3")
        detail["Ping Internet"] = "[OK] berhasil" if "ms" in ping_output else "[X] gagal"
        if "ms" in ping_output: correct_items += 1

        client_ips = re.findall(r'address=(\d+\.\d+\.\d+\.\d+)', leases_output)
        client_ip = client_ips[0] if client_ips else None
        detail["Client IP"] = f"[OK] {client_ip}" if client_ip else "[X] tidak ada client"
        if client_ip: correct_items += 1

        ssh.close()
        return correct_items, detail, client_ip

    except Exception as e:
        print(f"[X] Gagal koneksi SSH {router_name}: {e}")
        return 0, {"Error": str(e)}, None


def main():
    ip_r1 = input("Masukkan IP Router1: ")
    user_r1 = input("Masukkan Username Router1: ")
    pass_r1 = input("Masukkan Password Router1: ")

    ip_r2 = input("Masukkan IP Router2: ")
    user_r2 = input("Masukkan Username Router2: ")
    pass_r2 = input("Masukkan Password Router2: ")

    correct1, detail1, client1 = check_router(ip_r1, user_r1, pass_r1, "Router1")
    correct2, detail2, client2 = check_router(ip_r2, user_r2, pass_r2, "Router2")

    total_correct = correct1 + correct2
    total_items = 17  # termasuk 2 item ping antar client

    print("\n=== Hasil Penilaian Siswa ===")

    print("\n--- Router1 ---")
    for k, v in detail1.items():
        print(f"{v} {k}")

    print("\n--- Router2 ---")
    for k, v in detail2.items():
        print(f"{v} {k}")

    # Validasi ping antar client
    if client1 and client2:
        ssh1 = paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh1.connect(ip_r1, username=user_r1, password=pass_r1)
        ping_r1 = run_cmd(ssh1, f"ping {client2} count=3")
        ssh1.close()
        hasil_r1 = "[OK] berhasil" if "ms" in ping_r1 else "[X] gagal"
        print(f"\nRouter1 coba ping ke Client Router2 ({client2}) → {hasil_r1}")
        if "ms" in ping_r1: total_correct += 1

        ssh2 = paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh2.connect(ip_r2, username=user_r2, password=pass_r2)
        ping_r2 = run_cmd(ssh2, f"ping {client1} count=3")
        ssh2.close()
        hasil_r2 = "[OK] berhasil" if "ms" in ping_r2 else "[X] gagal"
        print(f"Router2 coba ping ke Client Router1 ({client1}) → {hasil_r2}")
        if "ms" in ping_r2: total_correct += 1

    # Hitung nilai akhir
    final_score = (total_correct / total_items) * 90
    print(f"\nTotal Benar: {total_correct} dari {total_items}")
    print(f"Nilai Akhir (maks 90): {round(final_score, 2)}")


if __name__ == "__main__":
    main()
