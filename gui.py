import customtkinter as ct
import atexit

from error_handling import TopErrorWindow, ErrorData
from components import LabeledProgress, CarHolder
from background_tasks import BackgroundTasks
from resources import ResourceManager
from settings import Settings
import hax as h

class Gui(ct.CTkFrame):
    def __init__(self, *args, master: ct.CTkBaseClass, tasks: BackgroundTasks, **kwargs):
        super().__init__(master=master, *args, **kwargs)

        self.tasks = tasks
        atexit.register(self.cleanup)

        self.pack(fill=ct.BOTH, expand=True, padx=20, pady=20)
        self.init_ui()


    def init_ui(self):
        self.frame_of_cars: CarHolder = None

        self.buttons_panel = ct.CTkFrame(self, fg_color="transparent")
        self.buttons_panel.columnconfigure((0, 1), pad=30)
        self.buttons_panel.rowconfigure(0, weight=1)

        self.settings_button = ct.CTkButton(self.buttons_panel, width=200, height=48, text="Settings", command=self.show_settings)
        self.settings_button.grid(row=0, column=0)
        self.start_button = ct.CTkButton(self.buttons_panel, width=200, height=48, text="Start Mission", command=self.begin_mission)
        self.start_button.grid(row=0, column=1)

        self.progress = LabeledProgress(master=self, text="Preparing UI...", total_processees=2, width=800, height=300, fg_color="transparent")
        self.progress.set(0)
        self.progress.start()
        self.progress.pack(anchor=ct.CENTER, expand=True)
        
        self.tasks(self.ingest_data, ( h.convert_to_car(ResourceManager.scored_data.read(), False), ErrorData() ))


    def pack_ui(self):
        self.frame_of_cars.pack(anchor=ct.CENTER, expand=True, fill=ct.BOTH)
        # self.configurator.pack(anchor=ct.CENTER, expand=True, pady=20)
        # self.mission_configure.pack()
        # self.settings_button.pack()
        # self.start_button.pack()
        self.buttons_panel.pack()


    def unpack_ui(self):
        if not self.frame_of_cars == None: 
            self.frame_of_cars.pack_forget()
            self.frame_of_cars.cleanup()
            del self.frame_of_cars

        self.buttons_panel.pack_forget()
        # self.start_button.pack_forget()
        # self.settings_button.pack_forget()


    def show_settings(self):
        Settings().grab_set()


    def begin_mission(self):    
        self.unpack_ui()

        self.progress = LabeledProgress(master=self, text="Clearing Cache...", total_processees=2, width=800, height=300, fg_color="transparent")
        self.progress.set(0)
        self.progress.start()
        self.progress.pack(anchor=ct.CENTER, expand=True)

        ResourceManager.clean_cache()

        self.progress.text = "Gathering Car Information..."

        self.tasks(h.filter_wrapper, (ResourceManager.configuration_data.get_configuration(), self.ingest_data))


    def ingest_data(self, data, error_data: ErrorData):
        if not error_data.is_empty():
            print("Error Ocurred")
            self.tasks.run_in_main(lambda : TopErrorWindow(error_data).start())

        self.progress.stop()
        self.progress.determinate_mode()
        self.progress.complete_processee()

        self.progress.text = "Loading Cars"
        self.frame_of_cars = CarHolder(master=self, data=data, progress=self.progress, tasks=self.tasks)
        
        self.progress.pack_forget()

        self.pack_ui()

    def cleanup(self):
        if self.frame_of_cars == None: return
        self.frame_of_cars.cleanup()