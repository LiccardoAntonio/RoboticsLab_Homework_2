# RoboticsLab 2025/2026
## Homework 2: Control your robot
-------------
# Overview

This repository contains the solution for Homework 2 of the Robotics Lab course.

The work is based on:
- `ros2_kdl_package`
- `ros2_iiwa`
- `aruco_ros`

The project includes:
- ROS 2 parameters loaded from YAML
- a launch file for `ros2_kdl_node`
- a null-space velocity controller
- an action server/client implementation
- a Gazebo world with an ArUco marker
- a vision-based controller
- a ROS 2 service bridge to move the marker in Gazebo

---

## Repository structure

```text
HW2/
├── aruco_ros/
├── ros2_kdl_package/
├── ros2_iiwa/
├── README.md
├── Joint_State_Plot.png
├── Joint_State_Plot_Null.png
├── Velocity_Commands_Plot.png
└── Velocity_Commands_Plot_Null.png
```

## Requirements

Tested on:

* Ubuntu 22.04
* ROS 2 Humble
* Gazebo / ros_gz
* Eigen / Orocos KDL

Install ROS 2 Humble and source it before building:
```bash
source /opt/ros/humble/setup.bash
```

## Workspace setup

Place the packages inside your ROS 2 workspace:
````bash
~/ros2\_ws/src/HW2/
````
Expected structure:
```
~/ros2\_ws/src/HW2/  
├── aruco\_ros  
├── ros2\_kdl\_package  
└── ros2\_iiwa
```
* * *

## Build

From the workspace root:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
  
colcon build \--packages-select \\  
  aruco \\  
  aruco\_msgs \\  
  aruco\_ros \\  
  iiwa\_description \\  
  iiwa\_bringup \\  
  external\_torque\_sensor\_broadcaster \\  
  impedance\_controller \\  
  ros2\_kdl\_package  
  
source ~/ros2\_ws/install/setup.bash
```
* * *

## 1\. Kinematic control

### 1.a ROS 2 parameters + YAML + launch

The node parameters are stored in:
```
ros2\_kdl\_package/config/args.yaml
```
and loaded through:
```
ros2\_kdl\_package/launch/ros2\_kdl.launch.py
```
To launch the node:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
ros2 launch ros2\_kdl\_package ros2\_kdl.launch.py
```
* * *

### 1.b Velocity controller and null-space velocity controller

To test the standard velocity controller, set in `ros2_kdl_package/config/args.yaml`:
```bash
ros2\_kdl\_node:  
  ros\_\_parameters:  
    traj\_duration: 2.0  
    acc\_duration: 0.5  
    total\_time: 2.0  
    trajectory\_len: 160  
    Kp: 7.0  
    lambda: 5.0  
    cmd\_interface: "velocity"  
    ctrl: "velocity\_ctrl"  
    end\_position: \[0.2, 0.0, 0.3\]  
    action\_server\_mode: false
```

Rebuild:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
colcon build \--packages-select ros2\_kdl\_package  
source ~/ros2\_ws/install/setup.bash
```
Then launch the simulation with the velocity command interface:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
  
export GZ\_SIM\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$GZ\_SIM\_RESOURCE\_PATH  
export IGN\_GAZEBO\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$IGN\_GAZEBO\_RESOURCE\_PATH  
  
ros2 launch iiwa\_bringup iiwa.launch.py \\  
  use\_sim:\=true \\  
  command\_interface:\=velocity \\  
  robot\_controller:\=velocity\_controller \\  
  gz\_args:\="-r ~/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/worlds/empty.world"
```

In another terminal:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
ros2 launch ros2\_kdl\_package ros2\_kdl.launch.py
```

To test the null-space controller, change only:
```bash
ctrl: "velocity\_ctrl\_null"
```

Rebuild and relaunch `ros2_kdl_package`.

* * *

### 1.c Action server / action client

To enable action server mode, set in `args.yaml`:
```bash
ros2\_kdl\_node:  
  ros\_\_parameters:  
    traj\_duration: 2.0  
    acc\_duration: 0.5  
    total\_time: 2.0  
    trajectory\_len: 160  
    Kp: 7.0  
    lambda: 5.0  
    cmd\_interface: "velocity"  
    ctrl: "velocity\_ctrl\_null"  
    end\_position: \[0.2, 0.0, 0.3\]  
    action\_server\_mode: true
```

Rebuild:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
colcon build \--packages-select ros2\_kdl\_package  
source ~/ros2\_ws/install/setup.bash
```

Run the simulation first:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
  
export GZ\_SIM\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$GZ\_SIM\_RESOURCE\_PATH  
export IGN\_GAZEBO\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$IGN\_GAZEBO\_RESOURCE\_PATH  
  
ros2 launch iiwa\_bringup iiwa.launch.py \\  
  use\_sim:\=true \\  
  command\_interface:\=velocity \\  
  robot\_controller:\=velocity\_controller \\  
  gz\_args:\="-r ~/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/worlds/empty.world"
