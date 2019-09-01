import time
import socket
import paramiko

timeout = 180

class SshConnection:

    def __init__(self, ip, gui):
        self.ip = ip
        self.gui = gui

        self.buff = ''
        self.resp = ''
        self.ssh = None
        self.chan = None

    def send_command_to_device(self, command):
        # Display output of first command
        self.chan.send(command)
        self.chan.send('\n')
        time.sleep(1)
        resp = self.chan.recv(99999)
        output = resp.decode('ascii').split(',')
        print(''.join(output))

    def connect_to_device(self):
        print("připojuji se k zařízení")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(self.gui.pass1)
        connected = self.try_login(self.gui.pass1)

        if not connected and self.gui.pass2_enabled:
            connected = self.try_login(self.gui.pass2)

        if not connected:
            return False

        try:
            self.chan = self.ssh.invoke_shell()
        except paramiko.ssh_exception.SSHException:
            raise paramiko.ssh_exception.SSHException(str(self.ip) + ": nepodařilo se připojit k této ip")
        except EOFError:
            return EOFError(str(self.ip) + ": nepodařilo se připojit k této ip")

        return connected

    def try_login(self, password):
        try:
            self.ssh.connect(self.ip, username='ubnt', password=password)
        except paramiko.ssh_exception.AuthenticationException:
            return False
        return True

    def send_commands_to_device(self):
        self.gui.insert_text_to_info(str(self.ip) + ": Aplikuji příkazy pro změnu zěmě...")
        self.send_command_to_device('cd /var/tmp')
        self.send_command_to_device('sed -i \'s/^\(radio.1.countrycode=\).*/\\1511/\' system.cfg')
        self.send_command_to_device('sed -i \'s/^\(radio.countrycode=\).*/\\1511/\' system.cfg')
        self.send_command_to_device('save')
        self.send_command_to_device('cat system.cfg')
        self.send_command_to_device('reboot')
        self.gui.insert_text_to_info(str(self.ip) + ": Příkazy provedeny")

    def wait_until_device_reboot(self):
        time.sleep(1)
        is_down = True
        time_counter = 1
        while is_down and time_counter <= timeout:
            is_down = not self.check_if_device_is_up(self.ip)
            print(is_down)
            print(time_counter)
            time_counter = time_counter + 1
        return not is_down

    @staticmethod
    def check_if_device_is_up(ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        response = sock.connect_ex((ip, 22))
        if response == 0:
            return True
        else:
            # print("Zařízení je neaktivní")
            return False

    def try_change_country(self):
        is_up = self.check_if_device_is_up(self.ip)
        print("Provádím zmenu země na zařízení s ip: " + str(self.ip))
        if is_up:
            connected = False
            try:
                connected = self.connect_to_device()
            except paramiko.ssh_exception.SSHException as e:
                raise paramiko.ssh_exception.SSHException(e)
            except EOFError as e:
                raise EOFError(e)

            if not connected:
                return False

            self.send_commands_to_device()
            self.ssh.close()
            self.gui.insert_text_to_info(str(self.ip) +": Čekám až nařízení naskočí po rebootu")
            alive = self.wait_until_device_reboot()
            if alive:
                print("zařízení naskočilo")
                return True
            else:
                raise ConnectionError(str(self.ip) + ": zařízení nenaběhlo")
                print("a doprdele")
