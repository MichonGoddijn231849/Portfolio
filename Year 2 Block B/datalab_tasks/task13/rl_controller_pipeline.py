"""
This script demonstrates a pipeline for using a trained PPO (Proximal Policy Optimization) 
model to navigate an OT2Env environment and inoculate root tips at specified zones on a plate. 
The main steps are:

1. Load a trained PPO model from a file (MODEL_PATH).
2. Initialize the OT2Env environment with rendering enabled and a maximum step limit.
3. Acquire an image of the plate from the environment (env.get_plate_image).
4. Process the image (process_single_image) to locate root tips in pixel coordinates.
5. Convert each pixel coordinate to robot coordinates (via pixel_to_robot_coords).
6. For each zone:
   a. Set the goal position in the environment and reset.
   b. Let the PPO model select actions at each timestep.
   c. Check the distance to the goal and stop when threshold is reached or max steps/truncation occurs.
   d. Inoculate the tip with repeated dispense actions if the goal is successfully reached.
7. Display the final image with tips for visualization and close the environment.

Configuration and constants (PLATE_SIZE_MM, PLATE_ORIGIN, X_BOUNDS, etc.) define the 
workspace and coordinate transformations between pixels and the robot's coordinate system.
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt

from stable_baselines3 import PPO
from ot2_gym_wrapper import OT2Env  # Environment that stops when distance < 0.001
from task_8 import process_single_image  # Your CV pipeline

##############################################################################
# Config
##############################################################################
PLATE_SIZE_MM = 150.0
PLATE_ORIGIN = [0.10775, 0.088 - 0.026, 0.057]  # => [0.10775, 0.062, 0.057]
X_BOUNDS = (-0.1872, 0.2531)
Y_BOUNDS = (-0.1711, 0.2201)
Z_BOUNDS = (0.1691, 0.2896)

DISTANCE_THRESHOLD = 0.001   # 1 mm
MAX_STEPS_PER_TIP = 2000

# Path to a trained PPO model file
MODEL_PATH = r"C:\Users\Michon\Documents\GitHub\2024-25b-fai2-adsai-MichonGoddijn231849\datalab_tasks\task11\models\dkj26bvp\best_model.zip"

def pixel_to_robot_coords(px, py, cropped_w_px):
    """
    Converts a pixel coordinate (px, py) from the plate image to the robot's 
    coordinate system (x, y, z) in meters. The function applies a scaling factor 
    derived from plate size in millimeters (PLATE_SIZE_MM) and the width of the 
    cropped image (cropped_w_px). The z-coordinate is chosen as the lower Z bound 
    for simplicity, but can be modified as needed. Finally, all coordinates are 
    clamped to the valid workspace bounds.

    Args:
        px (float): Pixel x-coordinate.
        py (float): Pixel y-coordinate.
        cropped_w_px (float): Width of the cropped plate image in pixels, used 
                              to determine mm/px scaling.

    Returns:
        list of float: [rx, ry, rz], the robot coordinates in meters, clamped to 
                       the defined workspace bounds.
    """
    scale_mm_per_px = PLATE_SIZE_MM / float(cropped_w_px)
    x_mm = px * scale_mm_per_px
    y_mm = py * scale_mm_per_px

    x_m = x_mm / 1000.0
    y_m = y_mm / 1000.0

    rx = PLATE_ORIGIN[0] + x_m
    ry = PLATE_ORIGIN[1] + y_m
    rz = Z_BOUNDS[0]  # By default, take the lower bound of the Z range

    # Clamp the coordinates within the defined bounds
    rx = np.clip(rx, X_BOUNDS[0], X_BOUNDS[1])
    ry = np.clip(ry, Y_BOUNDS[0], Y_BOUNDS[1])
    rz = np.clip(rz, Z_BOUNDS[0], Z_BOUNDS[1])

    return [rx, ry, rz]

def inoculate_tip(env, steps=10, sleep_time=0.05):
    """
    Conducts an inoculation sequence by sending dispense=1 commands to the environment 
    multiple times, with zero velocity. This allows a visual indication of dispensing 
    in the simulation (e.g., PyBullet).

    Args:
        env (OT2Env): The simulation environment instance.
        steps (int, optional): Number of dispensing steps. Defaults to 10.
        sleep_time (float, optional): Delay in seconds between dispense actions. Defaults to 0.05.
    """
    print("    => Starting multi-step inoculation sequence...")
    for i in range(steps):
        velocity_action = [0.0, 0.0, 0.0]   # No movement
        sim_action = velocity_action + [1] # 4th index => 'dispense=1'
        env.sim.run([sim_action])

        # Sleep briefly for rendering
        time.sleep(sleep_time)
    print("    => Finished inoculation steps.\n")

def main():
    """
    The main function orchestrates the following:
      1. Load the trained PPO model.
      2. Initialize the OT2Env environment (with rendering).
      3. Capture or retrieve a plate image from the environment.
      4. Process the image (process_single_image) to identify tip positions in pixel coords.
      5. For each tip's coordinates:
         a. Convert them to robot coordinates.
         b. Set the environment's target position, then reset.
         c. Run the PPO policy until the distance threshold or max steps is reached.
         d. Inoculate the tip if within the threshold.
      6. Display the final pipeline image with tips, then close the environment.
    """
    # 1) Load PPO model
    model = PPO.load(MODEL_PATH)
    print(f"Loaded PPO from: {MODEL_PATH}")

    # 2) Create the environment
    env = OT2Env(render=True, max_steps=MAX_STEPS_PER_TIP)

    # 3) Acquire the plate image
    image_path = env.get_plate_image()
    print(f"Plate image: {image_path}")

    # 4) Run CV pipeline => zone_points
    zone_points = process_single_image(image_path, exclude_top_px=500, visualize=False)

    # Assume final cropped plate is about 2000 pixels wide
    cropped_w_px = 2000.0

    print("DEBUG: zone_points in pixel coords =>", zone_points)

    all_distances = []
    all_rewards = []

    # 5) For each zone, move & inoculate
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

        # Set the environment's target, then reset
        env.target_position = np.array(goal_robot, dtype=np.float32)
        obs, _ = env.reset()

        total_reward = 0.0

        for step in range(MAX_STEPS_PER_TIP):
            # RL model picks the next action
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)

            total_reward += reward
            all_rewards.append(reward)

            current_distance = info.get("current_distance", None)
            all_distances.append(current_distance)

            print(
                f"Step {step}: dist={current_distance:.4f}, "
                f"reward={reward:.4f}, action={action}"
            )

            # Check threshold => 1 mm
            if current_distance < DISTANCE_THRESHOLD:
                print(
                    f"  => Reached tip zone {zone_id} at step={step}, "
                    f"distance={current_distance:.4f}, total_reward={total_reward:.4f}"
                )
                # Inoculate the root tip (multi-step)
                inoculate_tip(env, steps=10, sleep_time=0.05)
                break

            if done or truncated:
                print(
                    f"  => Env done or idle-limit. "
                    f"Distance={current_distance:.4f}, total_reward={total_reward:.4f}\n"
                )
                break

            time.sleep(0.1)

    # 6) Visualize the final pipeline with tips
    print("\n-- Now showing final pipeline w/ tips --")
    process_single_image(image_path, exclude_top_px=500, visualize=True)

    # Close the environment
    env.close()
    print("Finished all zones.")

if __name__ == "__main__":
    main()
