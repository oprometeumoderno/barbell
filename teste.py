import random

import gym
import FlappyBird  # noqa

env = gym.make('flappybird-v0')
env.set_definition_file('flappybird_definition.yaml')
env.reset()


while True:
    observation, reward, done = env.step(int(random.randint(0, 1)))
    if done:
        env.reset()
    env.render(mode='human')
