from abc import ABC, abstractmethod
from typing import List
import cv2
import numpy as np
import pathlib
import os

class InterfaceVideoCreator(ABC):
    def __init__(self):
        self.frames = []

  
    @abstractmethod
    def add_frame(self, frames):
        pass

    @abstractmethod
    def save_video(self, filename):
        pass

    @abstractmethod
    def save_frame(self, frame, filename):
        pass

class VideoCreator(InterfaceVideoCreator):
    def __init__(self, filepath):
        super().__init__()
        self.fullfilename = pathlib.Path(filepath) if isinstance(filepath, str) else filepath
        if self.fullfilename.suffix != ".mp4":
            self.fullfilename = self.fullfilename.with_suffix(".mp4")
        

    def add_frame(self, frame: np.ndarray):
        frame = frame.astype(np.uint8)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = np.transpose(frame, (1, 0, 2))
        self.frames.append(frame)

    import os

    def save_video(self):
        height, width, layers = self.frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        # Create the folder if it doesn't exist
        folder_path = str(self.fullfilename.parent)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        video = cv2.VideoWriter(filename=str(self.fullfilename), 
                                fourcc=fourcc, 
                                fps=5, 
                                frameSize=(width, height))
        for frame in self.frames:
            video.write(frame)
        cv2.destroyAllWindows()
        video.release()
        cv2.destroyAllWindows()

    def save_frame(self, frame, filename):
        cv2.imwrite(filename, frame)


