import gym
import Cartpole  # noqa

env = gym.make('pendulum1-v0')
env.reset()

while True:
    observation, reward, done = env.step(0)
    if done:
        env.reset()
    env.render()
