# Project 8: Costmap Configuration and Autonomous Patrol
Reid Beckes, Jackson Newell, Ian Mattson, and Anders Smitterberg


# Introduction + Setup
- ROS2 distribution and OS
- How you setup the enviornment (ROS_DOMAIN_ID, model export, params file origin)
- Any setup challenges and how you resolved them


# Part 1 - Costmap Configuration
- Table of parameter values tried (inflation radius, cost_scaling_factor) and observed effect on path planning
- Labeled before/after RViz2 screenshots
- Explanation of the tradoff you made in choosing your final parameters
- Obstacle layer screenshot with real-time detection visible

# Part 2 - Keepout and Speed Filter Zones

## Physical Floor Markers

Blue tape marks both filter zones in front of the main door of EERC 722. The zone closest to the door (0–50 cm out) is the **keepout zone** chosen because someone opening the door may not see the robot and could step or trip on it. The band from 50–150 cm is the **speed restriction zone** (≤ 50% max speed), providing a safe buffer before the keepout area. both areas are the width of the door. This also has the benefit of making is very easy to draw the boundaries in software.

| Zone | Distance from door |
|------|--------------------|
| Keepout | 0 – 50 cm |
| Speed restriction | 50 – 150 cm |

### Overview — full keepout + speed zone extent
![Floor markers overview](figures/IMG_0209.jpg)
![Floor markers with door](figures/IMG_0204.jpg)

### Keepout zone boundary (0–50 cm from door)
![Keepout zone near door](figures/IMG_0207.jpg)
![Keepout and speed zone boundary at door](figures/IMG_0208.jpg)

### Speed zone outer boundary (150 cm from door)
![Speed zone outer corners](figures/IMG_0205.jpg)
![Speed zone outer corner](figures/IMG_0206.jpg)

### Keepout zone in costmap (RViz2)
![Keepout zone rendered as lethal cells in costmap](figures/keepout_in_costmap.png)

- Speed zone validation evidence (cmd_vel output or RViz2 velocity display)
- Explanation of how you created the masks (tool used, coordinate derivation)

# Part 3 - Patrol Script
- Waypoint table: ID, map-frame coordinates, brief description of location
- Description of your loop closure check implementation
- Terminal output from a patrol run (copy-paste the log)

# Part 4 - Patrol Execution and Analysis
- Link to patrol video (or embedded if commited directly)
- Recovery event description (what happened, Nav2's response, your mitigation)
- Drift analysis table and discussion
- Comparison to Project 3 dead-reckoning drift

# Usage Instructions

All commands are run from the workspace root (`proj8_ws/`). Source the workspace and set the robot model before running anything:

```bash
export TURTLEBOT3_MODEL=burger
export ROS_DOMAIN_ID=4
source install/setup.bash
```

### Terminal 1 — TurtleBot3 bringup (SSH into robot, run on the robot)
```bash
ros2 launch turtlebot3_bringup robot.launch.py
```

### Terminal 2 — Costmap filter servers (workstation)
```bash
ros2 launch src/config/filters_launch.py
```
Wait until you see `Managed nodes are active` before proceeding.

### Terminal 3 — Nav2 (workstation)
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=False \
  map:=src/maps/eerc722.yaml \
  params_file:=src/config/nav2_params.yaml
```

Once Nav2 is up, use RViz2's **2D Pose Estimate** to initialize AMCL before sending any navigation goals.

still need - How to run the patrol script