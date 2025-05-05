import json
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyperclip

class EditableLabel(ttk.Label):
    def __init__(self, master, exposevariable, editing, *args, **kwargs):
        super().__init__(master, textvariable=exposevariable, *args, **kwargs)
        self.expose_variable = exposevariable
        self.editing = editing
        self.entry = ttk.Entry(self, font=("Noto Sans", 13))
        self.bind("<Double-1>", self.edit_start)
        self.entry.bind("<Return>", self.edit_save)
        self.entry.bind("<Button-3>", self.edit_copy)
        self.entry.bind("<Control-C>", self.edit_copy)
        self.entry.bind("<FocusOut>", self.edit_stop)
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_copy(self, event=None):
        pyperclip.copy(self.entry.get())
        print("Copied from edit_copy")

    def edit_start(self, event=None):
        self.entry.place(
            relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center"
        )
        self.entry.delete(0, END)
        self.entry.insert(0, super().cget("text"))
        self.entry.focus_set()
        self.editing[0] = True

    def edit_save(self, event=None):
        self.configure(text=self.entry.get())
        print("Current value from self: ", self.entry.get())
        print("Current value from super: ", super().cget("text"))
        self.expose_variable.set(self.entry.get())
        print("Current value from self after setvar: ", self.entry.get())
        print("Current value from super after setvar: ", super().cget("text"))
        self.entry.place_forget()

    def edit_stop(self, event=None):
        self.configure(text=self.entry.get())
        self.editing[0] = False
        self.entry.place_forget()

    def edit_cancel(self, event=None):
        self.entry.delete(0, "end")
        self.editing[0] = False
        self.entry.place_forget()


