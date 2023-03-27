from background_tasks import BackgroundTasks
import customtkinter as ct
from components import LabeledProgress, CarHolder, ConfigureMission
from error_handling import TopErrorWindow, ErrorData
from utils import Resources
import hax as h
import atexit

class Gui(ct.CTkFrame):
    def __init__(self, *args, master: ct.CTkBaseClass, tasks: BackgroundTasks, **kwargs):
        super().__init__(master=master, *args, **kwargs)

        self.tasks = tasks
        atexit.register(self.cleanup)

        self.pack(fill=ct.BOTH, expand=True, padx=20, pady=20)
        self.init_ui()


    def init_ui(self):
        self.frame_of_cars: CarHolder = None

        self.configurator = ct.CTkFrame(self, bg_color="transparent", fg_color="transparent")

        self.mission_configure = ConfigureMission(master=self.configurator)
        self.mission_configure.pack()

        self.start_button = ct.CTkButton(self.configurator, width=200, height=48, text="Start Mission", command=self.begin_mission)

        self.progress = LabeledProgress(master=self, text="Preparing UI...", total_processees=2, width=800, height=300, fg_color="transparent")
        self.progress.set(0)
        self.progress.start()
        self.progress.pack(anchor=ct.CENTER, expand=True)
        
        self.tasks(self.log, ( h.convert_to_car(Resources.scored_data.read(), False), ErrorData() ))


    def pack_ui(self):
        self.frame_of_cars.pack(anchor=ct.CENTER, expand=True, fill=ct.BOTH)
        self.configurator.pack(anchor=ct.CENTER, expand=True, pady=20)
        self.start_button.pack()


    def begin_mission(self):
        if not self.frame_of_cars == None: 
            self.frame_of_cars.pack_forget()
            self.frame_of_cars.cleanup()
            del self.frame_of_cars

        self.progress = LabeledProgress(master=self, text="Clearing Cache...", total_processees=2, width=800, height=300, fg_color="transparent")
        self.progress.set(0)
        self.progress.start()
        self.progress.pack(anchor=ct.CENTER, expand=True)

        Resources.clean_cache()

        self.progress.text = "Gathering Car Information..."

        self.configurator.pack_forget()

        self.tasks(h.filter_wrapper, (self.mission_configure.extract(), self.log))


    def log(self, data, error_data: ErrorData):
        if not error_data.is_empty():
            print("Error Ocurred")
            self.tasks.run_in_main(lambda : TopErrorWindow(error_data).start())

        self.progress.stop()
        self.progress.determinate_mode()
        self.progress.complete_processee()

        # self.frame_of_cars = ct.CTkFrame(master=self, height=500)

        self.progress.text = "Loading Cars"
        self.frame_of_cars = CarHolder(master=self, data=data, progress=self.progress, tasks=self.tasks)
        # self.frame_of_cars.pack(padx=10, pady=10, fill=ct.BOTH, expand=True)
        
        self.progress.pack_forget()

        self.pack_ui()

    def cleanup(self):
        if self.frame_of_cars == None: return
        self.frame_of_cars.cleanup()