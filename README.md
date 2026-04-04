# Project 8: Costmap Configuration and Autonomous Patrol
Reid Beckes, Jackson Newell, Ian Mattson, and Anders Smitterberg Project 8


# Introduction + Setup

__Project introduction blurb here!__

This project is completed and tested in ROS2 Jazzy Jalisco on an Ubuntu 24.04 Noble Numbat PC.

Each Turtlebot3 in EERC 722 is assigned a static IP on a lab managed wireless router. Our group used Turtlebot Anchovy, which is assigned local IP address 32.80.100.108 and `ROS_DOMAIN_ID=8`. 

The testing enviornment is setup on a local PC by exporting the following parameter flags:
```
$ export ROS_DOMAIN_ID=8
$ export TURTLEBOT3_MODEL=burger
$ export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```
__!! Need param file origin and model export still !!__

- Any setup challenges and how you resolved them


# Part 1 - Costmap Configuration

### A. Identify baseline params

local costmap defaults:

inflation_radius = 0.5 cost_scaling_factor = 5.0

global costmap defaults:

inflation_radius = 0.5 cost_scaling_factor = 5.0


- Table of parameter values tried (inflation radius, cost_scaling_factor) and observed effect on path planning

| `inflation_radius` | `cost_scaling_factor` | Observed Effect |
| :---------: | :---------: | :---------: |
|  0.50  |  5.0  | __[Baseline]__ Collision with object  |
|  0.15  |  2.0  |  Success, meandered  |
|  0.30  |  2.0  |  Collision with object  |
|  0.45  |  2.0  |  Success, very straight path  |
|  0.15  |  3.5  |  Success, meandered and very close collision |
|  0.30  |  3.5  |  Collision with object  |
|  0.45  |  3.5  |  Collision with object  |
|  0.15  |  5.0  |  Success, meandered and very close collision  |
|  0.30  |  5.0  |  Success, meandered and very close collision  |
|  0.45  |  5.0  |  Collision with object  |

__Discussion on observed effects!__


- Labeled before/after RViz2 screenshots
(side by side screenshots of costmap with smallest and largest inflation radius, label each with param value)

![Figure 1](./figures/project8_part1_map_comparison.png)

Figure 1: Smallest and largest tested inflation radius costmaps in RViz

- Explanation of the tradeoff you made in choosing your final parameters


![Figure 2](./figures/costmap_tuned_0.15_inflation.png)

Figure 2: Tuned `inflation_radius` and `cost_scaling_factor` parameters.

- Obstacle layer screenshot with real-time detection visible


Default `obstacle_range` and `raytrace_range` :

```
raytrace_max_range: 3.0
raytrace_min_range: 0.0
obstacle_max_range: 2.5
obstacle_min_range: 0.0
```

Increased range params:
```
raytrace_max_range: 5.0
raytrace_min_range: 0.0
obstacle_max_range: 4.5
obstacle_min_range: 0.0
```

Decreased range params:
```
raytrace_max_range: 1.0
raytrace_min_range: 0.0
obstacle_max_range: 0.5
obstacle_min_range: 0.0
```

![Figure 3](./figures/obstacle_range_costmap.png)

Figure 3: Real-time object detection with __XXXX__ tuned param values



![Figure 4](./figures/project8_part1c_comparison.png)

Figure 4: Comparison of decreased, default, and increased `obstacle_max_range` and `raytrace_max_range` parameters. As 


# Part 2 - Keepout and Speed Filter Zones 
- Photo of physical floor markers
- Description of zone locations and why you chose them
- RViz2 screenshots: keepout cells in costmap, path routing around zone, goal rejection
-Speed zone validation evidence (cmd_vel output or RViz2 velocity display)
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
Step-by-step instructions for a grader to reproduce your patrol run from scratch, including:

- How to launch the Turtlebot3 bringup
- How to launch Nav2 with your params and filter servers
- How to run the patrol script