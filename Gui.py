import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from Threading import *


class Gui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("640x300")
        self.title("Ubiquitu country changer")
        self.frame1 = Frame(self)
        self.frame1.pack(fill=X)

        self.ipLabel = tk.Label(self.frame1, text="IP addres/addresses:", width=18)
        self.ipLabel.pack(side=LEFT, padx=5, pady=5)
        self.ipEntry = tk.Entry(self.frame1)
        self.ipEntry.pack(fill=X, padx=5, expand=True)

        self.frame2 = Frame(self)
        self.frame2.pack(fill=X)
        self.pass1Label = tk.Label(self.frame2, text="Prvni testovane heslo:", width=18)
        self.pass1Label.pack(side=LEFT, padx=5, pady=0)
        self.pass1Entry = tk.Entry(self.frame2, width=40)
        self.pass1Entry.pack(side=LEFT ,padx=5)

        self.frame3 = Frame(self)
        self.frame3.pack(fill=X)
        self.pass2Label = tk.Label(self.frame3, text="Druhe testovane heslo:", width=18)
        self.pass2Label.pack(side=LEFT, padx=5, pady=0)
        self.pass2Entry = tk.Entry(self.frame3, width=40)
        self.pass2Entry.pack(side=LEFT, padx=5, expand=False)
        self.check_box_state = BooleanVar()
        self.check_box_state.set(True)
        self.check_box = Checkbutton(self.frame3, text='Enable second pass', var=self.check_box_state, command=lambda: self.on_check_box_state_changed(), width=20)
        self.check_box.pack(side=LEFT, padx=5, pady=5, expand=False)

        self.style = ttk.Style()

        self.style.theme_use('default')

        self.style.configure("black.Horizontal.TProgressbar", background='black')
        self.bar = Progressbar(self, length=200, style='black.Horizontal.TProgressbar')

        self.bar['value'] = 0
        self.bar.pack()

        self.frame4 = Frame(self)
        self.frame4.pack(fill=BOTH, expand=True)
        self.scrollText = scrolledtext.ScrolledText(self, width=60, height=5)
        self.scrollText.pack(fill=BOTH, padx=5, pady=5, expand = True)

        self.button = tk.Button(self, text="Start", command=lambda: self.on_button_start(), width=10)
        self.button.pack(padx=5, pady=5)

    @property
    def start_button(self):
        return self.button

    @property
    def ip(self):
        return self.ipEntry.get()

    @property
    def pass1(self):
        return self.pass1Entry.get()

    @property
    def pass2(self):
        return self.pass2Entry.get()

    @property
    def pass2_enabled(self):
        enabled = self.check_box_state.get()
        return enabled

    def insert_text_to_info(self, text):
        self.scrollText.insert(tk.INSERT, text + "\n")
        self.scrollText.see(END)

    def del_info_text(self):
        self.scrollText.delete(1.0, END)

    def show_message_box_error(self, title, message):
        messagebox.showerror(title, message)

    def show_message_box_info(self, title, message):
        messagebox.showinfo(title, message)

    def progress_bar(self, percentage):
        self.bar['value'] = percentage

    def on_button_start(self):
        print(self.ipEntry.get())
        th = Threader(self ,name='Worker-Thread')
        th.start()

    def on_check_box_state_changed(self):
        if self.check_box_state.get() == False:
            self.pass2Entry['state'] = 'disabled'
        else:
            self.pass2Entry['state'] = 'normal'


app = Gui()
app.mainloop()
