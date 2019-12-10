import random

import gym
import Cartpole  # noqa
import AcroBot  # noqa
import FlappyBird  # noqa

env = gym.make('barbellAcrobot-v0')
env.set_definition_file('acrobot_definition.yaml')
env.reset()


while True:
    observation, reward, done  = env.step(1)
    if done:
        env.reset()
    env.render(mode='human')
