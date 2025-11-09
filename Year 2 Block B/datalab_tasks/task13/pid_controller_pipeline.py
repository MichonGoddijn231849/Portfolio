"""
This script demonstrates a full pipeline that:
1) Initializes a PID-controlled environment (PIDControlledEnv) with a maximum step limit.
2) Captures or retrieves an image of a plate (via the environment).
3) Processes the image using a CV pipeline (process_single_image) to obtain tip positions in pixel coordinates.
4) Converts each pixel coordinate to the robot coordinate space using known scale and offsets.
5) Uses the PID-controlled environment to move the pipette to each tip position in turn.
6) Performs an inoculation sequence at each tip (if reached) by repeatedly dispensing.

Key components:
    - PIDControlledEnv: Provides x, y, z PID controllers in a Gym-like environment.
    - process_single_image: The CV function from 'task_8.py' that identifies tip locations.
    - pixel_to_robot_coords: Converts from pixels to real-world (x, y, z) in meters, factoring in bounding/clamping.
    - inoculate_tip: Issues repeated dispense commands to the environment to simulate inoculation.
    - main: Orchestrates the entire pipeline, one zone at a time.
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt

from pid_controlled_env import PIDControlledEnv
from task_8 import process_single_image  # your CV pipeline

##############################################################################
# Config
##############################################################################
PLATE_SIZE_MM = 150.0
PLATE_ORIGIN = [0.10775, 0.062, 0.057]  # Same as your RL pipeline
X_BOUNDS = (-0.1872, 0.2531)
Y_BOUNDS = (-0.1711, 0.2201)
Z_BOUNDS = (0.1691, 0.2896)

DISTANCE_THRESHOLD = 0.001  # 1 mm
MAX_STEPS_PER_TIP = 2000    # Same as RL

def pixel_to_robot_coords(px, py, cropped_w_px):
    """
    Converts pixel coordinates (px, py) to the robot's (x, y, z) space in meters.
    The function applies scaling based on the plate size and clamps coordinates 
    according to specified workspace bounds (X_BOUNDS, Y_BOUNDS, Z_BOUNDS).

    Args:
        px (float): Pixel position along the x-axis (horizontal).
        py (float): Pixel position along the y-axis (vertical).
        cropped_w_px (float): The width of the cropped image in pixels, used to derive scaling.

    Returns:
        list of float: [rx, ry, rz], the robot coordinates in meters.
    """
    scale_mm_per_px = PLATE_SIZE_MM / float(cropped_w_px)
    x_mm = px * scale_mm_per_px
    y_mm = py * scale_mm_per_px

    x_m = x_mm / 1000.0
    y_m = y_mm / 1000.0

    rx = PLATE_ORIGIN[0] + x_m
    ry = PLATE_ORIGIN[1] + y_m
    rz = Z_BOUNDS[0]

    # Clamp to the valid workspace bounds
    rx = np.clip(rx, X_BOUNDS[0], X_BOUNDS[1])
    ry = np.clip(ry, Y_BOUNDS[0], Y_BOUNDS[1])
    rz = np.clip(rz, Z_BOUNDS[0], Z_BOUNDS[1])

    return [rx, ry, rz]

def inoculate_tip(env, steps=10, sleep_time=0.05):
    """
    Simulates an inoculation sequence by repeatedly issuing dispense=1 commands with zero velocity.

    Args:
        env (PIDControlledEnv): The environment controlling the pipette.
        steps (int, optional): Number of steps to spend dispensing. Defaults to 10.
        sleep_time (float, optional): Delay (seconds) between dispense actions. Defaults to 0.05.
    """
    print("    => Starting multi-step inoculation sequence...")
    for i in range(steps):
        velocity_action = [0.0, 0.0, 0.0]
        sim_action = velocity_action + [1]  # 4th => 'dispense=1'
        env.env.sim.run([sim_action])
        time.sleep(sleep_time)
    print("    => Finished inoculation steps.\n")

def main():
    """
    Main pipeline:
      1) Creates the PID environment with slow movement and specific idle limit.
      2) Retrieves/captures a plate image from the environment.
      3) Processes the image to find tip positions (in pixels).
      4) Converts each pixel coordinate to robot space.
      5) Moves the pipette to each tip using PID control.
      6) Inoculates if the goal is reached.
      7) Shows a final pipeline image with tips highlighted, then closes the environment.
    """
    # 1) Create your PID env w/ slow movement
    env = PIDControlledEnv(render=True, max_steps=MAX_STEPS_PER_TIP, idle_limit=300)

    # 2) Acquire the plate image
    image_path = env.env.get_plate_image()
    print(f"Plate image => {image_path}")

    # 3) CV => zone_points
    zone_points = process_single_image(image_path, exclude_top_px=500, visualize=False)
    cropped_w_px = 2000.0  # e.g., final cropped size

    print("DEBUG: zone_points in pixel coords =>", zone_points)

    all_distances = []

    # 4) For each zone, move & inoculate
    for zone_id in range(1, 6):
        tip = zone_points.get(zone_id)
        if tip is None:
            print(f"Zone {zone_id} => no tip found, skipping...\n")
            continue

        px, py = tip
        print(f"Zone {zone_id} => pixel=({px},{py}).")

        # Convert pixel->robot
        goal_robot = pixel_to_robot_coords(px, py, cropped_w_px)
        print(f" => Robot Goal => {goal_robot}\n")

        # 5) Set the environment's goal
        env.set_goal(goal_robot)

        # 6) Run until done
        reached = env.run_until_done(distance_threshold=DISTANCE_THRESHOLD)

        # 7) If reached => inoculate
        if reached:
            inoculate_tip(env, steps=10, sleep_time=0.05)
        else:
            print(f"Zone {zone_id} => Did NOT reach the tip (timeout or stuck).\n")

    # 8) (Optional) Show final pipeline with tips
    print("\n-- Now showing final pipeline w/ tips --")
    process_single_image(image_path, exclude_top_px=500, visualize=True)

    env.close()
    print("Finished all zones with slow PID controller.")

if __name__ == "__main__":
    main()
