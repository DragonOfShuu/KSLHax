import customtkinter as ct

from resources import ResourceManager
from data_types import Configuration
from .settings import settingable

class ConfigureMission(ct.CTkFrame):
    def __init__(self, *args, master: ct.CTkBaseClass, **kw):
        super().__init__(*args, master=master, **kw)

        self.data: Configuration = self.get_data()

        self._init_ui()


    def _init_ui(self):
        self.all_settings = []
        for setting in settingable:
            current_setting = setting(self)
            current_setting.pack(anchor=ct.W, fill=ct.X)
            self.all_settings.append(current_setting)
    

    def get_data(self) -> Configuration:
        return ResourceManager.configuration_data.get_configuration()


    def extract(self) -> Configuration:
        writable = {}
        for i in self.all_settings:
            writable.update(i.extract())
        ResourceManager.configuration_data.write(writable)
        return self.data
    