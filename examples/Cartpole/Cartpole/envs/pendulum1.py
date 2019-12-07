import random

import gym
from barbell_environment import BarbellWorld, BarbellViewer
from barbell_utils import parse_file, get_color

DEG_TO_RAD = 0.0174533
RAD_TO_DEG = 57.2958
FPS = 50  # desired FPS rate


class Pendulum1(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': FPS
    }

    def __init__(self):
        self.scroll = 0.0
        self.current_epoch = 0
        self.viewer = None
        self.viewport_width = None
        self.viewport_height = None
        self.gravity = None
        self.drawlist = {}
        self.partslist = {}
        self.jointslist = []
        self.world = BarbellWorld(gravity=self.gravity)

    def get_object(self, object_name):
        return self.world.objects[object_name]

    def get_joint(self, object_a, object_b):
        return self.world.joints["%s_%s" % object_a, object_b]

    def set_definition_file(self, filename):
        parse_file(filename, self)

    def reset(self):
        self.current_epoch = 0
        for body in self.drawlist:
            self.world.DestroyBody(self.drawlist[body])
        self.world = BarbellWorld(gravity=self.gravity)

        self.world.create_objects(self.partslist)
        self.world.create_joints(self.jointslist)

    def observation(self):
        obs = [
            self.get_object('cart').position[0] * self.ppm,
            self.get_object('cart').linearVelocity[0],
            self.get_object('pole').angle * RAD_TO_DEG,
            self.get_object('poletop').linearVelocity[0]
        ]
        return obs

    def done(self):
        angle = abs(self.get_object('pole').angle)
        if angle * RAD_TO_DEG >= 40 or self.current_epoch == 200:
            return True
        else:
            return False

    def step(self, action):
        self.world.Step(1.0 / FPS, 6 * 30, 2 * 30)

        self.world.apply_force('local', 'pole', (random.choice((-1, 1)), 0))

        observation = self.observation()
        done = self.done()

        if done:
            reward = 0
        else:
            reward = 1
        self.current_epoch += 1
        return observation, reward, done

    def render(self, mode='human', close=False):
        if self.viewer is None:
            self.viewer = BarbellViewer(self.viewport_width, self.viewport_height)

        self.viewer.draw_objects(self.world.objects)
        return self.viewer.render(return_rgb_array=(mode == 'rgb_array'))
