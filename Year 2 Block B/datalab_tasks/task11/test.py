"""
This script demonstrates how to:
1) Load a pre-trained PPO model from a saved file.
2) Initialize an OT2Env environment with custom display and maximum cycles.
3) Override the environment's target position with a randomly generated goal.
4) Roll out a policy in the environment, logging reward and distance information.
5) Terminate when the goal is reached or the environment signals done.
6) Optionally, examine the actions taken in the process.

Usage:
    - Make sure you have stable-baselines3 installed for PPO.
    - Update the model_path to the location of your trained PPO model.
    - Run this script to see the agent attempt to reach a randomly generated goal.
"""

import numpy as np
from stable_baselines3 import PPO
from ot2_gym_wrapper import OT2Env  # Custom environment module
import matplotlib.pyplot as plt
import time
import wandb  # Used for experiment tracking if desired

# ------------------------------------------------------------------------------
# Define position bounds for generating random goals
# ------------------------------------------------------------------------------
position_bounds = {
    "x": [-0.1872, 0.2531],
    "y": [-0.1711, 0.2201],
    "z": [0.1691, 0.2896]
}

def generate_random_goal(bounds):
    """
    Generates a random 3D position (x, y, z) within the provided bounding ranges.

    Args:
        bounds (dict): Dictionary containing 'x', 'y', and 'z' as keys. 
                       Each key maps to a [min_val, max_val].

    Returns:
        np.ndarray: Random 3D position within the specified bounds.
    """
    return np.array([
        np.random.uniform(bounds["x"][0], bounds["x"][1]),
        np.random.uniform(bounds["y"][0], bounds["y"][1]),
        np.random.uniform(bounds["z"][0], bounds["z"][1]),
    ])

# ------------------------------------------------------------------------------
# Path to the trained model
# ------------------------------------------------------------------------------
# Update this path to point to the correct location of your trained PPO model.
model_path = r"C:\Users\Michon\Documents\GitHub\2024-25b-fai2-adsai-MichonGoddijn231849\datalab_tasks\task11\models\dkj26bvp\best_model.zip"

# ------------------------------------------------------------------------------
# Load the trained model
# ------------------------------------------------------------------------------
model = PPO.load(model_path)

# ------------------------------------------------------------------------------
# Initialize the environment
# ------------------------------------------------------------------------------
# OT2Env is a custom environment from the 'ot2_gym_wrapper' module. We set:
#    display=True for any available visual rendering.
#    max_cycles=2000 as the maximum number of steps per episode.
#    idle_limit=100 to define how many idle steps are allowed (if used in the environment).
env = OT2Env(display=True, max_cycles=2000, idle_limit=100)

# ------------------------------------------------------------------------------
# Reset the environment and generate a random goal
# ------------------------------------------------------------------------------
obs, _ = env.reset()
random_goal = generate_random_goal(position_bounds)
env.target_position = random_goal  # Override the default target in the environment
print(f"Randomly Generated Goal: {random_goal}")

# ------------------------------------------------------------------------------
# Tracking variables for analysis
# ------------------------------------------------------------------------------
reward_history = []
distance_history = []
action_history = []
total_reward = 0

# ------------------------------------------------------------------------------
# Run the model for up to 2000 steps (or until goal is reached)
# ------------------------------------------------------------------------------
for step in range(2000):
    # Add a short delay to slow down the simulation and observe it
    time.sleep(0.1)  # 100ms delay per step

    # Use the loaded PPO model to predict the next action in a deterministic manner
    action, _ = model.predict(obs, deterministic=True)
    
    # Apply the action in the environment
    obs, reward, done, _, info = env.step(action)
    
    # current_distance may be stored in info by the environment
    current_distance = info.get("current_distance", None)
    distance_history.append(current_distance)
    action_history.append(action)
    total_reward += reward

    # Print step information for debugging and clarity
    print(f"Step {step + 1}: Action = {action}, Reward = {reward:.4f}, Distance = {current_distance:.4f}")

    # If the environment signals done, we conclude
    if done:
        print(f"Simulation ended at step {step + 1}. "
              f"Final Reward: {total_reward:.4f}, "
              f"Final Distance: {current_distance:.4f}")
        reward_history.append(total_reward)
        break

# ------------------------------------------------------------------------------
# After finishing, log all actions taken
# ------------------------------------------------------------------------------
print("\nActions Taken:")
for i, action in enumerate(action_history, 1):
    print(f"Step {i}: {action}")

# ------------------------------------------------------------------------------
# Close the environment to release resources
# ------------------------------------------------------------------------------
env.close()
