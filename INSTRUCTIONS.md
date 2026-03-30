# Project 8: Costmap Configuration and Autonomous Patrol

## EE5531 Introduction to Robotics

---
## Introduction

In this project you will move beyond using the ROS2 Navigation Stack as a black box and learn to configure it. You will tune the layered costmap that governs how Nav2 perceives the robot's environment, define spatial policy overlays that restrict where the robot may travel and how fast, and write a Python patrol script that drives the robot autonomously around a multi-waypoint loop — all on the physical TurtleBot3 in EERC 722.

This project builds directly on Project 7:

- You will reuse the **EERC 722 map** you created with SLAM Toolbox
- You will extend the **Nav2 parameter file** from that project rather than starting from scratch
- The patrol route will traverse the same physical space you already mapped

By the end of this project you will have hands-on experience with the parts of Nav2 that robotics engineers spend the most time tuning in real deployments.

---

## Learning Objectives

1. Understand the role of each layer in a Nav2 layered costmap
2. Tune inflation and obstacle layer parameters and observe their effect on path planning
3. Create costmap filter masks that define keepout zones and speed restriction zones
4. Configure the Nav2 `KeepoutFilter` and `SpeedFilter` costmap plugins
5. Write an autonomous patrol script using the `nav2_simple_commander` Python API
6. Deploy and evaluate a multi-waypoint patrol loop on a physical robot, including recovery from navigation failures
7. Analyze localization drift over repeated patrol cycles

---

## Team Structure

This project is completed in team up to four or on your own. All team members must make meaningful commits to the repository before the submission deadline. Graders will check the git log — commits that only add image files or cosmetic README changes do not count as meaningful contributions.

---

## AI Use Policy

Any use of AI tools (ChatGPT, Claude, Copilot, etc.) **must be thoroughly documented** in your README. For each section where AI was used, note:

- Which tool was used
- What prompt or query was given
- How you verified or modified the output

Undisclosed AI use is an academic integrity violation.

---

## Background

### Layered Costmaps

Nav2 represents the navigable environment as a **costmap** — a 2D grid where each cell holds a cost value from 0 (free) to 254 (lethal obstacle). The costmap is built by stacking independent **layers**, each contributing information from a different source:

| Layer | Purpose |
|-------|---------|
| `StaticLayer` | Reads the pre-built map (your `.pgm` file) as a fixed background |
| `ObstacleLayer` | Marks real-time obstacles detected by the LiDAR |
| `InflationLayer` | Expands obstacle cells outward with a cost gradient, keeping the robot away from walls |

Nav2 maintains two separate costmaps: the **global costmap** (used by the path planner, updated slowly) and the **local costmap** (used by the controller, updated at sensor rate). Each has its own layer stack configured in `nav2_params.yaml`.

The `InflationLayer` is the most consequential parameter to tune:

- `inflation_radius` — how far (in meters) obstacle costs spread outward. Larger = more clearance, fewer paths through tight spaces.
- `cost_scaling_factor` — how steeply cost decays with distance. Larger = sharper falloff, robot hugs walls more.

### Costmap Filters

**Costmap filters** are policy overlays that modify navigation behavior based on a separate mask image, independent of the sensor-detected obstacles. Nav2 ships with two filters relevant to this project:

- **`KeepoutFilter`** — marks regions as impassable. The planner will route around them; goals placed inside a keepout zone are rejected.
- **`SpeedFilter`** — limits the robot's maximum speed in designated regions. Useful for narrow doorways, areas with foot traffic, or near fragile equipment.

Both filters read from a **filter mask**: a `.pgm` image (same format as your map) where pixel values encode the filter behavior. The mask is served by a `filter_mask_server` node and accompanied by a `.yaml` metadata file. Both the global and local costmaps must have the filter plugin enabled to enforce the policy at both planning and execution time.

### nav2_simple_commander

`nav2_simple_commander` is the officially supported Python API for sending goals and waypoints to a running Nav2 stack. It wraps the Nav2 action servers in a clean, blocking interface:

