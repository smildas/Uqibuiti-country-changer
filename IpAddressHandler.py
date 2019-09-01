import re
import ipaddress
import threading

from SshConnection import SshConnection
from threading import Lock


pattern = '((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])/([8-9]|[1-2][0-9]|3[0-2]))|((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))-((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))'
number_of_workers = 50


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


def worker(ip_handler, number):

    while True:
        ip = ip_handler.get_ip_from_list_to_process()
        if ip is not None:
            is_active = SshConnection.check_if_device_is_up(ip)

            if is_active:
                ip_handler.add_address_to_active_list(ip)
        else:
            break
        ip_handler.udpdate_progress_bar()


class IpAddressHandler:
    def __init__(self, gui):
        self.gui = gui
        self.input = gui.ip
        self.number_of_ip_to_process = 0
        self.number_of_processed_ips = 0
        self.ip_list = []
        self.active_ip_list = []
        self.lock = Lock()

    """
    Zkotroluje vstup podle regexu na ip adresy 
    a pokud se dá vstup ohodnotit jako
    unicast ip, síť nebo rozsah ip adres,
    tak vrátí true
    """
    def validate(self):
        m = re.fullmatch(pattern, self.input)

        if m:
            return True
        else:
            return False

    @synchronized
    def udpdate_progress_bar(self):
        self.number_of_processed_ips += 1
        percentage = (self.number_of_processed_ips / self.number_of_ip_to_process) * 100
        self.gui.progress_bar(percentage)

    def has_ip_to_process(self):
        if len(self.ip_list) > 0:
            return True
        else:
            return False

    @synchronized
    def get_ip_from_list_to_process(self):
        if self.has_ip_to_process():
            ip = self.ip_list[-1]
            del self.ip_list[-1]
            print("Zbývá: " + str(len(self.ip_list)))
            return ip
        else:
            return None

    @synchronized
    def add_address_to_active_list(self, ip):
        self.active_ip_list.append(ip)

    def clasifate_input_and_work_with_him(self):
        try:
            if "-" in self.input:
                print("range")
                self.work_with_range()
            elif "/" in self.input:
                print("network")
                self.work_with_network()
            else:
                print("unicast")
                self.work_with_single_ip()
        except ValueError as e:
            raise ValueError(e)


    def work_with_single_ip(self):
        ip = ipaddress.ip_address(self.input)
        SshConnection.check_if_device_is_up(str(ip))
        self.ip_list.append(str(ip))
        self.number_of_ip_to_process = len(self.ip_list)

    def work_with_range(self):
        splitet = self.input.split('-')
        start_ip = ipaddress.ip_address(splitet[0])
        end_ip = ipaddress.ip_address(splitet[1])
        # pokud je pocatenci ip vetsi nez koncova nedelej nic
        if start_ip > end_ip:
            raise ValueError("Nemůže být větší počátněí ip než koncová ip!!!")

        for ip_int in range(int(start_ip), int(end_ip)+1):
            ip = ipaddress.IPv4Address(ip_int)
            self.ip_list.append(str(ip))
        self.number_of_ip_to_process = len(self.ip_list)

    def work_with_network(self):
        try:
            network = ipaddress.ip_network(self.input)
        except ValueError:
            raise ValueError("Špatně zadaná síť")
        for ip in network:
            self.ip_list.append(str(ip))
        self.number_of_ip_to_process = len(self.ip_list)

    def procces_input(self):
        if self.validate() == False:
            self.gui.insert_text_to_info("Nepovolený vstup!")
            return None

        try:
            self.clasifate_input_and_work_with_him()
        except ValueError as e:
            raise ValueError(e)

        self.gui.insert_text_to_info("Hladám aktivní zařízení...")
        threads = []
        for i in range(number_of_workers):
            t = threading.Thread(target=worker, args=(self, i))
            threads.append(t)
            t.start()

        print("nastartovano")
        for t in threads:
            t.join()

        # items = sorted(self.active_ip_list.count(), key=lambda item: socket.inet_aton(item[0]))

        # for ip in items:
        #
        #     print(ip)

        self.gui.insert_text_to_info("Počet aktivních zařízeních:" + str(len(self.active_ip_list)))
        self.gui.insert_text_to_info("Seznam ip aktivních zařízeních:")

        for ip in sorted(self.active_ip_list, key=lambda ip: \
                (int(ip.split(".")[0]),
                 int(ip.split(".")[1]),
                 int(ip.split(".")[2]),
                 int(ip.split(".")[3]))):
            self.gui.insert_text_to_info(ip)
            print(ip)

        return self.active_ip_list







# iphandling = IpAddressHandler("10.144.30.0/24")
# iphandling.procces_input()

# list = ['1' , '2' , '3']
# print(list[-1])
