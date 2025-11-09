"""
This module defines a custom OpenAI Gym environment (OT2Env) that uses the Simulation 
class to simulate an agent (pipette) interacting in a 3D space. The agent's actions 
control the pipette's velocities along x, y, and z axes, and it aims to reach a 
randomly generated goal position within a bounding box.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from sim_class import Simulation

class OT2Env(gym.Env):
    """
    Custom Gym environment (OpenAI Gym v26+ style) integrating with a Simulation 
    that manages an OT-2 style robot pipette in 3D space.

    Attributes:
        render (bool): Flag to enable/disable rendering within the simulation.
        max_steps (int): Maximum number of steps before truncation.
        sim (Simulation): The underlying Simulation instance used for environment steps.
        action_space (gym.Space): Defines the valid range of actions for the agent.
        observation_space (gym.Space): Defines the shape/range of valid observations.
        steps (int): Tracks the current number of steps in the episode.
        goal_position (np.ndarray): The 3D coordinates of the target position.
    """

    def __init__(self, render=False, max_steps=1000):
        """
        Initializes the environment by creating a Simulation instance and defining
        the action and observation spaces.

        Args:
            render (bool, optional): Whether to enable the simulation's visualization.
            max_steps (int, optional): The maximum number of steps allowed per episode.
        """
        super(OT2Env, self).__init__()
        self.render = render
        self.max_steps = max_steps
        
        # Create the Simulation instance: 1 agent, optionally rendered
        self.sim = Simulation(num_agents=1, render=render)
        
        # Action space: control velocities for x, y, z axes in [-1.0, 1.0]
        # The final dimension (4th) for the simulation is reserved for no liquid dispensing (0).
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32)
        
        # Observation space: 
        # [pipette_x, pipette_y, pipette_z, goal_x, goal_y, goal_z]
        # This includes the current pipette position (3 values) plus the goal position (3 values).
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(6,), 
            dtype=np.float32
        )
        
        self.steps = 0
        self.goal_position = None

    def reset(self, seed=None, options=None):
        """
        Resets the environment at the start of each episode:
          1) Resamples a random goal position within [-0.5, 0.5] for x and y, and [0.0, 0.5] for z.
          2) Resets the Simulation.
          3) Returns the initial observation array:
             [pipette_x, pipette_y, pipette_z, goal_x, goal_y, goal_z]

        Args:
            seed (int, optional): Seed for the environment's random number generator.
            options (dict, optional): Additional reset options (unused here).

        Returns:
            observation (np.ndarray): The initial state (pipette pos + goal pos).
            info (dict): Additional info dictionary (empty here).
        """
        super().reset(seed=seed)
        
        # Sample a random goal within specified bounds
        self.goal_position = np.random.uniform(
            low=[-0.5, -0.5, 0.0],
            high=[0.5, 0.5, 0.5]
        )

        # Reset the simulation environment
        state = self.sim.reset(num_agents=1)
        
        # Dynamically fetch the robot ID key from the returned state dictionary
        robot_id_key = list(state.keys())[0]
        pipette_position = state[robot_id_key]["pipette_position"]

        # Create the observation array by concatenating pipette position + goal position
        observation = np.array(pipette_position + list(self.goal_position), dtype=np.float32)
        
        # Reset step count
        self.steps = 0
        return observation, {}

    def step(self, action):
        """
        Performs one step in the simulation by:
          1) Clipping the action to [-1.0, 1.0].
          2) Appending a 0 for the 4th dimension (e.g., no liquid dispensing).
          3) Running the simulation for one step with the scaled action.
          4) Computing the new observation, reward, termination, and truncation signals.

        Args:
            action (np.ndarray): Array of 3 floats (x, y, z velocities in [-1, 1]).

        Returns:
            observation (np.ndarray): [pipette_x, pipette_y, pipette_z, goal_x, goal_y, goal_z].
            reward (float): Negative distance to goal (closer = higher reward).
            terminated (bool): True if the pipette is within 0.01 of the goal.
            truncated (bool): True if the maximum number of steps has been reached.
            info (dict): Additional information about the episode (e.g., final reward).
        """
        # Ensure action is within the allowed range
        action = np.clip(action, -1.0, 1.0)
        
        # Append the 4th dimension as 0 (no dispensing), as required by Simulation
        scaled_action = list(action) + [0]
        
        # Run the simulation with the provided actions
        state = self.sim.run([scaled_action])
        
        # Retrieve the pipette's position from the simulation state
        robot_id_key = list(state.keys())[0]
        pipette_position = state[robot_id_key]["pipette_position"]
        
        # Create the new observation array
        observation = np.array(pipette_position + list(self.goal_position), dtype=np.float32)

        # Calculate the distance to the goal and use it for reward (negative distance)
        distance = np.linalg.norm(np.array(pipette_position) - np.array(self.goal_position))
        reward = -distance
        
        # Check termination condition: reached the goal if distance < 0.01
        terminated = distance < 0.01
        
        # Check truncation condition: exceeded the maximum allowed steps
        truncated = self.steps >= self.max_steps
        
        # If the episode ends, store final reward info
        info = {}
        if terminated or truncated:
            info = {"episode": {"r": reward}}
        
        # Increment step counter
        self.steps += 1
        
        # Return the standard Gym tuple
        return observation, reward, terminated, truncated, info

    def render(self, mode="human"):
        """
        Renders the environment. In this case, rendering is handled by the Simulation class 
        if render=True was set. This placeholder function exists for Gym compatibility.
        """
        pass

    def close(self):
        """
        Closes the Simulation instance. Properly releasing resources and stopping any 
        existing render windows.
        """
        self.sim.close()