```python
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

nav = BasicNavigator()
nav.waitUntilNav2Active()

nav.followWaypoints(waypoint_list)
while not nav.isTaskComplete():
    pass

result = nav.getResult()
if result == TaskResult.SUCCEEDED:
    print('Patrol complete')
```

This is the same API used in Nav2's own demos and in production deployments. You should not write raw action clients for this project.

---

## Equipment

- TurtleBot3 Burger with LDS-01/LDS-02 LiDAR
- Workstation with ROS2 Jazzy
- Floor tape (masking or gaffer) for marking keepout and speed zone boundaries
- Phone or camera for recording video evidence

---

## Instructions

### Preliminary: Environment Setup

You will use your EERC 722 map from Project 7 as the base map throughout this project. Copy `map_eerc722.yaml` and `map_eerc722.pgm` into your Project 8 repository under `maps/`.

---

### Part 1 — Costmap Layer Configuration

The goal of this part is to understand how costmap parameters affect the robot's planned paths and executable clearances in the real environment.

#### 1a. Identify your baseline

Copy the `nav2_params.yaml` from your Project 7 work (or from the standard TurtleBot3 navigation2 package) into `config/nav2_params.yaml`. Locate the `inflation_layer` configuration in both the global and local costmap sections. Record the baseline values for `inflation_radius` and `cost_scaling_factor`.

#### 1b. Tune the inflation layer

On the real robot, launch Nav2 with your baseline parameters:

```bash
# Terminal 1 — on TurtleBot3 (SSH)
ros2 launch turtlebot3_bringup robot.launch.py

# Terminal 2 — on workstation
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=False \
  map:=maps/map_eerc722.yaml \
  params_file:=config/nav2_params.yaml
```

In RViz2, set the **2D Pose Estimate** to initialize AMCL, then display the **Global Costmap** and **Local Costmap** overlays. Take a screenshot showing the inflated obstacle costs around the walls.

Now modify `inflation_radius` (try values between 0.15 m and 0.45 m) and `cost_scaling_factor` (try 2.0–5.0). For each configuration:

1. Relaunch Nav2 with the updated params
2. Send a navigation goal through a **narrow section** of the room (a doorway or tight corridor)
3. Observe whether the robot finds a path, refuses to plan, or clips the walls

**Required evidence:**

- Two RViz2 screenshots side-by-side showing the costmap with your smallest and largest `inflation_radius` values (label each with the parameter values)
- A screenshot showing a planned path through the narrow section in the configuration you chose as your final setting

#### 1c. Tune the obstacle layer

Locate the `obstacle_layer` in your params file. Adjust `obstacle_range` (detection distance) and `raytrace_range` (clearing distance). Observe in RViz2 how the local costmap responds when you stand near the robot.

**Required evidence:**

- One RViz2 screenshot showing the local costmap with a person or object within `obstacle_range`

---

### Part 2 — Keepout and Speed Filter Zones

#### 2a. Plan your zones

Choose two types of zones to mark in EERC 722:

1. **One keepout zone** — a region the robot must never enter (e.g., a storage area, a section near a door that swings open, a region near equipment)
2. **One speed restriction zone** — a region where the robot must slow to ≤ 50% of its maximum speed (e.g., a narrow doorway, a high-traffic corridor segment)

Sketch the zones on your environment drawing from Part 1. Record the approximate map-frame coordinates of each zone boundary — you will need these to draw the filter masks.

#### 2b. Mark the physical zones

Using floor tape, mark the boundaries of both zones on the floor of EERC 722. Take a **photo of the taped floor** clearly showing both zones. This photo must be committed to your repository and embedded in your README.

#### 2c. Create the filter masks

A filter mask is a `.pgm` image the same size and resolution as your map (`map_eerc722.pgm`). Pixels corresponding to zone boundaries are filled; all other pixels are white (free).

The simplest workflow: open your map `.pgm` in an image editor (GIMP, Paint, or a Python script using Pillow/OpenCV), paint the zone polygons black, and save as a new file.

Create two separate masks:

