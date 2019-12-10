import gym
from barbell_environment import BarbellWorld, BarbellViewer, BarbellContact, BarbellStatistics
from barbell_utils import parse_file
from math import sin, cos
import numpy as np

# CONSTANTS
FPS = 50  # desired FPS rate


class BarbellAcrobotContactDetector(BarbellContact):
    def __init__(self, env):
        BarbellContact.__init__(self)
        self.env = env

    def BeginContact(self, contact):
        pass

    def EndContact(self, contact):
        pass


class BarbellAcrobot(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': FPS
    }

    def __init__(self):
        self.viewer = None
        self.viewport_width = None
        self.viewport_height = None
        self.gravity = None
        self.drawlist = {}
        self.partslist = {}
        self.jointslist = []
        self.name = 'barbellAcrobot-v0'
        self.world = None
        self.current_step = 0
        self.current_epoch = 0
        self.statistics = False
        self.statisticsRecorder = None

        high = np.array([1.0, 1.0, 1.0, 1.0, np.inf, np.inf])
        low = -high

        self.observation_space = gym.spaces.Box(low=low, high=high, dtype=np.float32)
        self.action_space = gym.spaces.Discrete(3)

        self.initialize_world()

    def initialize_world(self):
        if self.world is not None:
            for body in self.world.objects:
                self.world.DestroyBody(self.world.objects[body])
        self.world = BarbellWorld(gravity=self.gravity)
        self.world.initialized_contact_detector = BarbellAcrobotContactDetector(self)
        self.world.contactListener = self.world.initialized_contact_detector

    def get_object(self, object_name):
        return self.world.objects[object_name]

    def get_joint(self, object_a, object_b):
        return self.world.joints["%s_%s" % object_a, object_b]

    def set_definition_file(self, filename):
        parse_file(filename, self)

    def reset(self):
        self.current_step = 0
        self.total_reward = 0
        self.current_epoch += 1

        self.initialize_world()
        self.world.create_objects(self.partslist)
        self.world.create_joints(self.jointslist)

    def observation(self):
        angle1 = self.get_object('pole1').angle
        angle2 = self.get_object('pole2').angle - angle1
        lv1 = self.get_object('pole1').angularVelocity
        lv2 = self.get_object('pole2').angularVelocity
        obs = [cos(angle1), sin(angle1), cos(angle2), sin(angle2), lv1, lv2]
        return np.array(obs)

    def reward(self):
        return -1

    def done(self, observation):
        angle1 = self.get_object('pole1').angle
        angle2 = self.get_object('pole2').angle - angle1
        return self.current_step >= 2000 or bool(-cos(angle1) - cos(angle1 + angle2) > 1.)

    def step(self, action):
        self.world.apply_force('rotate', 'pole1', action * 10)

        self.current_step += 1
        reward = self.reward()
        observation = self.observation()
        done = self.done(observation)
        self.world.Step(1.0 / FPS, 6 * 30, 2 * 30)
        if done and self.statistics:
            if self.statisticsRecorder is None:
                self.statisticsRecorder = BarbellStatistics(self.env_name)
            self.statisticsRecorder.save(self.current_epoch, self.total_reward)
        return observation, reward, done

    def render(self, mode='human', close=False):
        if self.viewer is None:
                    self.viewer = BarbellViewer(viewport_width=self.viewport_width, viewport_height=self.viewport_height)

        self.viewer.draw_objects(self.world.objects)
        return self.viewer.render(return_rgb_array=(mode == 'rgb_array'))
