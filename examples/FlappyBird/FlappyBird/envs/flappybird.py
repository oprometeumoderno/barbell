import gym
import random
from barbell_environment import BarbellWorld, BarbellViewer, BarbellContact, BarbellStatistics
from barbell_utils import parse_file


# CONSTANTS
FPS = 50  # desired FPS rate


class FlappybirdContactDetector(BarbellContact):
    def __init__(self, env):
        BarbellContact.__init__(self)
        self.env = env

    def BeginContact(self, contact):
        self.env.collided = True

    def EndContact(self, contact):
        self.env.collided = False


class Flappybird(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': FPS
    }

    def __init__(self):
        self.env_name = 'flappybird-v0'
        self.viewer = None
        self.drawlist = {}
        self.viewport_width = None
        self.viewport_height = None
        self.gravity = None
        self.partslist = {}
        self.jointslist = []
        self.world = None
        self.collided = False
        self.current_step = 0
        self.current_epoch = 0
        self.statistics = False
        self.statisticsRecorder = None

        self.initialize_world({})

    def initialize_world(self, objects):
        if self.world is not None:
            for body in self.world.objects:
                self.world.DestroyBody(self.world.objects[body])
        self.world = BarbellWorld(gravity=self.gravity)
        self.world.initialized_contact_detector = FlappybirdContactDetector(self)
        self.world.contactListener = self.world.initialized_contact_detector
        self.world.create_objects(objects)

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
        objects = {}
        objects['bird'] = self.partslist['bird']
        objects['floor'] = self.partslist['floor']
        objects['ceiling'] = self.partslist['ceiling']
        for i in range(4):
            pipe = random.randint(1, 4)
            pipe_top = dict(self.partslist['pipe%d_top' % pipe])
            pipe_bottom = dict(self.partslist['pipe%d_bottom' % pipe])
            pipe_top['initial_position'] = (pipe_top['initial_position'][0] + (i * 250), pipe_top['initial_position'][1])
            pipe_bottom['initial_position'] = (pipe_bottom['initial_position'][0] + (i * 250), pipe_bottom['initial_position'][1])
            objects['pipe_%d_top' % i] = pipe_top
            objects['pipe_%d_bottom' % i] = pipe_bottom
        self.initialize_world(objects)

    def observation(self):
        pass

    def reward(self):
        if self.done():
            return 0
        else:
            return 1

    def done(self):
        if self.collided or self.current_step >= 2000:
            return True
        else:
            return False

    def step(self, action):
        if random.randint(1, 20) == 2:
            self.world.apply_force('local', 'bird', (0, 40))

        to_delete = []
        for key in self.world.objects:
            if key.startswith("pipe"):
                pipe_object = self.get_object(key)
                if pipe_object.position[0] * self.ppm < -30:
                    to_delete.append(key)

        if len(to_delete) > 0:
            self.world.destroy_object(to_delete[0])
            self.world.destroy_object(to_delete[1])
            new_pipe = random.randint(1, 5)
            new_pipe_top = dict(self.partslist['pipe%d_top' % new_pipe])
            new_pipe_bottom = dict(self.partslist['pipe%d_bottom' % new_pipe])
            self.world.create_object(to_delete[0], new_pipe_top)
            self.world.create_object(to_delete[1], new_pipe_bottom)

        reward = self.reward()
        self.total_reward += reward
        observation = self.observation()
        done = self.done()
        self.current_step += 1
        self.world.Step(1.0 / FPS, 6 * 30, 2 * 30)
        if done and self.statistics:
            if self.statisticsRecorder is None:
                self.statisticsRecorder = BarbellStatistics(self.env_name)
            self.statisticsRecorder.save(self.current_epoch, self.total_reward)
        return observation, reward, done

    def render(self, mode='human', close=False):
        if self.viewer is None:
                    self.viewer = BarbellViewer(viewport_width=self.viewport_width, viewport_height=self.viewport_height)
        self.viewer.move_camera(self.world.objects, (-2, 0))
        self.viewer.move_camera({
            'b': self.world.objects['bird'],
            'floor': self.world.objects['floor'],
            'ceiling': self.world.objects['ceiling']}, (2, 0))
        self.viewer.draw_objects(self.world.objects)
        return self.viewer.render(return_rgb_array=(mode == 'rgb_array'))