- `config/keepout_mask.pgm` — keepout zone pixels filled black (value 0); all other pixels white (value 255)
- `config/speed_mask.pgm` — speed zone pixels filled with a value encoding the speed limit (value 1 = active speed restriction; all other pixels 0)

Each mask needs a corresponding metadata file with the same origin, resolution, and frame as your base map:

```yaml
# config/keepout_mask.yaml
image: keepout_mask.pgm
resolution: 0.05
origin: [<same x as map_eerc722.yaml>, <same y>, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
mode: keepout
```

```yaml
# config/speed_mask.yaml
image: speed_mask.pgm
resolution: 0.05
origin: [<same x as map_eerc722.yaml>, <same y>, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
mode: speed
speed_limit: 0.15   # m/s — fill with your chosen limit
```

#### 2d. Configure the filter plugins in nav2_params.yaml

Add the `filter_mask_server` and `costmap_filter_info_server` nodes to your params file, and add the filter plugins to both the global and local costmap layer stacks. The Nav2 costmap filter documentation describes the required parameter block structure.

Add to your `nav2_params.yaml`:

```yaml
filter_mask_server:
  ros__parameters:
    use_sim_time: False
    frame_id: "map"
    topic_name: "/filter_mask"
    mask_topic: "/filter_mask"

costmap_filter_info_server:
  ros__parameters:
    use_sim_time: False
    filter_info_topic: "/costmap_filter_info"
    type: 0          # 0 = keepout, 1 = speed filter
    base: 0.0
    multiplier: 1.0
```

Add to each costmap's `plugins` list and corresponding parameter block:

```yaml
keepout_filter:
  plugin: "nav2_costmap_2d::KeepoutFilter"
  enabled: True
  filter_info_topic: "/costmap_filter_info"
```

You will need to run two separate `filter_mask_server` / `costmap_filter_info_server` instances (with distinct node names and topics) for the keepout and speed masks. Consult the Nav2 costmap filters tutorial for the complete multi-filter launch pattern.

#### 2e. Validate on the real robot

Launch the full Nav2 stack with filters enabled:

```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=False \
  map:=maps/map_eerc722.yaml \
  params_file:=config/nav2_params.yaml
```

Demonstrate each filter:

1. Send a navigation goal **through** the keepout zone. The robot must route around it.
2. Send a navigation goal **into** the keepout zone. Nav2 should reject the goal.
3. Send a navigation goal that routes the robot **through** the speed zone. Observe the robot slow down in RViz2's velocity display or via `ros2 topic echo /cmd_vel`.

**Required evidence:**

- Photo of the taped floor zones (committed to `figures/`)
- RViz2 screenshot showing the keepout zone rendered as lethal cells in the costmap
- RViz2 screenshot showing a path that routes around the keepout zone
- Terminal output or RViz2 screenshot showing a goal inside the keepout zone being rejected
- `ros2 topic echo /cmd_vel` terminal output (or RViz2 screenshot) showing reduced speed while traversing the speed zone

---

### Part 3 — Autonomous Patrol Script

Write a Python script `patrol/patrol_node.py` that drives the TurtleBot3 around a continuous patrol loop using `nav2_simple_commander`.

#### 3a. Define your waypoints

Choose at least **five waypoints** that form a loop around EERC 722, using coordinates from your `map_eerc722.yaml` map frame. At least one waypoint should require the planner to route near (but not through) your keepout zone, so that the filter is exercised during normal patrol.

Define waypoints as `PoseStamped` messages:

```python
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy

def make_pose(nav, x, y, yaw_deg):
    """Helper: return a PoseStamped in the map frame."""
    from math import radians, sin, cos
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    yaw = radians(yaw_deg)
    pose.pose.orientation.z = sin(yaw / 2)
    pose.pose.orientation.w = cos(yaw / 2)
    return pose
```

#### 3b. Implement the patrol loop

Your script must:

