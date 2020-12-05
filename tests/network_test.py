import gym
import bikey.network.network_env
import numpy as np
import os


def main():
    env = gym.make('NetworkEnv-v0',
                   address = '127.0.0.1',
                   port = 65432,
                   env_name = 'BicycleEnv-v0',
                   simulink_file = 'simulation.slx',
                   copy_simulink = True,
                   copy_spacar = True)

    # input("Press <enter> to start test simulation.")

    obs = env.reset()
    action = np.array([[0, 0, 0.001]]).T
    done = False

    input("Press enter to start episode")

    while not done:
        results = env.step(action)
        print(results)
        done = results[2]

    return env

def action(i):
    return np.array([[i, i+1, i+2]]).T

if __name__ == "__main__":
    env = main()

    input("Press <enter> to end test.")
