import customtkinter as ct

class LabeledProgress(ct.CTkFrame):
    def __init__(self, *args, master: ct.CTkBaseClass, text: str = "", total_processees: int = 1, current_processee: int = 1, **kwargs):
        super().__init__(*args, master=master, **kwargs)
        self._text = text

        self._total_processees = total_processees
        self._current_processee = current_processee

        self._init_ui()

    def _init_ui(self):
        self.rowconfigure(0, weight=2, uniform="true")
        self.rowconfigure(1, weight=1, uniform="true")

        self.columnconfigure((0,2), weight=1, uniform="yes")
        self.columnconfigure(1, weight=3, uniform="yes")

        self.process_label = ct.CTkLabel(self, text=f"{self._current_processee} / {self._total_processees}", font=ct.CTkFont("Trebuchet MS", 8))
        self.process_label.grid(row=0, column=2, sticky=ct.NSEW)

        self.label = ct.CTkLabel(self, font=ct.CTkFont('Trebuchet MS', 12), text=self._text)
        # self.label.pack(fill=ct.X)
        self.label.grid(row=0, column=1, sticky=ct.S)

        self.progress = ct.CTkProgressBar(self, height=10, mode='indeterminate')
        self.progress.set(0)
        self.progress.grid(row=1, column=0, columnspan=3)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self.label.configure(text=value)
        self._text = value
        return self._text

    @property
    def processees(self):
        return self._current_processee

    @processees.setter
    def processees(self, value):
        self._current_processee = value
        self.update()
        return self._current_processee

    def update(self):
        self.process_label.configure(text=f"{self._current_processee} / {self._total_processees}")

    def complete_processee(self):
        if self._current_processee >= self._total_processees:
            self._current_processee=self._total_processees; return;
        self._current_processee+=1
        self.update()

    def __iadd__(self, value):
        self._current_processee += value
        if self._current_processee >= self._total_processees:
            self._current_processee=self._total_processees
        self.update()

    def set(self, value: float):
        self.progress.set(value)

    def start(self):
        self.progress.start()

    def stop(self):
        self.progress.stop()

    def determinate_mode(self):
        self.progress.configure(mode="determinate")

    def indeterminate_mode(self):
        self.progress.configure(mode = "indeterminate")

    def pack(self, **kwargs):
        return super().pack(ipadx=10, ipady=10, **kwargs)