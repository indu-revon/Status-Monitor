import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyperclip
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8", format="[%(funcName)s() ] %(message)s", level=logging.DEBUG
)

class EditableLabel(ttk.Label):
    def __init__(self, master, exposevariable, update_state, *args, **kwargs):
        super().__init__(master, textvariable=exposevariable, *args, **kwargs)
        self.expose_variable = exposevariable
        self.update_state = update_state
        self.entry = ttk.Entry(self, font=("Noto Sans", 13))
        self.bind("<Double-1>", self.edit_start)
        self.entry.bind("<Return>", self.edit_save)
        self.entry.bind("<Button-3>", self.edit_copy)
        self.entry.bind("<Control-C>", self.edit_copy)
        self.entry.bind("<FocusOut>", self.edit_stop)
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_copy(self, event=None):
        pyperclip.copy(self.entry.get())
        logger.info("Value copied from entry widget,")

    def edit_start(self, event=None):
        self.entry.place(
            relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center"
        )
        self.entry.delete(0, END)
        self.entry.insert(0, super().cget("text"))
        self.entry.focus_set()
        self.update_state["Editing"] = True
        logger.info("Edit session begun.")

    def edit_save(self, event=None):
        self.configure(text=self.entry.get())
        self.expose_variable.set(self.entry.get())
        self.update_state["Commit"] = True
        logger.info(f"Value changed. Awaiting commit.")
        self.entry.place_forget()

    def edit_stop(self, event=None):
        self.configure(text=self.entry.get())
        self.update_state["Editing"] = False
        self.update_state["Commit"] = False
        logger.info("Edit session aborted. Reason: Focus Lost.")
        self.entry.place_forget()

    def edit_cancel(self, event=None):
        self.entry.delete(0, "end")
        self.update_state["Editing"] = False
        self.update_state["Commit"] = False
        logger.info("Edit session aborted. Reason: Cancelled.")
        self.entry.place_forget()


