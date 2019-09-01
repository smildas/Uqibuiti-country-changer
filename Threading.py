import threading
import paramiko
from SshConnection import *
from IpAddressHandler import *


class Threader(threading.Thread):
    def __init__(self, gui, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.gui = gui

    def run(self):
        self.gui.start_button['state'] = 'disabled'
        self.gui.del_info_text()
        self.gui.insert_text_to_info("Spouštím se")
        self.gui.progress_bar(0)

        error = False

        ip_handler = IpAddressHandler(self.gui)
        ips = None
        try:
            ips = ip_handler.procces_input()
        except ValueError as e:
            error = True
            self.gui.insert_text_to_info(str(e))

        self.gui.progress_bar(0)

        if not error and ips is not None:
            ip_to_change_country = len(ips)
            processed_ips = 0

        self.gui.insert_text_to_info("")
        self.gui.insert_text_to_info("")

        self.gui.insert_text_to_info("Začíná proces změn na aktivních zařízeních.")
        # pokud není prázdný list s ip adresama tam projdi seznam
        if ips is not None:
            for ip in ips:
                self.gui.insert_text_to_info(str(ip) + ": Probíhá změna země")
                ssh = SshConnection(ip, self.gui)

                connected = False
                # try-catch pro ošetření stavu, kdy nemusí po 180s naskočit anténa
                # pokud nenaskočí tak se ukončí smyčka a informuje uživatele co se stalo
                try:
                    connected = ssh.try_change_country()
                # chyba kdy nenaskočí zařízení po změně ip
                except ConnectionError as e:
                    self.gui.insert_text_to_info(str(e))
                    self.gui.show_message_box_error("error", e)
                    error = True
                    break
                # pokus o připojení k zařízení, které nemá ubnt loginy
                except paramiko.ssh_exception.SSHException as e:
                    self.gui.insert_text_to_info(e)
                    processed_ips += 1
                    self.update_progress_bar(ip_to_change_country, processed_ips)
                    continue
                # jiná chyba, která může nastat
                except EOFError as e:
                    self.gui.insert_text_to_info(e)

                if connected:
                    self.gui.insert_text_to_info(str(ip) + ": Změna proběhla v pořádku")
                else:
                    self.gui.insert_text_to_info(str(ip) + ": Nejedná se o Ubiquiti nebo byly zadány nesprávné loginy")

                processed_ips += 1
                self.update_progress_bar(ip_to_change_country, processed_ips)

        if not error and ips is not None:
            self.gui.show_message_box_info("Úspěch", "Změna země na všech zařízeních proběhla v pořádku")

        self.gui.start_button['state'] = 'normal'
        self.gui.progress_bar(0)

    def update_progress_bar(self, final_val, current_val):
        percentage = (current_val / final_val) * 100
        self.gui.progress_bar(percentage)