1. Initialize `BasicNavigator` and wait for Nav2 to become active
2. Execute the waypoint loop for a configurable number of cycles (accept `--cycles N` as a command-line argument; default 3)
3. After each waypoint, log the waypoint ID, result (succeeded / failed), and elapsed time
4. If a waypoint fails (Nav2 returns `TaskResult.FAILED` or `TaskResult.CANCELED`), log the failure with the waypoint ID and **continue to the next waypoint** rather than aborting the patrol
5. At the end of each full cycle, log the number of successful and failed waypoints
6. After all cycles complete, log a summary and shut down cleanly

#### 3c. Loop closure check

At the end of each patrol cycle, record the robot's estimated pose by reading a single message from the `/amcl_pose` topic. Compare the pose at the start of the cycle (recorded when the robot was at waypoint 1) to the pose at the end (after returning near waypoint 1). Log the Euclidean distance between these poses as the **cycle drift**. This measures how much AMCL's estimate has shifted during one loop.

```bash
# Run the patrol (from your project root, with Nav2 already running)
ros2 run patrol patrol_node.py --cycles 3
```

**Required evidence:**

- `patrol/patrol_node.py` committed and functional
- Terminal output log from a real patrol run showing waypoint results and cycle drift values

---

### Part 4 — Patrol Execution and Analysis

#### 4a. Execute the full patrol on the real robot

With Nav2 running (using your tuned `nav2_params.yaml` and both filters active), run the patrol script for **three complete cycles**:

```bash
ros2 run patrol patrol_node.py --cycles 3
```

Record the run with a phone or camera. The video must show:

- The physical TurtleBot3 moving through the room
- At least one instance of the robot routing around the keepout zone or slowing in the speed zone
- At least one navigation event (failure, recovery, or re-routing)

Upload the video to your team's shared drive or a video hosting service and include the link prominently in your README. If the file is small enough (< 50 MB compressed), you may commit it directly to `videos/`.

#### 4b. Document a recovery event

During your patrol run, at least one waypoint will likely fail or trigger a recovery behavior (spin, backup, wait). In your README, describe:

- Which waypoint failed and why (robot blocked, poor localization, keepout zone edge case, etc.)
- What Nav2's recovery behavior did
- Whether the patrol resumed successfully after recovery
- What you would change in your waypoint placement or costmap parameters to prevent this failure

If no failure occurs during your three-cycle run, induce one deliberately: place an object in the robot's path to a waypoint and document what happens.

#### 4c. Drift analysis

From your loop closure check data (Part 3c), complete this table in your README:

| Cycle | Start pose (x, y) | End pose (x, y) | Drift (m) |
|-------|-------------------|-----------------|-----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

Discuss: Is the drift consistent across cycles? Does it accumulate, or does AMCL correct itself? How does this compare to the dead-reckoning drift you observed in Project 3?

---

## Deliverables

Submit by pushing to your team's **class GitHub repository** before the deadline.

### Repository Structure

```
proj8-nav-patrol/
├── README.md
├── maps/
│   ├── map_eerc722.yaml          # copied from Project 7
│   └── map_eerc722.pgm
├── config/
│   ├── nav2_params.yaml          # tuned params with filter plugins configured
│   ├── keepout_mask.pgm
│   ├── keepout_mask.yaml
│   ├── speed_mask.pgm
│   └── speed_mask.yaml
├── patrol/
│   └── patrol_node.py
├── figures/
│   ├── floor_markers.jpg         # photo of taped zones
│   ├── costmap_baseline.png
│   ├── costmap_tuned.png
│   ├── narrow_path.png
│   ├── keepout_costmap.png
│   ├── keepout_routing.png
│   ├── keepout_rejection.png
│   ├── speed_zone_cmdvel.png
│   └── patrol_rviz.png
└── videos/
    └── patrol_run.mp4            # or README link to hosted video
```

### README Requirements

Your README is the project report. Graders read it top to bottom — treat it as a complete lab report with embedded figures and terminal output.

#### 1. Introduction and Setup (3 pts)

- ROS2 distribution and OS
- How you set up the environment (ROS_DOMAIN_ID, model export, params file origin)
- Any setup challenges and how you resolved them

#### 2. Part 1 — Costmap Configuration (10 pts)

