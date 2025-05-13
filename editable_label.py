"""
A Widget that extends the Label widget to support
editing and saving the Label text. Useful in scenarios
where editing is desired and at the same time a
separate input box is not.
"""
import logging
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyperclip



class EditableLabel(ttk.Label):
    """
    Class definition of EditableLabel. This widget extends ttk.Label
    and supports editing, copying from, pasting to the label field.
    An entry widget is overlaid on activation via double-click.
    """
    def __init__(self, master, exposevariable, update_state, label_name, loglevel, *args, **kwargs):
        super().__init__(master, textvariable=exposevariable, *args, **kwargs)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            encoding="utf-8", format="[%(levelname)s][%(funcName)s() ] %(message)s", level=loglevel
        )
        self.expose_variable = exposevariable
        self.update_state = update_state
        self.label_name = label_name
        self.entry = ttk.Entry(self, font=("Noto Sans", 13))
        self.bind("<Double-1>", self.edit_start)
        self.entry.bind("<Return>", self.edit_save)
        self.entry.bind("<Button-3>", self.edit_copy)
        self.entry.bind("<Control-C>", self.edit_copy)
        self.entry.bind("<FocusOut>", self.edit_stop)
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_copy(self, event=None):
        """Copy text from the overlaid Entry widget."""
        pyperclip.copy(self.entry.get())
        self.logger.info("Value copied from entry widget,")

    def edit_start(self, event=None):
        """This callback sets up the beginning of an edit session.
        Update state is a shared object used to synchronize read/write
        between the main GUI and this widget.
        """
        self.entry.place(
            relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center"
        )
        self.entry.delete(0, END)
        self.entry.insert(0, super().cget("text"))
        self.entry.focus_set()
        self.update_state["Editing"] = self.label_name
        self.logger.info("Edit session begun.")

    def edit_save(self, event=None):
        """Save the edited text in the Entry widget to the underlying
        Var bound to the widget and forget the overlaid entry widget.
        """
        self.configure(text=self.entry.get())
        self.expose_variable.set(self.entry.get())
        self.update_state["Commit"] = self.label_name
        self.logger.info("Value changed. Awaiting commit.")
        self.entry.place_forget()

    def edit_stop(self, event=None):
        """Forget the entry widget and abort the edit session when user cancels an edit session by changing focus"""
        self.configure(text=self.entry.get())
        self.update_state["Editing"] = ""
        self.update_state["Commit"] = ""
        self.logger.info("Edit session aborted. Reason: Focus Lost.")
        self.entry.place_forget()

    def edit_cancel(self, event=None):
        """Forget the entry widget and abort the edit session when the user
        cancels an edit session
        """
        self.entry.delete(0, "end")
        self.update_state["Editing"] = ""
        self.update_state["Commit"] = ""
        self.logger.info("Edit session aborted. Reason: Cancelled.")
        self.entry.place_forget()
