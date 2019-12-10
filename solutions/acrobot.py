import gym
import numpy as np
import AcroBot  # NOQA

from scipy.optimize import minimize


x0 = np.random.rand(7)


def run_cartpole(weights, render=False):
    env = gym.make('barbellAcrobot-v0')
    env.set_definition_file('acrobot_definition.yaml')
    env.reset()
    observation = np.zeros(6)
    done = False
    total_reward = 0
    while not done:
        if np.sum(weights * np.append(observation, [1])) <= 0:
            action = -1
        else:
            action = 1
        observation, reward, done = env.step(action)
        total_reward += reward
    return -1 * total_reward


result = minimize(run_cartpole, x0)
print(result)
