from data_types import Configuration
from .input_box import InputBox
from dacite import from_dict
from utils import Resources
import customtkinter as ct
import webbrowser
import json as j
import shutil
import os

class ConfigureMission(ct.CTkFrame):
    def __init__(self, *args, master: ct.CTkBaseClass, **kw):
        super().__init__(*args, master=master, **kw)

        self.data: Configuration = self.get_data()

        self._init_ui()


    def _init_ui(self):
        self.columnconfigure(0, pad=30)
        self.columnconfigure(1)

        self.rowconfigure(0, weight=1)

        # SCORING BOX
        # ==========
        self.scoring_box = ct.CTkFrame(master=self)
        self.scoring_box.grid(row=0, column=0, sticky=ct.NS)

        # Scoring configure
        self.scoring_box.rowconfigure(0, weight=1)
        self.scoring_box.rowconfigure(1, weight=3)
        
        self.scoring_box.columnconfigure(0)
        self.scoring_box.columnconfigure(1, pad=20)
        self.scoring_box.columnconfigure(2)

        # Scoring elements
        self.scoring_text = ct.CTkLabel(master=self.scoring_box, text="Scoring", bg_color="transparent")
        self.scoring_text.grid(row=0, column=0, columnspan=3, sticky=ct.NSEW)

        self.profile_list = ct.CTkComboBox(master=self.scoring_box, command=self.profile_changed, width=250)
        self.reset_profile_values()
        self.profile_list.set(self.data.score_script_location)
        self.profile_list.grid(row=1, column=0)

        self.add_profile_button = ct.CTkButton(master=self.scoring_box, width=28, height=28, text="+", command=self.add_profile)
        self.add_profile_button.grid(row=1, column=1, sticky=ct.W)

        self.open_script = ct.CTkButton(master=self.scoring_box, height=28, text="Open Script", command=self.open_script_command)
        self.open_script.grid(row=1, column=2)

        # API BOX
        # ==========
        self.api_box = ct.CTkFrame(master=self)
        self.api_box.grid(row=0, column=1, sticky=ct.NSEW)

        self.api_text = ct.CTkLabel(master=self.api_box, text="API")
        self.api_text.pack(fill=ct.X, anchor=ct.N, pady=10)

        self.url_box = InputBox(master=self.api_box, 
                                placeholder_text="Url...", 
                                font=ct.CTkFont("Trebuchet MS", 14),
                                acceptable=self.verify_ksl,
                                width=300
                                )
        self.url_box.insert(ct.END, self.data.url)
        self.url_box.pack(side=ct.LEFT, fill=ct.X)

        self.reset_url_box = ct.CTkButton(master=self.api_box, text="↺", width=10, command=self.reset_url)
        self.reset_url_box.pack(side=ct.LEFT)

        self.break_point = ct.CTkFrame(master=self.api_box, fg_color="transparent", width=15, height=28)
        self.break_point.pack(side=ct.LEFT)

        self.page_box = InputBox(master=self.api_box, placeholder_text="Page Count", width=100, acceptable=lambda x : x.isdigit())
        self.page_box.insert(ct.END, str(self.data.page_count))
        self.page_box.pack(side=ct.LEFT)


    def pack(self, **kwargs):
        if not ("ipadx" in kwargs or "ipady" in kwargs):
            return super().pack(ipadx=10, ipady=10, **kwargs)
        return super().pack(**kwargs)
    

    def get_data(self) -> Configuration:
        return from_dict(Configuration, ( Resources.configuration_data.read() ))
    

    def reset_profile_values(self):
        # Setting up combo box
        # Put all scoring files into a list
        values: list[str] = ["scoring/"+f for f in os.listdir(Resources.scoring_location) if os.path.isfile(os.path.join(Resources.scoring_location, f))]
        # If the score file that originally existed doesn't, reselect the default
        if not self.data.score_script_location in values:
            self.data.score_script_location = Resources.default_scoring_script
        self.profile_list.configure(values=values)
    

    def profile_changed(self, value):
        self.data.score_script_location = value


    def open_script_command(self):
        replace_old = '\\'
        webbrowser.open(f"file://{os.getcwd().replace(replace_old, '/')}/{self.data.score_script_location}")


    def add_profile(self):
        count = 1
        script_end_location = f"{Resources.scoring_location}new_scoring_method{count}.py"
        while os.path.isfile(script_end_location):
            count+=1
            script_end_location = f"{Resources.scoring_location}new_scoring_method{count}.py"

        shutil.copy(Resources.new_script_location, script_end_location)
        self.reset_profile_values()


    def reset_url(self):
        self.url_box.delete(0, ct.END)
        self.url_box.insert(0, "https://cars.ksl.com/search/")


    def extract(self) -> Configuration:
        self.data.url = self.url_box.get()
        self.data.page_count = int(self.page_box.get())
        writable: dict = {
            "score_script_location": self.data.score_script_location,
            "url": self.data.url,
            "page_count": self.data.page_count
        }
        Resources.configuration_data.write(writable)
        return self.data


    def verify_ksl(self, future_possible: str):
        return "https://cars.ksl.com/search/" in future_possible
    