import random
import numpy as np
import gym
from gym import spaces
from barbell_environment import BarbellWorld, BarbellViewer, BarbellStatistics
from barbell_utils import parse_file

DEG_TO_RAD = 0.0174533
RAD_TO_DEG = 57.2958
FPS = 50  # desired FPS rate


class Pendulum1(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': FPS
    }

    def __init__(self):
        self.current_epoch = 0
        self.viewer = None
        self.viewport_width = None
        self.viewport_height = None
        self.gravity = None
        self.partslist = {}
        self.jointslist = []
        self.statistics = False
        self.statisticsRecorder = None
        self.total_reward = 0
        self.current_epoch = 0
        self.env_name = 'cartpoleBarbell-v0'
        self.world = BarbellWorld(gravity=self.gravity)

        self.action_space = spaces.Discrete(2)
        high = np.array([
            self.viewport_width,
            np.finfo(np.float32).max,
            40 + 5,
            np.finfo(np.float32).max])

        low = np.array([
            0,
            np.finfo(np.float32).max,
            -40 - 5,
            np.finfo(np.float32).max])

        self.observation_space = spaces.Box(low, high, dtype=np.float32)

    def get_object(self, object_name):
        return self.world.objects[object_name]

    def get_joint(self, object_a, object_b):
        return self.world.joints["%s_%s" % object_a, object_b]

    def set_definition_file(self, filename):
        parse_file(filename, self)

    def reset(self):
        self.current_epoch += 1
        self.current_step = 0
        self.total_reward = 0
        for body in self.world.objects:
            self.world.DestroyBody(self.world.objects[body])
        self.world = BarbellWorld(gravity=self.gravity)

        self.world.create_objects(self.partslist)
        self.world.create_joints(self.jointslist)
        # self.world.apply_force('local', 'pole', (random.choice((1, 1)) * random.choice((1, 2, 3, 4)), 0))

    def observation(self):
        pass
        # obs = [
        #     self.get_object('cart').position[0] * self.ppm,
        #     self.get_object('cart').linearVelocity[0],
        #     self.get_object('pole').angle * RAD_TO_DEG,
        #     self.get_object('poletop').linearVelocity[0]
        # ]
        # return obs

    def done(self):
        pass
        # angle = abs(self.get_object('pole').angle)
        # if angle * RAD_TO_DEG >= 40 or self.current_step == 300:
        #     return True
        # else:
        #     return False

    def step(self, action):
        # if action == 0:
        #     self.world.apply_force('local', 'cart', (-3, 0))
        # elif action == 1:
        #     self.world.apply_force('local', 'cart', (3, 0))
        #
        observation = self.observation()
        done = self.done()
        #
        # if done:
        #     reward = 0
        # else:
        #     reward = 1
        reward = 0
        self.total_reward += reward
        self.current_step += 1
        self.world.Step(1.0 / FPS, 6 * 30, 2 * 30)
        if done and self.statistics:
            if self.statisticsRecorder is None:
                self.statisticsRecorder = BarbellStatistics(self.env_name)
            self.statisticsRecorder.save(self.current_epoch, self.total_reward)
        return np.array(observation), reward, done

    def render(self, mode='human', close=False):
        if self.viewer is None:
            self.viewer = BarbellViewer(self.viewport_width, self.viewport_height)
        self.viewer.draw_objects(self.world.objects)
        return self.viewer.render(return_rgb_array=(mode == 'rgb_array'))
