"""
This module defines a simple PID (Proportional-Integral-Derivative) controller class
used for controlling a single variable system. The controller calculates a control
output based on the difference (error) between a setpoint and the current value,
and it keeps track of integral and derivative terms over time.

Typical usage:
    - Initialize the PIDController with desired kp, ki, kd, and optional setpoint.
    - Call the compute() method on each timestep, providing the current value 
      and the elapsed time (dt). 
    - Use the returned output to drive your control system (e.g., motor commands).
"""

class PIDController:
    def __init__(self, kp, ki, kd, setpoint=0):
        """
        Initializes the PID Controller with given gains and an optional setpoint.

        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
            setpoint (float, optional): The target value the PID tries to achieve. Defaults to 0.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        # Store the previous error for derivative calculation
        self.prev_error = 0
        
        # Integral term accumulates over time
        self.integral = 0
        
        # Anti-windup limit to prevent integral from growing too large
        self.max_integral = 1.0  

    def compute(self, current_value, dt):
        """
        Computes the control output based on the current system value and elapsed time.

        Args:
            current_value (float): The current measured value of the system.
            dt (float): Time step (seconds) since the last compute() call.

        Returns:
            float: The control output that incorporates proportional, integral, and derivative terms.
        """
        # Calculate the error between setpoint and current value
        error = self.setpoint - current_value
        
        # Update integral term and apply anti-windup
        self.integral += error * dt
        self.integral = max(min(self.integral, self.max_integral), -self.max_integral)
        
        # Derivative term: rate of change of error
        derivative = (error - self.prev_error) / dt if dt > 0 else 0

        # Combine P, I, and D components
        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        # Store current error for the next step
        self.prev_error = error

        # Return the control signal
        return output
