# import os

# from ament_index_python.packages import get_package_share_directory


# from launch import LaunchDescription
# from launch.actions import IncludeLaunchDescription, TimerAction
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# from launch.substitutions import Command
# from launch.actions import RegisterEventHandler
# from launch.event_handlers import OnProcessStart

# from launch_ros.actions import Node



# def generate_launch_description():


#     # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
#     # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

#     package_name='articubot_one' #<--- CHANGE ME

#     rsp = IncludeLaunchDescription(
#                 PythonLaunchDescriptionSource([os.path.join(
#                     get_package_share_directory(package_name),'launch','rsp.launch.py'
#                 )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true'}.items()
#     )

#     # joystick = IncludeLaunchDescription(
#     #             PythonLaunchDescriptionSource([os.path.join(
#     #                 get_package_share_directory(package_name),'launch','joystick.launch.py'
#     #             )])
#     # )


#     twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux.yaml')
#     twist_mux = Node(
#             package="twist_mux",
#             executable="twist_mux",
#             parameters=[twist_mux_params],
#             remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')]
#         )

    


#     robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])

#     controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')

#     controller_manager = Node(
#         package="controller_manager",
#         executable="ros2_control_node",
#         parameters=[{'robot_description': robot_description},
#                     controller_params_file]
#     )

#     delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

#     diff_drive_spawner = Node(
#         package="controller_manager",
#         executable="spawner",
#         arguments=["diff_cont"],
#     )

#     delayed_diff_drive_spawner = RegisterEventHandler(
#         event_handler=OnProcessStart(
#             target_action=controller_manager,
#             on_start=[diff_drive_spawner],
#         )
#     )

#     joint_broad_spawner = Node(
#         package="controller_manager",
#         executable="spawner",
#         arguments=["joint_broad"],
#     )

#     delayed_joint_broad_spawner = RegisterEventHandler(
#         event_handler=OnProcessStart(
#             target_action=controller_manager,
#             on_start=[joint_broad_spawner],
#         )
#     )


#     # Code for delaying a node (I haven't tested how effective it is)
#     # 
#     # First add the below lines to imports
#     # from launch.actions import RegisterEventHandler
#     # from launch.event_handlers import OnProcessExit
#     #
#     # Then add the following below the current diff_drive_spawner
#     # delayed_diff_drive_spawner = RegisterEventHandler(
#     #     event_handler=OnProcessExit(
#     #         target_action=spawn_entity,
#     #         on_exit=[diff_drive_spawner],
#     #     )
#     # )
#     #
#     # Replace the diff_drive_spawner in the final return with delayed_diff_drive_spawner



#     # Launch them all!
#     return LaunchDescription([
#         rsp,
#         # joystick,
#         twist_mux,
#         delayed_controller_manager,
#         delayed_diff_drive_spawner,
#         delayed_joint_broad_spawner
#     ])


import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    RegisterEventHandler,
    DeclareLaunchArgument,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch.event_handlers import OnProcessStart

from launch_ros.actions import Node


def generate_launch_description():

    package_name = "articubot_one"

    #
    # Launch Arguments
    #
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_ros2_control = LaunchConfiguration("use_ros2_control")

    #
    # Generate robot_description directly from xacro
    #
    pkg_path = get_package_share_directory(package_name)

    xacro_file = os.path.join(
        pkg_path,
        "description",
        "robot.urdf.xacro",
    )

    robot_description = Command(
        [
            "xacro ",
            xacro_file,
            " use_ros2_control:=",
            use_ros2_control,
            " sim_mode:=",
            use_sim_time,
        ]
    )

    #
    # Robot State Publisher
    #
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": use_sim_time,
            }
        ],
    )

    #
    # Twist Mux
    #
    twist_mux_params = os.path.join(
        pkg_path,
        "config",
        "twist_mux.yaml",
    )

    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        parameters=[twist_mux_params],
        remappings=[
            ("/cmd_vel_out", "/diff_cont/cmd_vel_unstamped")
        ],
    )

    #
    # ros2_control
    #
    controller_params_file = os.path.join(
        pkg_path,
        "config",
        "my_controllers.yaml",
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
            },
            controller_params_file,
        ],
    )

    delayed_controller_manager = TimerAction(
        period=2.0,
        actions=[controller_manager],
    )

    #
    # Joint State Broadcaster
    #
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
        output="screen",
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    #
    # Diff Drive Controller
    #
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
        output="screen",
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    return LaunchDescription(
        [

            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
            ),

            DeclareLaunchArgument(
                "use_ros2_control",
                default_value="true",
            ),

            rsp,

            twist_mux,

            delayed_controller_manager,

            delayed_joint_broad_spawner,

            delayed_diff_drive_spawner,
        ]
    )