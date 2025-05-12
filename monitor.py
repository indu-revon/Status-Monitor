"""
Status monitor. A GUI application based on ttk/ttkbootstrap
to monitor EV charger state via a provided json file and
controls are provided to perform basic actions.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES, TOP, BOTTOM, LEFT, RIGHT, X
from ttkbootstrap.themes.standard import STANDARD_THEMES
import pyperclip


PATH = Path(__file__).parent / "assets"


class Dash(ttk.Frame):
    """
    All the UI elements are embedded in the Dash Class.
    """

    def __init__(self, master, json_file, refresh_rate):
        super().__init__(master, padding=(5, 5))
        self.pack(fill=BOTH, expand=YES)

        # Singleton class. This will be used later to customise other elements.
        dash_style = ttk.Style()
        dash_style.configure(".", font=("Noto Sans", 15))

        self.update_state = {"Editing": "", "Commit": ""}
        self.json_file = json_file
        self.refresh_rate = refresh_rate

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
        reservation_id_container = ttk.Frame(master=coupled_container_1)
        reservation_id_container.pack(side=LEFT, fill=X, expand=YES)

        reservation_id_key_label = ttk.Label(
            master=reservation_id_container, text="Reservation ID", **key_label_style
        )
        reservation_id_key_label.pack(**key_label_pack_params)

        self.reservation_id = ttk.IntVar()
        reservation_id_value_label = ttk.Label(
            master=reservation_id_container,
            textvariable=self.reservation_id,
            width=value_label_width,
        )
        reservation_id_value_label.pack(**value_label_pack_params)

        # 1st coupled container end

        # 2nd coupled container containing Active Power and Power Factor
        coupled_container_2 = ttk.Frame(master=ro_container)
        coupled_container_2.pack(**ro_child_container_pack_params)

        # Active Power
        active_power_container = ttk.Frame(master=coupled_container_2)
        active_power_container.pack(side=LEFT, fill=X, expand=YES)

        active_power_key_label = ttk.Label(
            master=active_power_container, text="Active Power", **key_label_style
        )
        active_power_key_label.pack(**key_label_pack_params)

        self.active_power = ttk.IntVar()
        active_power_value_label = ttk.Label(
            master=active_power_container,
            textvariable=self.active_power,
            width=value_label_width,
        )
        active_power_value_label.pack(**value_label_pack_params)

        # Power Factor
        power_factor_container = ttk.Frame(master=coupled_container_2)
        power_factor_container.pack(side=RIGHT, fill=X, expand=YES)

        power_factor_key_label = ttk.Label(
            master=power_factor_container, text="Power Factor", **key_label_style
        )
        power_factor_key_label.pack(**key_label_pack_params)

        self.power_factor = ttk.IntVar()
        power_factor_value_label = ttk.Label(
            master=power_factor_container,
            textvariable=self.power_factor,
            width=value_label_width,
        )
        power_factor_value_label.pack(**value_label_pack_params)

        # 2nd container end

        # ID Tag
        id_tag_container = ttk.Frame(master=ro_container)
        id_tag_container.pack(**ro_child_container_pack_params)

        id_tag_key_label = ttk.Label(
            master=id_tag_container, text="ID Tag", width=15, bootstyle="primary"
        )
        id_tag_key_label.pack(**key_label_pack_params)

        self.id_tag = ttk.StringVar()
        id_tag_value_label = ttk.Label(
            master=id_tag_container, textvariable=self.id_tag
        )
        id_tag_value_label.pack(**value_label_pack_params)

        # This should be a visual indicator for powerloss occurence
        self.powerloss = ttk.IntVar()
        self.powerloss_container = ttk.Frame(master=ro_container)
        self.powerloss_container.pack(**ro_child_container_pack_params)

        # This is just a TTK frame. No other elegant method available
        # to get a themed rectangle to change colors.
        powerloss_led = ttk.Frame(
            master=self.powerloss_container, style="danger.TFrame"
        )
        powerloss_led.pack(side=LEFT, fill=BOTH, expand=YES, padx=15, pady=15)
        powerloss_label = ttk.Label(
            master=powerloss_led,
            image="warning_icon",
            compound="right",
            text="Power Loss",
            style="danger.Inverse.TLabel",
        )
        powerloss_label.pack(side=TOP, fill=BOTH, expand=YES, padx=(200, 200), pady=10)

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

        voltage_scale = ttk.Progressbar(
            master=voltage_container,
            variable=self.voltage,
            maximum=240,
            value=0,
            mode="determinate",
        )
        voltage_scale.pack(side=RIGHT, padx=5, pady=15, fill=X, expand=YES)

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

        current_scale = ttk.Progressbar(
            master=current_container, variable=self.current, value=0, maximum=25
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

        frequency_scale = ttk.Progressbar(
            master=frequency_container, variable=self.frequency, value=0, maximum=60
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

        temperature_scale = ttk.Progressbar(
            master=temperature_container, variable=self.temperature, value=0, maximum=50
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
        self.gun_connection_toggle_state = False

        def gun_connection_toggled():
            if not self.gun_connection_toggle_state:
                self.gun_connection_toggle_state = True
                if self.gun_connected.get() == 0:
                    self.gun_connected.set(1)
                    self.update_state["Editing"] = "gun_connection_toggled"
                    self.update_state["Commit"] = "gun_connection_toggled"
            else:
                self.gun_connection_toggle_state = False
                if self.gun_connected.get() == 1:
                    self.gun_connected.set(0)
                    self.update_state["Editing"] = "gun_connection_toggled"
                    self.update_state["Commit"] = "gun_connected_toggled"

        gun_connected_container = ttk.Frame(master=rw_coupled_container)
        gun_connected_container.pack(side=LEFT, expand=YES)
        self.gun_connected = ttk.IntVar()
        dash_style.configure("Roundtoggle.Toolbutton", font=("Noto Sans", 15))
        self.gun_connection_toggle = ttk.Checkbutton(
            master=gun_connected_container,
            command=gun_connection_toggled,
            text="Connect Gun",
            style="Roundtoggle.Toolbutton",
        )
        self.gun_connection_toggle.pack(side=LEFT, fill=X, padx=10, pady=10, expand=YES)

        # Authorize Button
        self.authorization_state = False

        def authorization_check():
            return True

        def authorize():
            if not self.authorization_state:
                if authorization_check():
                    self.send_or_stop_button.configure(text="De-Authorize")
                    self.authorization_state = True
                    if self.send_or_stop.get() == 0:
                        self.send_or_stop.set(1)
                        self.update_state["Editing"] = "authorize"
                        self.update_state["Commit"] = "authorize"
            else:
                self.send_or_stop_button.configure(text="Authorize")
                self.authorization_state = False
                if self.send_or_stop.get() == 1:
                    self.send_or_stop.set(0)
                    self.update_state["Editing"] = "authorize"
                    self.update_state["Commit"] = "authorize"

        self.send_or_stop = ttk.IntVar()
        send_or_stop_container = ttk.Frame(master=rw_coupled_container)
        send_or_stop_container.pack(side=RIGHT, fill=X, expand=YES)
        self.send_or_stop_button = ttk.Button(
            master=send_or_stop_container,
            text="Authorize",
            command=authorize,
            bootstyle="primary",
        )
        self.send_or_stop_button.pack(side=LEFT, fill=X, padx=10, pady=10, expand=YES)

        # Emergency Stop: a button
        self.estop = ttk.IntVar()
        estop_container = ttk.Frame(master=rw_container)
        estop_container.pack(side=RIGHT, fill=X, expand=YES)
        dash_style.configure(
            "estop.TButton",
            background=dash_style.colors.warning,
            foreground="black",
            font=("Noto Sans", 19),
        )
        estop_button = ttk.Button(
            master=estop_container,
            text="Emergency Stop",
            command=self.on_estop,
            style="estop.TButton",
            width=40,
        )
        estop_button.pack(side=BOTTOM, padx=5, pady=5)

        # RW End

        self.update_callback()

        self.update_job = self.after(self.refresh_rate, self.update_callback)

        ttk.Separator(master=self, bootstyle="primary").pack(fill=X, pady=15)

        self.create_buttons()

    def create_buttons(self):
        """A method to setup the buttons at the bottom"""
        button_container = ttk.Frame(self)
        button_container.pack(fill=X, expand=YES, pady=(15, 10))

        # Writes edited values to the json file
        edit_button = ttk.Button(
            master=button_container,
            text="Save",
            command=self.on_save,
            bootstyle="primary",
            width=6,
        )
        edit_button.pack(side=RIGHT, padx=5)
        edit_button.focus_set()

        # Copies the entire json to the system clipboard
        copy_button = ttk.Button(
            master=button_container,
            text="Copy",
            command=self.on_copy,
            bootstyle="primary",
            width=6,
        )
        copy_button.pack(side=RIGHT, padx=5)
        copy_button.focus_set()

        # Exits the program
        exit_button = ttk.Button(
            master=button_container,
            text="Exit",
            command=self.on_exit,
            bootstyle="danger",
            width=6,
        )
        exit_button.pack(side=LEFT, padx=5)

    def on_estop(self):
        """Callback for emergency stop button"""
        self.estop.set(1)
        self.update_state["Editing"] = "on_estop"
        self.update_state["Commit"] = "on_estop"

    def on_copy(self):
        """Callback for copy button"""
        data = {}
        data["status_evse"] = self.status_evse.get()
        data["gun_connected"] = self.gun_connected.get()
        data["send_or_stop"] = self.send_or_stop.get()
        data["reservation_id"] = self.reservation_id.get()
        data["estop"] = self.estop.get()
        data["powerloss"] = self.powerloss.get()
        data["id_tag"] = self.id_tag.get()
        data["Voltage"] = self.voltage.get()
        data["Current"] = self.current.get()
        data["active_power"] = self.active_power.get()
        data["Frequency"] = self.frequency.get()
        data["power_factor"] = self.power_factor.get()
        data["Temperature"] = self.temperature.get()
        pyperclip.copy(json.dumps(data, indent=4))

    def on_save(self):
        """Main method used to update the json file contents
        based on changes in the GUI
        """
        data = {}
        data["status_evse"] = self.status_evse.get()
        data["gun_connected"] = self.gun_connected.get()
        data["send_or_stop"] = self.send_or_stop.get()
        data["reservation_id"] = self.reservation_id.get()
        data["estop"] = self.estop.get()
        data["powerloss"] = self.powerloss.get()
        data["id_tag"] = self.id_tag.get()
        data["Voltage"] = self.voltage.get()
        data["Current"] = self.current.get()
        data["active_power"] = self.active_power.get()
        data["Frequency"] = self.frequency.get()
        data["power_factor"] = self.power_factor.get()
        data["Temperature"] = self.temperature.get()

        with open(self.json_file, "w", encoding="utf-8") as json_file_write:
            logger.info("Commiting to file: %s", json.dumps(data, indent=4))
            json.dump(data, json_file_write, indent=4)
            json_file_write.write("\n")

    def on_exit(self):
        """Exit the application."""
        logger.info("Exiting application.")
        self.quit()

    def update_from_file(self):
        """Main method to update GUI state from json file"""
        with open(self.json_file, "r", encoding="utf-8") as json_fp:
            data = json.load(json_fp)

            self.status_evse.set(data["status_evse"])
            self.gun_connected.set(data["gun_connected"])
            self.send_or_stop.set(data["send_or_stop"])
            self.reservation_id.set(data["reservation_id"])
            self.estop.set(data["estop"])

            # Power Loss Indicator
            if data["powerloss"] == 0:
                if self.powerloss_container.winfo_manager():
                    self.powerloss_container.pack_forget()
            elif data["powerloss"] == 1:
                self.powerloss_container.pack(side=LEFT, fill=X, expand=YES)

            self.id_tag.set(data["id_tag"])
            self.voltage.set(data["Voltage"])
            self.current.set(data["Current"])
            self.active_power.set(data["active_power"])
            self.frequency.set(data["Frequency"])
            self.power_factor.set(data["power_factor"])
            self.temperature.set(data["Temperature"])

    def update_callback(self):
        """A wrapper around update_from_file which acts as the GUI periodical callback
        and manages the state of data edited in the GUI and data present
        in the source json file
        """
        if self.update_state["Commit"] != "":
            logger.info("Write request for: %s", self.update_state["Commit"])
            self.on_save()
            self.update_state["Commit"] = ""
            self.update_state["Editing"] = ""
            logger.info(
                "Changes commited to file. Exiting Commit session and edit session."
            )

        if not self.update_state["Editing"]:
            logger.debug("Refreshing GUI from file contents: %s", self.json_file)
            self.update_from_file()

        self.update_job = self.after(self.refresh_rate, self.update_callback)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog="Status Monitor",
        description="Minimal GUI application to display status \
                     from given JSON file and manipulate EV Charger state",
    )
    arg_parser.add_argument(
        "-s",
        "--source",
        default="./memory.json",
        help="Path to the json file to monitor",
    )
    arg_parser.add_argument(
        "-L",
        "--loglevel",
        default="DEBUG",
        help="Specify the verbosity of logs: debug, info, warn, error, critical, quite",
    )
    arg_parser.add_argument(
        "-r",
        "--refresh",
        default=500,
        help="Time period in ms at which to periodically check source file",
    )
    arg_parser.add_argument("-w", "--width", default=600, help="GUI width")
    arg_parser.add_argument("-l", "--length", default=850, help="GUI height")
    arg_parser.add_argument(
        "-t", "--theme", default="black", help="Pick a theme for the GUI"
    )

    arguments = arg_parser.parse_args()

    loglevel = arguments.loglevel
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        encoding="utf-8", format="[%(levelname)s][%(funcName)s() ] %(message)s"
    )

    if loglevel.strip().upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logging.getLogger().setLevel(loglevel)
    else:
        logger.error("Unknown value %s passed for logging level", loglevel)
        sys.exit(1)

    json_file = arguments.source
    provided_path = Path(json_file)
    if not provided_path.is_file():
        logger.error("Source json file %s does not seem to exist.", str(provided_path))
        sys.exit(1)

    x = arguments.width
    y = arguments.length

    THEME = arguments.theme

    if THEME not in STANDARD_THEMES:
        if THEME.strip().lower() == "dark":
            THEME = "black"
        elif THEME.strip().lower() == "light":
            THEME = "yeti"

    app = ttk.Window(
        title="Status Monitor", themename=THEME, size=(x, y), resizable=(False, False)
    )

    Dash(app, json_file, arguments.refresh)
    app.mainloop()
