import json
import argparse
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyperclip
from editable_label import EditableLabel

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8", format="[%(funcName)s() ] %(message)s", level=logging.DEBUG
)

from pathlib import Path

PATH = Path(__file__).parent / "assets"


class Dash(ttk.Frame):

    def __init__(self, master, json_file, refresh_rate):
        super().__init__(master, padding=(5, 5))
        self.pack(fill=BOTH, expand=YES)

        # Singleton class. This will be used later to customise other elements.
        dash_style = ttk.Style()
        dash_style.configure(".", font=("Noto Sans", 15))

        self.update_state = {"Editing": False, "Commit": False}
        self.json_file = json_file
        self.refresh_rate = 500

        self.images = [
            ttk.PhotoImage(name="warning_icon", file=PATH / "warning_icon_32x32.png")
        ]

        # form header
        header_text = "State Monitor"
        header = ttk.Label(
            master=self,
            font=("Noto Sans", 23),
            text=header_text,
            width=12,
            bootstyle="primary",
        )
        header.pack(side=TOP, fill=X, padx=15, pady=10)

        ttk.Separator(master=self, bootstyle="primary").pack(fill=X, pady=10)

        # RO Container contains all the RO parameters which are passively monitored

        ro_border_container = ttk.Frame(master=self, bootstyle="dark")
        ro_border_container.pack(side=TOP, padx=(5, 5), fill=X, expand=YES)
        ro_container = ttk.Frame(master=ro_border_container)
        ro_container.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=YES)

        ro_child_container_pack_params = {
            "side": TOP,
            "fill": X,
            "pady": 10,
            "expand": YES,
        }
        key_label_pack_params = {"side": LEFT, "fill": X, "padx": (15, 15)}
        key_label_style = {"width": 13, "bootstyle": "primary"}
        value_label_pack_params = {
            "side": LEFT,
            "padx": 1,
            "pady": 1,
            "fill": BOTH,
            "expand": YES,
        }
        value_label_width = 8

        # 1st coupled container containing EVSE Status and Power Loss Status
        # EVSE Status
        coupled_container_1 = ttk.Frame(master=ro_container)
        coupled_container_1.pack(**ro_child_container_pack_params)

        status_evse_container = ttk.Frame(master=coupled_container_1)
        status_evse_container.pack(side=LEFT, fill=X, expand=YES)

        status_evse_key_label = ttk.Label(
            master=status_evse_container, text="EVSE Status", **key_label_style
        )
        status_evse_key_label.pack(**key_label_pack_params)

        self.status_evse = ttk.StringVar()
        status_evse_value_label = ttk.Label(
            master=status_evse_container,
            textvariable=self.status_evse,
            width=value_label_width,
        )
        status_evse_value_label.pack(**value_label_pack_params)

        # Reservation Id
        Reservation_id_container = ttk.Frame(master=coupled_container_1)
        Reservation_id_container.pack(side=LEFT, fill=X, expand=YES)

        Reservation_id_key_label = ttk.Label(
            master=Reservation_id_container, text="Reservation ID", **key_label_style
        )
        Reservation_id_key_label.pack(**key_label_pack_params)

        self.Reservation_id = ttk.IntVar()
        Reservation_id_value_label = ttk.Label(
            master=Reservation_id_container,
            textvariable=self.Reservation_id,
            width=value_label_width,
        )
        Reservation_id_value_label.pack(**value_label_pack_params)

        # 1st coupled container end

        # 2nd coupled container containing Active Power and Power Factor
        coupled_container_2 = ttk.Frame(master=ro_container)
        coupled_container_2.pack(**ro_child_container_pack_params)

        # Active Power
        Active_Power_container = ttk.Frame(master=coupled_container_2)
        Active_Power_container.pack(side=LEFT, fill=X, expand=YES)

        Active_Power_key_label = ttk.Label(
            master=Active_Power_container, text="Active Power", **key_label_style
        )
        Active_Power_key_label.pack(**key_label_pack_params)

        self.Active_Power = ttk.IntVar()
        Active_Power_value_label = ttk.Label(
            master=Active_Power_container,
            textvariable=self.Active_Power,
            width=value_label_width,
        )
        Active_Power_value_label.pack(**value_label_pack_params)

        # Power Factor
        Power_factor_container = ttk.Frame(master=coupled_container_2)
        Power_factor_container.pack(side=RIGHT, fill=X, expand=YES)

        Power_factor_key_label = ttk.Label(
            master=Power_factor_container, text="Power Factor", **key_label_style
        )
        Power_factor_key_label.pack(**key_label_pack_params)

        self.Power_factor = ttk.IntVar()
        Power_factor_value_label = ttk.Label(
            master=Power_factor_container,
            textvariable=self.Power_factor,
            width=value_label_width,
        )
        Power_factor_value_label.pack(**value_label_pack_params)

        # 2nd container end

        # 3rd container

        # ID Tag
        id_tag_container = ttk.Frame(master=ro_container)
        id_tag_container.pack(**ro_child_container_pack_params)

        id_tag_key_label = ttk.Label(
            master=id_tag_container, text="ID Tag", width=15, bootstyle="primary"
        )
        id_tag_key_label.pack(**key_label_pack_params)

        self.Idtag = ttk.StringVar()
        id_tag_value_label = ttk.Label(master=id_tag_container, textvariable=self.Idtag)
        id_tag_value_label.pack(**value_label_pack_params)

        # This should be a visual indicator for powerloss occurence
        self.Powerloss = ttk.IntVar()
        self.Powerloss_container = ttk.Frame(master=ro_container)
        self.Powerloss_container.pack(**ro_child_container_pack_params)

        # This is just a TTK frame. No other elegant method available to get a themed rectangle to change colors.
        Powerloss_LED = ttk.Frame(
            master=self.Powerloss_container, style="danger.TFrame"
        )
        Powerloss_LED.pack(side=LEFT, fill=BOTH, expand=YES, padx=15, pady=15)
        Powerloss_label = ttk.Label(
            master=Powerloss_LED,
            image="warning_icon",
            compound="right",
            text="Power Loss",
            style="danger.Inverse.TLabel",
        )
        Powerloss_label.pack(side=TOP, fill=BOTH, expand=YES, padx=(200, 10), pady=10)

        # RO END

        # Slider Container
        slider_border_container = ttk.Frame(master=self, bootstyle="dark")
        slider_border_container.pack(side=TOP, padx=(5, 5), fill=BOTH, expand=YES)
        slider_container = ttk.Frame(master=slider_border_container)
        slider_container.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=YES)

        # Voltage
        self.voltage = ttk.IntVar()
        voltage_container = ttk.Frame(master=slider_container)
        voltage_container.pack(side=TOP, fill=X, expand=YES)
        voltage_label = ttk.Label(
            master=voltage_container, text="Voltage", width=13, bootstyle="primary"
        )
        voltage_label.pack(side=LEFT, fill=X, padx=(5, 5))
        voltage_value_label = ttk.Label(
            master=voltage_container,
            textvariable=self.voltage,
            width=5,
        )
        voltage_value_label.pack(side=LEFT, fill=X, padx=(5, 5))

        voltage_scale = ttk.Scale(
            master=voltage_container, variable=self.voltage, from_=0, to=400, value=200
        )
        voltage_scale.pack(side=RIGHT, fill=X, padx=5, pady=15, expand=YES)

        # current
        self.current = ttk.IntVar()
        current_container = ttk.Frame(master=slider_container)
        current_container.pack(side=TOP, fill=X, expand=YES)
        current_label = ttk.Label(
            master=current_container, text="Current", width=13, bootstyle="primary"
        )
        current_label.pack(side=LEFT, fill=X, padx=(5, 5))

        current_value_label = ttk.Label(
            master=current_container,
            textvariable=self.current,
            width=5,
        )
        current_value_label.pack(side=LEFT, fill=X, padx=(5, 5))

        current_scale = ttk.Scale(
            master=current_container, variable=self.current, from_=0, to=400, value=200
        )
        current_scale.pack(side=TOP, fill=X, padx=5, pady=15, expand=YES)

        # Frequency
        self.frequency = ttk.IntVar()
        frequency_container = ttk.Frame(master=slider_container)
        frequency_container.pack(side=TOP, fill=X, expand=YES)
        frequency_label = ttk.Label(
            master=frequency_container, text="Frequency", width=13, bootstyle="primary"
        )
        frequency_label.pack(side=LEFT, fill=X, padx=(5, 5))

        frequency_value_label = ttk.Label(
            master=frequency_container,
            textvariable=self.frequency,
            width=5,
        )
        frequency_value_label.pack(side=LEFT, fill=X, padx=(5, 5))

        frequency_scale = ttk.Scale(
            master=frequency_container,
            variable=self.frequency,
            from_=0,
            to=400,
            value=200,
        )
        frequency_scale.pack(side=TOP, fill=X, padx=5, pady=15, expand=YES)

        # temperature
        self.temperature = ttk.IntVar()
        temperature_container = ttk.Frame(master=slider_container)
        temperature_container.pack(side=TOP, fill=X, expand=YES)
        temperature_label = ttk.Label(
            master=temperature_container,
            text="Temperature",
            width=13,
            bootstyle="primary",
        )
        temperature_label.pack(side=LEFT, fill=X, padx=(5, 5))

        temperature_value_label = ttk.Label(
            master=temperature_container,
            textvariable=self.temperature,
            width=5,
        )
        temperature_value_label.pack(side=LEFT, fill=X, padx=(5, 5))

        temperature_scale = ttk.Scale(
            master=temperature_container,
            variable=self.temperature,
            from_=0,
            to=400,
            value=200,
        )
        temperature_scale.pack(side=TOP, fill=X, padx=5, pady=15, expand=YES)

        # RW Container here contains some user input widgets
        rw_border_container = ttk.Frame(master=self, bootstyle="info")
        rw_border_container.pack(side=TOP, padx=(5, 5), fill=X, expand=YES)
        rw_container = ttk.Frame(master=rw_border_container)
        rw_container.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=YES)

        rw_coupled_container = ttk.Frame(master=rw_container)
        rw_coupled_container.pack(side=TOP, fill=X, pady=10, expand=YES)

        # This should be a toggle
        gun_connected_container = ttk.Frame(master=rw_coupled_container)
        gun_connected_container.pack(side=LEFT, fill=X, expand=YES)
        dash_style.configure("TCheckbutton", font=("Noto Sans", 17))
        self.gun_connected = ttk.IntVar()
        gun_connected_toggle = ttk.Checkbutton(
            gun_connected_container,
            text="Connect Gun",
            style="Roundtoggle.Toolbutton",
        )
        gun_connected_toggle.pack(side=LEFT, fill=X, padx=10, pady=10, expand=YES)

        # Authorize Button
        self.send_or_stop = ttk.IntVar()
        send_or_stop_container = ttk.Frame(master=rw_coupled_container)
        send_or_stop_container.pack(side=RIGHT, fill=X, expand=YES)
        send_or_stop_button = ttk.Button(
            send_or_stop_container,
            text="Authorize",
            bootstyle=PRIMARY,
        )
        send_or_stop_button.pack(side=LEFT, fill=X, padx=10, pady=10, expand=YES)

        # Emergency Stop: a button
        self.Estop = ttk.IntVar()
        Estop_container = ttk.Frame(master=rw_container)
        Estop_container.pack(side=RIGHT, fill=X, expand=YES)
        dash_style.configure(
            "Estop.TButton",
            background=dash_style.colors.warning,
            foreground="black",
            font=("Noto Sans", 19),
        )
        Estop_button = ttk.Button(
            master=Estop_container,
            text="Emergency Stop",
            command=self.on_estop,
            style="Estop.TButton",
            width=40,
        )
        Estop_button.pack(side=BOTTOM, padx=5, pady=5)

        # RW End

        self.update_from_file_callback()

        self.update_job = self.after(self.refresh_rate, self.update_from_file_callback)

        ttk.Separator(master=self, bootstyle="primary").pack(fill=X, pady=15)

        self.create_buttons()

    # Format json key name for GUI
    #   def format_json_key(self, string):
    #       return " ".join(word.title() for word in string.split("_"))

    #   def create_entry(self, label, variable):
    #       """Create a row for one json key-value pair"""
    #       container = ttk.Frame(self)
    #       container.pack(fill=X, expand=YES, pady=5)

    #       key_label = ttk.Label(
    #           master=container,
    #           text=self.format_json_key(label),
    #           width=15,
    #           bootstyle="primary",
    #       )
    #       key_label.pack(side=LEFT, fill=X, padx=(15, 15))

    #       # Builtin label border styles look dated. This is a simple trick to
    #       # Place the label in a frame with a themed color to 'simulate' a border.
    #       #
    #       editable_container = ttk.Frame(master=container, bootstyle="dark")
    #       editable_container.pack(side=LEFT, padx=(5, 5), fill=X, expand=YES)
    #       editable = EditableLabel(
    #           master=editable_container,
    #           exposevariable=variable,
    #           update_state=self.update_state,
    #       )
    #       editable.pack(side=LEFT, padx=1, pady=1, fill=BOTH, expand=YES)

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
            command=self.on_exit,
            bootstyle=DANGER,
            width=6,
        )
        exit_button.pack(side=LEFT, padx=5)

    def on_estop(self):
        pass

    def on_copy(self):
        data = {}
        data["status_evse"] = self.status_evse.get()
        data["gun_connected"] = self.gun_connected.get()
        data["send_or_stop"] = self.send_or_stop.get()
        data["Reservation_id"] = self.Reservation_id.get()
        data["Estop"] = self.Estop.get()
        data["Powerloss"] = self.Powerloss.get()
        data["Idtag"] = self.Idtag.get()
        data["Voltage"] = self.voltage.get()
        data["Current"] = self.current.get()
        data["Active_Power"] = self.Active_Power.get()
        data["Frequency"] = self.frequency.get()
        data["Power_factor"] = self.Power_factor.get()
        data["Temperature"] = self.temperature.get()
        pyperclip.copy(json.dumps(data, indent=4))

    def on_save(self):
        data = {}
        data["gun_connected"] = self.gun_connected.get()
        data["send_or_stop"] = self.send_or_stop.get()
        data["Estop"] = self.Estop.get()
        data["Powerloss"] = self.Powerloss.get()
        data["Voltage"] = self.voltage.get()
        data["Current"] = self.current.get()
        data["Frequency"] = self.frequency.get()
        data["Temperature"] = self.temperature.get()

        with open(self.json_file, "w") as json_file_write:
            logger.info(f"Commiting to file: {json.dumps(data, indent=4)}")
            json.dump(data, json_file_write, indent=4)
            json_file_write.write("\n")

    def on_exit(self):
        """Exit the application."""
        logger.info("Exiting application.")
        self.quit()

    def update_from_file(self):
        with open(self.json_file, "r") as json_fp:
            data = json.load(json_fp)

            self.status_evse.set(data["status_evse"])
            self.gun_connected.set(data["gun_connected"])
            self.send_or_stop.set(data["send_or_stop"])
            self.Reservation_id.set(data["Reservation_id"])
            self.Estop.set(data["Estop"])

            # Power Loss Indicator
            if data["Powerloss"] == 0:
                if self.Powerloss_container.winfo_manager():
                    self.Powerloss_container.pack_forget()
            elif data["Powerloss"] == 1:
                self.Powerloss_container.pack(side=LEFT, fill=X, expand=YES)

            self.Idtag.set(data["Idtag"])
            self.voltage.set(data["Voltage"])
            self.current.set(data["Current"])
            self.Active_Power.set(data["Active_Power"])
            self.frequency.set(data["Frequency"])
            self.Power_factor.set(data["Power_factor"])
            self.temperature.set(data["Temperature"])

    def update_from_file_callback(self):
        if self.update_state["Commit"]:
            self.on_save()
            self.update_state["Commit"] = False
            self.update_state["Editing"] = False
            logger.info(
                f"Changes commited to file. Exiting Commit session and edit session."
            )

        if not self.update_state["Editing"]:
            logger.debug(f"Refreshing GUI from file contents: {self.json_file}")
            self.update_from_file()

        self.update_job = self.after(self.refresh_rate, self.update_from_file_callback)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog="Status Monitor",
        description="Minimal GUI application to display status from given JSON file and manipulate EV Charger state",
    )
    arg_parser.add_argument(
        "-s",
        "--source",
        default="./memory.json",
        help="Path to the json file to monitor",
    )
    arg_parser.add_argument("-c", "--config", help="Path to the GUI configuration file")
    arg_parser.add_argument(
        "-L",
        "--loglevel",
        help="Specify the verbosity of logs: debug, info, warn, error, quiet",
    )
    arg_parser.add_argument(
        "-r",
        "--refresh",
        default=500,
        help="Time period in ms at which to periodically check source file",
    )
    arg_parser.add_argument("-w", "--width", default=600, help="GUI width")
    arg_parser.add_argument("-l", "--length", default=850, help="GUI height")

    arguments = arg_parser.parse_args()

    json_file = arguments.source

    provided_path = Path(json_file)
    if not provided_path.is_file():
        logger.error(f"Source json file {str(provided_path)} does not seem to exist.")
        exit(1)

    x = arguments.width
    y = arguments.length
    app = ttk.Window("Status Monitor", "dashui", size=(x, y), resizable=(False, False))

    # config_file = arg_parser.config
    Dash(app, json_file, arguments.refresh)
    app.mainloop()
