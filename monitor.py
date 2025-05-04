from pathlib import Path
import json
import ttkbootstrap as ttk
from ttkbootstrap import PhotoImage, Text, StringVar, IntVar
from ttkbootstrap.constants import *


class EditableLabel(ttk.Label):
    def __init__(self, master, exposevariable, *args, **kwargs):
        super().__init__(
            master,
            textvariable=exposevariable,
            #3borderwidth=2,
            #relief="sunken",
            #padding=(5, 5, 5, 5),
            *args,
            **kwargs
        )
        self.label_variable = exposevariable
        self.entry = ttk.Entry(self, font=("Noto Sans", 15))
        self.bind("<Double-1>", self.edit_start)
        self.entry.bind("<Return>", self.edit_save)
        self.entry.bind("<FocusOut>", self.edit_stop) 
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_start(self, event=None):
        self.entry.place(
            relx=0.5, rely=0.5, relwidth=1.0, relheight=1.5, anchor="center"
        )
        self.entry.focus_set()
        self.editing = True

    def edit_save(self, event=None):
        self.configure(text=self.entry.get())
        super(EditableLabel, self).config(text=self.entry.get())
        self.entry.place_forget()

    def edit_stop(self, event=None):
        self.configure(text=self.entry.get())
        self.entry.place_forget()

    def edit_cancel(self, event=None):
        self.entry.delete(0, "end")
        self.entry.place_forget()


class Dash(ttk.Frame):

    def __init__(self, master, json_file):
        super().__init__(master, padding=(5, 5))
        self.pack(fill=BOTH, expand=YES)
        self.editing = False
        dash_style = ttk.Style()
        dash_style.configure(".", font=("Noto Sans", 15))

        # form header
        header_text = "State Monitor"
        header = ttk.Label(
            master=self, font=("Noto Sans", 23), text=header_text, width=50
        )
        header.pack(fill=X, pady=5)

        self.status_evse = StringVar()
        self.create_entry("status_evse", self.status_evse)
        self.Gun_connected = IntVar()
        self.create_entry("Gun_connected", self.Gun_connected)
        self.send_or_stop = IntVar()
        self.create_entry("send_or_stop", self.send_or_stop)
        self.Reservation_id = IntVar()
        self.create_entry("Reservation_id", self.Reservation_id)
        self.Estop = IntVar()
        self.create_entry("Estop", self.Estop)
        self.Powerloss = IntVar()
        self.create_entry("Powerloss", self.Powerloss)
        self.Idtag = StringVar()
        self.create_entry("Idtag", self.Idtag)
        self.Voltage = IntVar()
        self.create_entry("Voltage", self.Voltage)
        self.Current = IntVar()
        self.create_entry("Current", self.Current)
        self.Active_Power = IntVar()
        self.create_entry("Active_Power", self.Active_Power)
        self.Frequency = IntVar()
        self.create_entry("Frequency", self.Frequency)
        self.Power_factor = IntVar()
        self.create_entry("Power_factor", self.Power_factor)
        self.Temperature = IntVar()
        self.create_entry("Temperature", self.Temperature)
        self.create_buttonbox()

        provided_path = Path(json_file)
        if not provided_path.is_file():
            raise TypeError

        self.json_file = json_file
        self.update_from_file()

        self.update_job = self.after(500, self.update_from_file_callback)

    def create_entry(self, label, variable):
        """Create a single form entry"""
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES, pady=5)

        def format_json_key(string):
            return " ".join(word.title() for word in string.split("_"))

        key_label = ttk.Label(
            master=container,
            text=format_json_key(label),
            width=19,
        )
        key_label.pack(side=LEFT, fill=X, padx=15)

        self.editable = EditableLabel(master=container, exposevariable=variable)
        self.editable.pack(side=LEFT, padx=5, fill=X, expand=YES)

    def create_buttonbox(self):
        """Create the application buttonbox"""
        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES, pady=(15, 10))

        edit_button = ttk.Button(
            master=container,
            text="Edit",
            command=self.on_edit,
            bootstyle=INFO,
            width=6,
        )
        edit_button.pack(side=RIGHT, padx=5)
        edit_button.focus_set()

        cancel_button = ttk.Button(
            master=container,
            text="Cancel",
            command=self.on_cancel,
            bootstyle=DARK,
            width=6,
        )
        cancel_button.pack(side=RIGHT, padx=5)

    def on_edit(self):
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

        print(data)

        with open(self.json_file, "w") as json_file_write:
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
        if not self.editing:
            self.update_from_file()
        self.update_job = self.after(500, self.update_from_file_callback)


if __name__ == "__main__":

    app = ttk.Window("Data Entry", "dashui", resizable=(False, False))
    app.geometry("550x750")
    Dash(app, "memory.json")
    app.mainloop()
