from typing import Callable, Literal
from urllib.error import HTTPError
import urllib.request as u
import threading as th
from PIL import Image
import queue as q
import time as t
import os

from data_types import ImageRequest
from resources import ResourceManager

class ImageLoader:
    def __init__(self):
        self.images_queue: q.Queue[ImageRequest] = q.Queue(50)
        self.image_thread: th.Thread|None = None


    def _thread(self):
        while not self.images_queue.empty():
            image = self.images_queue.get()

            if ((time_wait:=t.perf_counter() - image.time_made) < 0.1):
                t.sleep(time_wait)

            if os.path.isfile(image.image_full_name):
                image.callback(image.image_full_name, True)
                continue

            try:
                u.urlretrieve(image.image_url, image.image_full_name)
            except HTTPError as e:
                print(f"Because: {e.reason} ({e.code}), now {image.image_full_name} failed, and now we have to use a default image.")
                image.callback(ResourceManager.default_image, True)
                continue

            image.callback(image.image_full_name, False)


    def update(self) -> None:
        # If there is nothing to do, ignore
        if self.images_queue.empty(): return

        # If there is a thread running, ignore
        if (
            self.image_thread != None and 
            self.image_thread.is_alive()
        ): return

        # If we are in demand of a thread,
        # create one, and start it.
        self.image_thread = th.Thread(target=self._thread, name="Image Loader Thread")
        self.image_thread.start()


    def __call__(self, time_made: float | Literal["default"], image_url: str, image_full_name: str, callback: Callable[[str], None]) -> None:
        if time_made.upper() == "DEFAULT":
            time_made = t.perf_counter()
        
        appendable: ImageRequest = ImageRequest(time_made, image_url, image_full_name, callback)
        self.images_queue.put(appendable)
        return Image.open(ResourceManager.default_image)
    