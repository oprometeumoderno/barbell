import gym
import numpy as np
import Cartpole  # NOQA

from scipy.optimize import minimize


x0 = np.zeros(4)


def run_cartpole(weights, render=False):
    env = gym.make('pendulum1-v0')
    env.set_definition_file('cartpole_definition.yaml')
    env.reset()
    observation = np.zeros(4)
    done = False
    total_reward = 0
    while not done:
        if np.sum(weights * observation) <= 0:
            action = 0
        else:
            action = 1
        observation, reward, done = env.step(action)
        total_reward += reward
    return -1 * total_reward


result = minimize(run_cartpole, x0, method="Nelder-Mead")
