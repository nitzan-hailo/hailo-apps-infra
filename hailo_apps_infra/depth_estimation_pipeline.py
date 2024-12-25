import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import argparse
import multiprocessing
import numpy as np
import setproctitle
import cv2
import time
import hailo
from hailo_apps_infra.hailo_rpi_common import (
    get_default_parser,
    detect_hailo_arch,
)
from hailo_apps_infra.gstreamer_helper_pipelines import(
    QUEUE,
    SOURCE_PIPELINE,
    INFERENCE_PIPELINE,
    INFERENCE_PIPELINE_WRAPPER,
    TILING_PIPELINE_WRAPPER,
    RESIZE_PIPELINE,
    USER_CALLBACK_PIPELINE,
    DISPLAY_PIPELINE,
)
from hailo_apps_infra.gstreamer_app import (
    GStreamerApp,
    app_callback_class,
    dummy_callback
)



# -----------------------------------------------------------------------------------------------
# User Gstreamer Application
# -----------------------------------------------------------------------------------------------

# This class inherits from the hailo_rpi_common.GStreamerApp class
class GStreamerDepthEstimationApp(GStreamerApp):
    def __init__(self, app_callback, user_data):
        parser = get_default_parser()
        args = parser.parse_args()
        args.input = 'rpi'

        super().__init__(args, user_data)
        
        self.hef_path = os.path.join(self.current_path, '../resources/scdepthv3.hef')
        self.app_callback = app_callback
        self.batch_size = 8
        self.post_process_so = os.path.join(self.current_path, '../resources/libdepth_estimation.so')

        # Set the process title
        setproctitle.setproctitle("Hailo Depth Estimation App")

        self.create_pipeline()

    def get_pipeline_string(self):
        source_pipeline = SOURCE_PIPELINE(self.video_source, self.video_width, self.video_height)
        depth_estimation_pipeline = INFERENCE_PIPELINE(
            hef_path=self.hef_path,
            post_process_so=self.post_process_so,
            batch_size=self.batch_size)
        depth_estimation_tiling_pipeline = TILING_PIPELINE_WRAPPER(depth_estimation_pipeline, tiles_x=1, tiles_y=1, overlap_x=0, overlap_y=0)
        user_callback_pipeline = USER_CALLBACK_PIPELINE()
        display_pipeline = DISPLAY_PIPELINE(video_sink=self.video_sink, sync=False, show_fps=self.show_fps)
#        display_pipeline2 = DISPLAY_PIPELINE(video_sink=self.video_sink, sync=False, show_fps=self.show_fps, name="display2")
        pipeline_string = (
            f'{source_pipeline} ! '
            f'{depth_estimation_tiling_pipeline} ! '
            f'hailooverlay ! {user_callback_pipeline} ! '
            f'{display_pipeline}'
        )
        print(pipeline_string)
        return pipeline_string

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = app_callback_class()
    app_callback = dummy_callback
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