```

Run the action server:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
ros2 launch ros2\_kdl\_package ros2\_kdl.launch.py
```

Run the action client:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
ros2 run ros2\_kdl\_package ros2\_kdl\_action\_client
```

* * *

## 2\. Vision-based control

### 2.a Gazebo world + ArUco detection

The ArUco model is placed under:
```
ros2\_iiwa/iiwa\_description/gazebo/models/arucotag
```
The world is:
```
ros2\_iiwa/iiwa\_description/gazebo/worlds/empty.world
```
To launch Gazebo with the marker world:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
  
export GZ\_SIM\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$GZ\_SIM\_RESOURCE\_PATH  
export IGN\_GAZEBO\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$IGN\_GAZEBO\_RESOURCE\_PATH  
  
ros2 launch iiwa\_bringup iiwa.launch.py \\  
  use\_sim:\=true \\  
  command\_interface:\=velocity \\  
  robot\_controller:\=velocity\_controller \\  
  gz\_args:\="-r ~/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/worlds/empty.world"
```

To start ArUco detection:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
  
ros2 run aruco\_ros single \--ros-args \\  
  \-p marker\_id:\=201 \\  
  \-p marker\_size:\=0.1 \\  
  \-p camera\_frame:\=iiwa/link\_7/camera \\  
  \-p reference\_frame:\=iiwa/link\_7/camera \\  
  \-p marker\_frame:\=aruco\_marker\_frame \\  
  \-r /image:\=/videocamera \\  
  \-r /camera\_info:\=/camera\_info
```

To verify pose publication:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
ros2 topic echo /aruco\_single/pose
```

* * *

### 2.b Vision-based controller

Set in `ros2_kdl_package/config/args.yaml`:
```bash
ros2\_kdl\_node:  
  ros\_\_parameters:  
    traj\_duration: 2.0  
    acc\_duration: 0.5  
    total\_time: 2.0  
    trajectory\_len: 160  
    Kp: 5.0  
    lambda: 0.1  
    cmd\_interface: "velocity"  
    ctrl: "vision\_ctrl"  
    end\_position: \[0.2, 0.0, 0.3\]  
    action\_server\_mode: false
```

Rebuild:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
colcon build \--packages-select ros2\_kdl\_package  
source ~/ros2\_ws/install/setup.bash
```

Launch the KDL node:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
ros2 launch ros2\_kdl\_package ros2\_kdl.launch.py
```

Then manually move the marker in Gazebo and observe the robot tracking behavior.

* * *

### 2.c Service to move the marker in Gazebo

The launch file `ros2_kdl.launch.py` also starts the service bridge for:
```
/world/default/set\_pose
```

To verify that the service exists:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
ros2 service list | grep set\_pose
```

To move the marker:
```bash
cd ~/ros2\_ws  
source /opt/ros/humble/setup.bash  
source ~/ros2\_ws/install/setup.bash  
  
ros2 service call /world/default/set\_pose ros\_gz\_interfaces/srv/SetEntityPose "{entity: {name: 'arucotag', id: 0, type: 2}, pose: {position: {x: 0.02, y: -0.53, z: 0.45}, orientation: {w: 0.15147, x: -0.69098, y: -0.15135, z: -0.69043}}}"
```

After the call:

-   the marker moves in Gazebo
    
-   `/aruco_single/pose` updates
    
-   the robot can continue reacting if the marker remains inside the camera field of view
    

* * *

## Plots

The repository includes the plots used for the comparison between the standard velocity controller and the null-space controller:

-   `Plot_Velocity_Commands.png`
    
-   `Plot:Velocity_Commands_Null.png`
    
-   `Plot_Joint_State.png`
    
-   `Plot_Joint_State_Null.png`
    

* * *

## Troubleshooting

### Marker appears gray / ArUco is not detected

Check that the marker texture is correctly referenced inside:
```
ros2\_iiwa/iiwa\_description/gazebo/models/arucotag/model.sdf
```
The texture path should point to:
```bash
<albedo\_map>model://arucotag/aruco-201.png</albedo\_map>
```

Also make sure the model path is exported before launching Gazebo:
```bash
export GZ\_SIM\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$GZ\_SIM\_RESOURCE\_PATH  
export IGN\_GAZEBO\_RESOURCE\_PATH\=$HOME/ros2\_ws/src/HW2/ros2\_iiwa/iiwa\_description/gazebo/models:$IGN\_GAZEBO\_RESOURCE\_PATH
```
### `ros2_kdl_node` waits for services

Make sure `iiwa_bringup` is already running before launching `ros2_kdl_package`.

### Marker moves outside the camera field of view

If the marker is moved too far, `aruco_ros` will stop publishing valid poses and the robot will stop reacting. Use the `set_pose` service to place it back into a visible pose.
