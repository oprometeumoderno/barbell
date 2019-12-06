import gym
import Henrique  # noqa

env = gym.make('henrique_hard-v0')
env.reset()

while True:
    observation, reward, done = env.step(0)
    if done:
        env.reset()
    env.render()
