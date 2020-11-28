import gym
import bikey.base
from math import inf, pi
import numpy as np
import os

# Properties of the motors/servos used in the bicycle robot, torques in
# Newton-meters

maxonEC90 = {
    "stallTorque": 4.940,
    "nominalTorque": 0.44,
    "limitedTorque": 0.4
}

maxonF2140 = {
    "stallTorque": 0.031,
    "nominalTorque": 0.012,
    "limitedTorque": 0.01
}

transmission_ratios = {
    "steering": 30,
    "bodyLeaning": 1,
    "propulsion": 1
}

_default_sim_config = {
    "initial_action": np.zeros((3,1)),
    "spacar_file": "bicycle",
    "output_sbd": True,
    "use_spadraw": False
}

class BicycleEnv(bikey.base.SpacarEnv):
    def __init__(self, simulink_file, working_dir = os.getcwd(),
                 create_from_template = False, template = "bicycle_template.slx",
                 in_template_dir = True, simulink_config =
                 _default_sim_config, matlab_params = '-desktop'):
        """
        This environment wraps the physics simulation of a scaled down bicycle.

        Keyword arguments:
        simulink_file -- The name of the simulink file that is used to run the
            simulation. This should not include the file's .slx extension. This
            file should be in the current working directory, and cannot be
            located in a nested directory due to the way the simulation
            software works.
        spacar_file -- The name of the spacar file that defines the physical
            properties of the bicycle. This should not include the file's .dat
            extension. This file must be in the current working directory, and
            cannot be located in a nested directory due to the way the
            simulation software works.
        matlab_params -- Parameters passed to Matlab during startup.
        """

        # define actions

        torque_limit_propulsion = \
            maxonEC90["limitedTorque"] * transmission_ratios["propulsion"]
        torque_limit_steering = \
            maxonEC90["limitedTorque"] * transmission_ratios["steering"]
        torque_limit_leaning = \
            maxonF2140["limitedTorque"] * transmission_ratios["bodyLeaning"]

        torque_limits = np.array([
            [torque_limit_steering],
            [torque_limit_leaning],
            [torque_limit_propulsion]],
            dtype = np.float32)

        action_space = gym.spaces.Box(
                low = -torque_limits,
                high = torque_limits,
                shape = (3, 1),
                dtype = np.float32)

        # define observations

        infinity = np.array([[inf], [inf], [inf], [inf], [inf], [inf]],
                            dtype = np.float32)

        # TODO: give a better description of the observations?
        observation_space = gym.spaces.Box(
                low = -infinity,
                high = infinity,
                shape = (6, 1),
                dtype = np.float32)

        config = _default_sim_config.copy()
        config.update(simulink_config)

        super().__init__(action_space, observation_space, simulink_file,
                         working_dir, create_from_template, template,
                         in_template_dir, config, matlab_params)

        # define rewards
        self.reward_range = (-inf, inf) #TODO

        # limits / at what point should the episode terminate?
        deg_to_rad = 2 * pi / 360
        leaning_limit = 20 * deg_to_rad # leaning angle of bicycle
        steering_limit = 50 * deg_to_rad # steering angle
        ub_leaning_limit = 30 * deg_to_rad # leaning angle of upper body

        self.limits =
            np.array([steering_limit, leaning_limit, ub_leaning_limit])

    def process_step(self, observations):
        reward = 1

        angles = abs(observations.flatten()[1:4])
        done = np.any(angles > self.limits)

        info = {}

        return (reward, done, info)
