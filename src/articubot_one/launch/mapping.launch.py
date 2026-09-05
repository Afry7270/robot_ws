import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    articubot_pkg = get_package_share_directory("articubot_one")
    depthai_pkg = get_package_share_directory("depthai_ros_driver_v3")

    #
    # Robot
    #
    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                articubot_pkg,
                "launch",
                "launch_robot.launch.py",
            )
        ),
        launch_arguments={
            "use_sim_time": "false",
            "use_ros2_control": "true",
        }.items(),
    )

    #
    # OAK-D Driver
    #
    oak = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                depthai_pkg,
                "launch",
                "driver.launch.py",
            )
        ),
        launch_arguments={
            "name": "oak",
            "parent_frame": "base_link",
            "params_file": os.path.join(
                articubot_pkg,
                "config",
                "depthai_rtabmap.yaml",
            ),
            "use_rviz": "false",
            "rsp_use_composition": "false",
        }.items(),
    )

    #
    # RTAB-Map
    #
    rtabmap = Node(
        package="rtabmap_slam",
        executable="rtabmap",
        name="rtabmap",
        output="screen",
        parameters=[
            os.path.join(
                articubot_pkg,
                "config",
                "rtabmap.yaml",
            ),
            {
                "frame_id": "base_link",
                "subscribe_rgb": True,
                "subscribe_depth": True,
                "subscribe_rgbd": False,
                "subscribe_scan": False,
                "subscribe_scan_cloud": False,
                "subscribe_odom_info": False,
                "approx_sync": True,
            },
        ],
        remappings=[
            ("rgb/image", "/oak/rgb/image_raw"),
            ("rgb/camera_info", "/oak/rgb/camera_info"),
            ("depth/image", "/oak/stereo/image_raw"),
            ("odom", "/diff_cont/odom"),
        ],
    )

    #
    # Wait for camera to initialize
    #
    delayed_rtabmap = TimerAction(
        period=8.0,
        actions=[rtabmap],
    )

    return LaunchDescription(
        [
            robot,
            oak,
            delayed_rtabmap,
        ]
    )