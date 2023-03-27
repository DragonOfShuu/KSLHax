from utils import ProcessObject, PaginationHelper, Resources
from .labeled_progress import LabeledProgress
from background_tasks import BackgroundTasks
from .input_box import InputBox
from .car_item import CarItem
from data_types import Car
import customtkinter as ct
from typing import Any
from itertools import chain
from dataclasses import asdict

class CarHolder(ct.CTkFrame, ProcessObject, PaginationHelper):
    def __init__(self, *args: Any, master: ct.CTkBaseClass, data: list[Car], progress: LabeledProgress | None, tasks: BackgroundTasks, **kwargs: Any):
        ct.CTkFrame.__init__(self, *args, master=master, **kwargs)
        ProcessObject.__init__(self, 6)
        PaginationHelper.__init__(self, data, 3)
        
        self.tasks = tasks
        self.progress = progress
        self.car_items: list[CarItem] = []
        self.page_changing_allowed: bool = False
        self.pending_blacklist: list[int] = []

        self._init_ui()

        self.page = 0


    def _init_ui(self):
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)

        self.content = ct.CTkFrame(master=self, corner_radius=0)
        self.content.grid(row=0, column=0, sticky=ct.NSEW)

        self.empty_buffer_text = ct.CTkLabel(master=self.content, text="BUFFER EMPTY", font=ct.CTkFont('Trebuchet MS', 48, weight='bold'), bg_color="transparent")

        # ==================
        # BOTTOM BAR CONTENT
        # ==================
        self.bottom_bar = ct.CTkFrame(master=self, corner_radius=0)

        self.bottom_bar.rowconfigure(0, weight=1)
        
        self.bottom_bar.columnconfigure((0, 1, 2), weight=1)

        self.left_button = ct.CTkButton(master=self.bottom_bar, width=28, text="←", command=self.left_button_clicked)
        self.left_button.grid(row=0, column=0, sticky=ct.W)

        self.bottom_center_content = ct.CTkFrame(master=self.bottom_bar, width=40, height=28, fg_color="transparent")
        self.bottom_center_content.grid(row=0, column=1, sticky=ct.NS)

        self.new_page_input = InputBox(master=self.bottom_center_content, width=48, acceptable=lambda x : x.isdigit(), enter_pressed=self.page_change)
        self.new_page_input.pack(side=ct.LEFT)

        self.all_pages_label = ct.CTkLabel(master=self.bottom_center_content, text=f"/ {self.page_count()}")
        self.all_pages_label.pack(side=ct.LEFT)

        self.right_button = ct.CTkButton(master=self.bottom_bar, width=28, text="→", command=self.right_button_clicked)
        self.right_button.grid(row=0, column=2, sticky=ct.E)

        self.bottom_bar.grid(row=1, column=0, sticky=ct.NSEW)


    @property
    def page(self) -> list[Car]:
        return self._page


    @page.setter
    def page(self, value):
        # If there is nothing on the new page, don't change at all
        if value < 0: return self.page
        if self.page_item_count(value) == -1: return self.page
        self._page = value
        self.amount_finished = 0
        self.deactivate_buttons()
        self.update_page()
        self.new_page_input.set(str(self._page+1))
        return self.page
    
    
    def page_change(self, _):
        self.page = int(self.new_page_input.get())-1
        self.new_page_input.set(str(self._page+1))

    def car_item_finished(self):
        self.amount_finished+=1
        if self.amount_finished==self.page_item_count(self.page):
            self.activate_buttons()
    

    def clear_content(self):
        while len(self.car_items) > 0:
            self.car_items[0].destroy()
            del self.car_items[0]


    def update_page(self):
        self.clear_content()

        if len(self.collection[self._page]) == 0:
            self.empty_buffer_text.pack(fill=ct.BOTH, expand=True)
            return;

        self.empty_buffer_text.pack_forget()
        for count,item in enumerate(self.collection[self._page]):
            item: Car
            self.car_items.append( CarItem(master=self.content, 
                                           data=item, 
                                           process = self, 
                                           tasks=self.tasks, 
                                           finished=self.car_item_finished,
                                           is_black_listed=item.id in self.pending_blacklist,
                                           add_blacklist=lambda x: self.pending_blacklist.append(x),
                                           remove_blacklist=lambda x: self.pending_blacklist.remove(x)
                                           ) 
                                 )
            self.car_items[count].pack(fill=ct.X, padx=5, pady=2)


    def left_button_clicked(self):
        self.page = self.page-1
    

    def right_button_clicked(self):
        self.page = self.page+1


    def deactivate_buttons(self):
        self.left_button.configure(state=ct.DISABLED)
        self.right_button.configure(state=ct.DISABLED)
        self.new_page_input.configure(state=ct.DISABLED)
        self.page_changing_allowed = False


    def activate_buttons(self):
        self.left_button.configure(state=ct.NORMAL)
        self.right_button.configure(state=ct.NORMAL)
        self.new_page_input.configure(state=ct.NORMAL)
        self.page_changing_allowed = True


    def process_completed(self):
        if self.progress != None:
            self.progress.set(self.percentage_complete)


    def apply_blacklist(self):
        if len(self.pending_blacklist) == 0: return

        black = Resources.blacklist_data.read()
        black.extend(self.pending_blacklist)
        Resources.blacklist_data.write(black)

        data: list[Car] = chain.from_iterable(self.collection)
        data = [asdict(i) for i in data if not i.id in self.pending_blacklist]
        Resources.scored_data.write(data)


    def cleanup(self):
        print("Did the exit")
        self.apply_blacklist()
