from typing import Callable
from background_tasks import BackgroundTasks
from utils import Resources, ProcessObject
import customtkinter as ct
from data_types import Car
import webbrowser as web
from PIL import Image

class CarItem(ct.CTkFrame):
    def __init__(self, 
                 *args, 
                 master: ct.CTkBaseClass, 
                 data: Car, 
                 process: ProcessObject, 
                 tasks: BackgroundTasks, 
                 finished: Callable, 
                 is_black_listed: bool,
                 add_blacklist: Callable[[int], None],
                 remove_blacklist: Callable[[int], None],
                 **kwargs):
        super().__init__(*args, master=master, **kwargs)

        self.data = data
        self.process = process
        self.tasks = tasks
        self.photo = None
        self.finished = finished

        self.add_blacklist = add_blacklist
        self.remove_blaclist = remove_blacklist

        print(f"New car discovered! {self.data.make} {self.data.model} {self.data.makeYear} {self.data.sellerType}")
        self._init_ui(is_black_listed)
    

    def _crop_image(self, image: Image.Image):
        width, height = image.size
        if width == height:
            return image
        offset  = int(abs(height-width)/2)
        if width>height:
            image = image.crop([offset,0,width-offset,height])
        else:
            image = image.crop([0,offset,width,height-offset])
        return image


    def _isolate_image_name(self, id: str):
        found_start: bool = False
        returnable: str = ""
        for i in id:
            if not (found_start or i.isnumeric()): continue
            returnable+=i
            found_start=True
        return returnable


    def _get_image_thread(self, image_full_name: str, already_existed: bool):
        # Open Image
        opened_image: Image.Image = Image.open(image_full_name)
        
        if not already_existed:
            # Crop Image
            opened_image = self._crop_image( opened_image )
            # Re-save Image
            opened_image.save(image_full_name)
            # Set the Image
            
        self.ctk_image = ct.CTkImage(
            dark_image=opened_image, 
            light_image=opened_image, 
            size=(200, 200)
        )
        while not self.photo: pass
        self.photo.configure(require_redraw=True, image=self.ctk_image)
        self.finished()


    def _solve_image(self) -> Image.Image:
        if self.data.photo == None:
            self.finished()
            return Image.open(Resources.default_image)
        image_name = self._isolate_image_name(self.data.photo)
        image_full_name = f"{Resources.cache_location}{image_name}"

        return self.tasks.images("default", self.data.photo, image_full_name, self._get_image_thread)


    def _register_image(self) -> None:
        opened_image = self._solve_image()
        self.ctk_image = ct.CTkImage(
            dark_image=opened_image, 
            light_image=opened_image, 
            size=(200, 200)
        )


    def blacklist_toggle(self) -> None:
        if self.blacklist_checkbox.get():
            self.add_blacklist(self.data.id)
        else:
            self.remove_blaclist(self.data.id)


    def _init_ui(self, is_black_listed: bool):
        # self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=6)

        self.configure(fg_color="gray18" if not self.data.newCar else "gray22")

        self.process.complete_process()

        # Resolve the image
        self._register_image()
        self.photo = ct.CTkLabel(
            master=self, 
            image=self.ctk_image, 
            text="", 
            anchor=ct.W
        )
        self.photo.grid(column=0, row=0, rowspan=2, sticky=ct.NSEW)


        quotations = "\""
        self.title = ct.CTkLabel(
            master=self, 
            text=f"{self.data.make} {self.data.model} {f'{quotations}{self.data.trim}{quotations} ' if self.data.trim else ''}{self.data.makeYear} ({self.data.city}, {self.data.state})", 
            font=ct.CTkFont('Trebuchet MS', size=20), 
            compound=ct.LEFT,
            bg_color=("gray90", "gray24"),
            corner_radius=10
        )
        self.title.grid(column=1, row=0, sticky=ct.NSEW)

        self.content = ct.CTkFrame(master=self, fg_color="transparent")
        self.content.grid(column=1, row=1, sticky=ct.NSEW, padx=10, pady=10)

        self.content.rowconfigure((0, 1, 2), weight=1)
        self.content.columnconfigure((0, 1, 2), weight=1)

        self.url_button = ct.CTkButton(master=self.content, text="Open in Browser", command=(lambda : web.open(f"https://cars.ksl.com/listing/{self.data.id}")))
        self.url_button.grid(row=0, column=0)

        self.blacklist_checkbox = ct.CTkCheckBox(master=self.content, text="Blacklist Item", command=self.blacklist_toggle, variable=ct.IntVar(value=is_black_listed))
        self.blacklist_checkbox.grid(row=2, column=0)

        self.score_label = ct.CTkLabel(master=self.content, text=f"Score: {self.data.score}", font=ct.CTkFont("Trebuchet MS", size=20))
        self.score_label.grid(row=2, column=1)

        self.price_label = ct.CTkLabel(master=self.content, text=f"Price: ${self.data.price}", font=ct.CTkFont("Trebuchet MS", size=20))
        self.price_label.grid(row=0, column=1)
 
        self.dealer = ct.CTkLabel(master=self.content, text=self.data.sellerType, font=ct.CTkFont("Trebuchet MS", size=20))
        self.dealer.grid(row=0, column=2)

        self.process.complete_process()