class Dash(ttk.Frame):

    def __init__(self, master, json_file):
        super().__init__(master, padding=(5, 5))
        self.pack(fill=BOTH, expand=YES)
        dash_style = ttk.Style()
        dash_style.configure(".", font=("Noto Sans", 15))
        self.editing = [False]
        self.json_file = json_file
        self.refresh_rate = 5000

        # form header
        header_text = "State Monitor"
        header = ttk.Label(
            master=self,
            font=("Noto Sans", 23),
            text=header_text,
            width=12,
            bootstyle="primary",
        )
        header.pack(side=TOP, fill=X, padx=15, pady=15)

        ttk.Separator(master=self, bootstyle="primary").pack(fill=X, pady=15)

        self.status_evse = ttk.StringVar()
        self.create_entry("status_evse", self.status_evse)
        self.Gun_connected = ttk.IntVar()
        self.create_entry("Gun_connected", self.Gun_connected)
        self.send_or_stop = ttk.IntVar()
        self.create_entry("send_or_stop", self.send_or_stop)
        self.Reservation_id = ttk.IntVar()
        self.create_entry("Reservation_id", self.Reservation_id)
        self.Estop = ttk.IntVar()
        self.create_entry("Estop", self.Estop)
        self.Powerloss = ttk.IntVar()
        self.create_entry("Powerloss", self.Powerloss)
        self.Idtag = ttk.StringVar()
        self.create_entry("Idtag", self.Idtag)
        self.Voltage = ttk.IntVar()
        self.create_entry("Voltage", self.Voltage)
        self.Current = ttk.IntVar()
        self.create_entry("Current", self.Current)
        self.Active_Power = ttk.IntVar()
        self.create_entry("Active_Power", self.Active_Power)
        self.Frequency = ttk.IntVar()
        self.create_entry("Frequency", self.Frequency)
        self.Power_factor = ttk.IntVar()
        self.create_entry("Power_factor", self.Power_factor)
        self.Temperature = ttk.IntVar()
        self.create_entry("Temperature", self.Temperature)

        provided_path = Path(json_file)
        if not provided_path.is_file():
            raise TypeError

        self.update_from_file()

        self.update_job = self.after(self.refresh_rate, self.update_from_file_callback)

        ttk.Separator(master=self, bootstyle="primary").pack(fill=X, pady=15)

        self.create_buttons()

    def create_entry(self, label, variable):
        """Create a row for one json key-value pair"""
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES, pady=5)

        # Format json key name for GUI
        def format_json_key(string):
            return " ".join(word.title() for word in string.split("_"))

        key_label = ttk.Label(
            master=container, text=format_json_key(label), width=15, bootstyle="primary"
        )
        key_label.pack(side=LEFT, fill=X, padx=(15, 15))

        # Builtin label border styles look dated. This is a simple trick to
        # Place the label in a frame with a themed color to 'simulate' a border.
        #
        editable_container = ttk.Frame(master=container, bootstyle="dark")
        editable_container.pack(side=LEFT, padx=(5, 5), fill=X, expand=YES)
        editable = EditableLabel(
            master=editable_container,
            exposevariable=variable,
            editing=self.editing,
        )
        editable.pack(side=LEFT, padx=1, pady=1, fill=BOTH, expand=YES)

    def create_buttons(self):
        """A method to setup the buttons at the bottom"""
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES, pady=(15, 10))

        # Writes edited values to the json file
        edit_button = ttk.Button(
            master=container,
            text="Save",
            command=self.on_save,
            bootstyle=PRIMARY,
            width=6,
        )
        edit_button.pack(side=RIGHT, padx=5)
        edit_button.focus_set()

        # Copies the entire json to the system clipboard
        copy_button = ttk.Button(
            master=container,
            text="Copy",
            command=self.on_copy,
            bootstyle=PRIMARY,
            width=6,
        )
        copy_button.pack(side=RIGHT, padx=5)
        copy_button.focus_set()

        # Exits the program
        exit_button = ttk.Button(
            master=container,
            text="Exit",
            command=self.on_cancel,
            bootstyle=DANGER,
            width=6,
        )
        exit_button.pack(side=LEFT, padx=5)


    def on_copy(self):
        data = {}
        data["status_evse"] = self.status_evse.get()
        data["Gun_connected"] = self.Gun_connected.get()
        data["send_or_stop"] = self.send_or_stop.get()
        data["Reservation_id"] = self.Reservation_id.get()
        data["Estop"] = self.Estop.get()
        data["Powerloss"] = self.Powerloss.get()
        data["Idtag"] = self.Idtag.get()
        data["Voltage"] = self.Voltage.get()
        data["Current"] = self.Current.get()
        data["Active_Power"] = self.Active_Power.get()
        data["Frequency"] = self.Frequency.get()
        data["Power_factor"] = self.Power_factor.get()
        data["Temperature"] = self.Temperature.get()
        data["status_evse"] = self.status_evse.get()
        pyperclip.copy(json.dumps(data, indent=4))


    def on_save(self):
        data = {}
        data["status_evse"] = self.status_evse.get()
        data["Gun_connected"] = self.Gun_connected.get()
        data["send_or_stop"] = self.send_or_stop.get()
        data["Reservation_id"] = self.Reservation_id.get()
        data["Estop"] = self.Estop.get()
        data["Powerloss"] = self.Powerloss.get()
        data["Idtag"] = self.Idtag.get()
        data["Voltage"] = self.Voltage.get()
        data["Current"] = self.Current.get()
        data["Active_Power"] = self.Active_Power.get()
        data["Frequency"] = self.Frequency.get()
        data["Power_factor"] = self.Power_factor.get()
        data["Temperature"] = self.Temperature.get()
        data["status_evse"] = self.status_evse.get()

        with open(self.json_file, "w") as json_file_write:
            print('About to write this: ', data)
            json.dump(data, json_file_write, indent=4)

    def on_cancel(self):
        """Cancel and close the application."""
        self.quit()

    def update_from_file(self):
        with open(self.json_file, "r") as json_fp:
            data = json.load(json_fp)

            self.status_evse.set(data["status_evse"])
            self.Gun_connected.set(data["Gun_connected"])
            self.send_or_stop.set(data["send_or_stop"])
            self.Reservation_id.set(data["Reservation_id"])
            self.Estop.set(data["Estop"])
            self.Powerloss.set(data["Powerloss"])
            self.Idtag.set(data["Idtag"])
            self.Voltage.set(data["Voltage"])
            self.Current.set(data["Current"])
            self.Active_Power.set(data["Active_Power"])
            self.Frequency.set(data["Frequency"])
            self.Power_factor.set(data["Power_factor"])
            self.Temperature.set(data["Temperature"])

    def update_from_file_callback(self):
        if not self.editing[0]:
            print("@@@@@@@ Resumed Updating @@@@@@@")
            self.update_from_file()
        else:
            print("@@@@@@@ Updating has been paused. @@@@@@@")
            self.on_save()
            self.editing[0] = False

        self.update_job = self.after(self.refresh_rate, self.update_from_file_callback)


if __name__ == "__main__":
    app = ttk.Window("Data Entry", "dashui", resizable=(False, False))
    app.geometry("550x800")
    Dash(app, "memory.json")
    app.mainloop()
