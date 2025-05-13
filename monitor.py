"""
Status monitor. A GUI application based on ttk/ttkbootstrap
to monitor EV charger state via a provided json file and
controls are provided to perform basic actions.
"""

import argparse
import logging
import sys
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.themes.standard import STANDARD_THEMES
from dash import Dash

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

Dash(app, json_file, arguments.refresh, loglevel)
app.mainloop()