- Table of parameter values tried (inflation_radius, cost_scaling_factor) and observed effect on path planning
- Labeled before/after RViz2 screenshots
- Explanation of the tradeoff you made in choosing your final parameters
- Obstacle layer screenshot with real-time detection visible

#### 3. Part 2 — Keepout and Speed Filter Zones (12 pts)

- Photo of physical floor markers
- Description of zone locations and why you chose them
- RViz2 screenshots: keepout cells in costmap, path routing around zone, goal rejection
- Speed zone validation evidence (cmd_vel output or RViz2 velocity display)
- Explanation of how you created the masks (tool used, coordinate derivation)

#### 4. Part 3 — Patrol Script (12 pts)

- Waypoint table: ID, map-frame coordinates, brief description of location
- Description of your loop closure check implementation
- Terminal output from a patrol run (copy-paste the log)

#### 5. Part 4 — Patrol Execution and Analysis (10 pts)

- Link to patrol video (or embedded if committed directly)
- Recovery event description (what happened, Nav2's response, your mitigation)
- Drift analysis table and discussion
- Comparison to Project 3 dead-reckoning drift

#### 6. Usage Instructions (3 pts)

Step-by-step instructions for a grader to reproduce your patrol run from scratch, including:

- How to launch the TurtleBot3 bringup
- How to launch Nav2 with your params and filter servers
- How to run the patrol script

---

## Grading Rubric

| Component | Points |
|-----------|--------|
| **Costmap configuration:** parameter table, labeled before/after screenshots, tuning rationale, obstacle layer screenshot | 10 |
| **Keepout and speed filter zones:** floor photo, mask files committed, RViz2 routing and rejection screenshots, speed validation | 12 |
| **Patrol script:** `patrol_node.py` functional, ≥5 waypoints, failure handling, loop closure check | 12 |
| **Patrol execution:** video evidence, recovery event documented, drift analysis table and discussion | 10 |
| **Usage instructions:** reproducible step-by-step instructions | 3 |
| **Setup and introduction:** environment description, challenges | 3 |
| **Both team members have meaningful commits** | 2 |
| **AI use documented (or explicitly stated none used)** | 1 |
| **Total** | **53** |

---

## Tips

- **Set `use_sim_time:=False`.** This is the most common mistake when transitioning from Project 7's simulation runs. With `use_sim_time:=True`, the real robot's sensor data is timestamped incorrectly and Nav2 will appear unresponsive.
- **Initialize AMCL carefully.** Before running the patrol, spend 30 seconds manually driving the robot around the room to let the particle filter converge. A poor initial pose estimate is the most common cause of patrol failures.
- **Derive mask coordinates from the map YAML.** Your map origin (the `origin` field in `map_eerc722.yaml`) is the real-world position of the bottom-left pixel. Pixel (col, row) maps to world (x, y) as: `x = origin_x + col * resolution`, `y = origin_y + (height - row) * resolution`. Getting this wrong shifts your masks relative to the real obstacles.
- **Test each filter independently before combining.** Enable keepout only, validate it, then add the speed filter. Debugging two interacting filters at once is significantly harder.
- **Commit `nav2_params.yaml` early.** If the TurtleBot3 battery dies mid-session, your parameter work is preserved.
- **Keep patrol cycles short for initial testing.** Run one cycle first to verify the script logic before committing to a three-cycle run for the video.
- **For the recovery event:** if three full cycles complete without a failure, the patrol area is too easy. Add a waypoint in a tight space or temporarily narrow a corridor with a box.

---

## References

1. Nav2 Costmap 2D Configuration: https://docs.nav2.org/configuration/packages/configuring-costmaps.html
2. Nav2 Costmap Filters: https://docs.nav2.org/tutorials/docs/navigation2_with_keepout_filter.html
3. nav2_simple_commander API: https://docs.nav2.org/commander_api/index.html
4. TurtleBot3 Manual: https://emanual.robotis.com/docs/en/platform/turtlebot3/
5. Macenski, S. et al. (2020). *The Marathon 2: A Navigation System*. IROS 2020.