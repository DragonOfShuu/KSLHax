import customtkinter as ct
import threading as th
import typing as t
import queue as q

from utils import ImageLoader

class BackgroundTasks():
    def __init__(self, master: ct.CTkBaseClass):
        self.bg_tasks = q.Queue(3)
        self.fg_tasks = q.Queue(3)
        self.images = ImageLoader()
        self.master = master

        self.running_tasks: list[th.Thread] = []

        self.start()
        

    def clean_running(self):
        self.running_tasks = [x for x in self.running_tasks if x.is_alive()]
        return self.running_tasks


    def update(self):
        if not self.bg_tasks.empty():
            self.update_bg()
        if not self.fg_tasks.empty():
            self.update_fg()


    def update_bg(self):
        self.clean_running()

        for _ in range(3):
            if self.bg_tasks.empty(): break

            gettable: tuple = self.bg_tasks.get()
            x = th.Thread(target=gettable[0], args=gettable[1])
            x.start()
            self.running_tasks.append(x)

    
    def update_fg(self):
        for _ in range(3):
            if self.fg_tasks.empty(): break
            gettable = self.fg_tasks.get()
            gettable[0](*gettable[1])


    def start(self):
        self.update()        
        self.images.update()
        # Start this same function again
        self.master.after(200, self.start)


    def run_in_main(self, new_fun: t.Callable, /, args: tuple = ()) -> t.Literal[True]:
        self.fg_tasks.put((new_fun, args))
        return True


    def __call__(self, new_fun: t.Callable, /, args: tuple = ()) -> t.Literal[True]:
        self.bg_tasks.put((new_fun, args))
        return True