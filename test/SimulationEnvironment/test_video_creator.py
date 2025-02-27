
from SimulationEnvironment.Renderer.VideoCreator import VideoCreator
import numpy as np
import os 

def test_video_creater_init():
    video_creater = VideoCreator(filepath="run_name")
    assert str(video_creater.fullfilename) == "run_name.mp4"

def test_video_creater_add_frame():
    video_creater = VideoCreator(filepath="run_name")
    video_creater.add_frame(frame=np.zeros((10, 10, 3)))
    assert len(video_creater.frames) == 1

def test_video_creater_save_video():
    video_creater = VideoCreator(filepath="run_name")
    video_creater.add_frame(frame=np.zeros((10, 10, 3)))
    video_creater.save_video()
    assert os.path.exists("run_name.mp4")
    os.remove("run_name.mp4")



