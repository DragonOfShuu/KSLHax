import json
import traceback
from error_handling import CompletelyDestroyedException
from dotenv import load_dotenv
import shutil
import os

from error_handling import ErrorData

load_dotenv()

global_save_location = "state/"
global_backups_location = "backups/"

class ResourceObject:
    def __init__(self, base_name: str, /, save_location: str | None = None, json: bool = False, default: str = ""):
        self._base_name = base_name
        self._save_folder = save_location if save_location else global_save_location
        self._json = json
        self._default = default


    @property
    def save_location(self):
        return f"{self._save_folder}{self._base_name}"


    @property
    def base_name(self):
        return self._base_name
    
    def write(self, data: str | dict | list):
        if type(data) != str and self._json: data = json.dumps(data, indent=4)
        elif type(data) != str: raise TypeError("For non JSON resources, only strings are allowed.")
        with open(repr(self), 'w') as f:
            f.write(data)
    
    
    def read(self):
        data: str
        with open(self.__repr__(), 'r') as f:
            data = f.read()
        if not self._json: return data
        else:              return json.loads(data)

    
    def verify(self):
        if not os.path.isfile(repr(self)):
            self.write(self._default)
    

    def __repr__(self) -> str:
        return self.save_location

class BackupObject(ResourceObject):
    def __init__(self, base_name: str, /, save_location: str | None = None, json: bool = False):
        super().__init__(base_name, save_location, json)
        self._default = self.read_backup()
        self.safely_restore()


    @property
    def backup_location(self):
        return f"{global_backups_location}{self._base_name}"


    def safely_restore(self) -> bool:
        '''
            Returns True if the file
            was restored.
        '''
        if not os.path.isfile(self.save_location):
            self.restore()
            return True
        return False
    
    
    def read_backup(self) -> str:
        returnable: str
        try:
            with open(self.backup_location, 'r') as f:
                returnable = f.read()
            return returnable
        except FileNotFoundError:
            raise CompletelyDestroyedException(ErrorData(text=f"Well, the backups are gone. Ya done did.",
                                                         simple_msg=f"Resource \"{self._base_name}\" is missing, corrupt, or destroyed.",
                                                         stack_trace=traceback.format_exc()
                                                         )
                                               )


    def restore(self):
        if not os.path.isfile(self.backup_location):
            raise CompletelyDestroyedException(ErrorData(text=f"Well, the backups are gone. Ya done did.",
                                                         simple_msg=f"Resource \"{self._base_name}\" is missing, corrupt, or destroyed.",
                                                         stack_trace=traceback.format_exc()
                                               ))
        if not os.path.isdir(self._save_folder):
            os.mkdir(self._save_folder)
        shutil.copyfile(self.backup_location, self.save_location)


class Resources:
    save_location = global_save_location
    cache_location = "cache/"
    scoring_location = "scoring/"
    backups_location = global_backups_location
    default_image = "assets/DefaultImage.png"
    new_script_location = "assets/new_score_method.py"

    old_data: ResourceObject = ResourceObject("old_data.json", json=True, default="[]")
    blacklist_data: ResourceObject = ResourceObject("blacklist_data.json", json=True, default="[]")
    scored_data: ResourceObject = ResourceObject("scored_data.json", json=True, default="[]")

    offline_mode: bool = os.environ["OFFLINE_MODE"].upper() == 'TRUE'
    clear_cache: bool = os.environ["CLEAR_CACHE"].upper() == 'TRUE'

    configuration_data = BackupObject("configuration_data.json", json=True)
    default_scoring_script = BackupObject("default_scoring.py", scoring_location)
    empty_scoring_script = BackupObject("empty_scoring.py", scoring_location)


    @classmethod
    def _verify_cache(cls):
        if not os.path.exists(cls.cache_location):
            os.mkdir(cls.cache_location)
        else:
            if cls.clear_cache:
                shutil.rmtree(cls.cache_location)
                os.mkdir(cls.cache_location)


    @classmethod
    def _verify_saves(cls):
        if not os.path.exists(cls.save_location):
            os.mkdir(cls.save_location)
        cls.configuration_data.safely_restore()
        cls.default_scoring_script.safely_restore()
        cls.empty_scoring_script.safely_restore()


    @classmethod
    def _verify_data(cls):
        files = [cls.old_data, cls.blacklist_data, cls.scored_data]
        for i in files:
            i.verify()


    @classmethod
    def clean_cache(cls):
        files = os.listdir(cls.cache_location)
        files = [cls.cache_location+i for i in files]
        files = sorted(files, key=os.path.getctime)
        while len(files) > 100:
            os.remove(files[0])
            files.pop(0)
            

    @classmethod
    def verify_files(cls):
        cls._verify_cache()
        cls._verify_saves()
        cls._verify_data()
