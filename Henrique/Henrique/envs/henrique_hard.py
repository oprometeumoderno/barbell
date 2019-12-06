import gym
import random
from barbell_environment import BarbellWorld, BarbellViewer

FPS = 60  # desired FPS rate
VIEWPORT_W = 600  # Viewport Width
VIEWPORT_H = 400  # Viewport Height
GRAVITY = (0, -100)  # Gravity Vector
SCALE = 50  # Scale factor (50px = 1m)

DEG_TO_RAD = 0.0174533
RAD_TO_DEG = 57.2958


class HenriqueHard(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': FPS
    }

    def __init__(self):
        self.scroll = 0.0
        self.current_epoch = 0
        self.viewer = None
        self.drawlist = {}
        self.world = BarbellWorld(gravity=GRAVITY)

    def observation(self):
        return [self.world.objects['pole']]

    def done(self):
        angle = abs(self.world.objects['pole'].joints[0].joint.angle)
        if angle * RAD_TO_DEG >= 40 or self.current_epoch == 200:
            return True
        else:
            return False

    def step(self, action):
        if(random.randint(0, 30) == 4):
            self.world.apply_force('local', 'cart', (90000, 0))

        observation = self.observation()
        done = self.done()

        if done:
            reward = 0
        else:
            reward = 1
        self.world.Step(1.0 / FPS, 6 * 30, 2 * 30)
        self.current_epoch += 1
        return observation, reward, done

    def reset(self):
        for body in self.drawlist:
            self.world.DestroyBody(self.drawlist[body])

        pole_definition = {
            'body_type': 'dynamic',
            'body_shape': 'box',
            'initial_position': (VIEWPORT_W / 2, VIEWPORT_H),
            'box_size': (5, 70),
            'angle': 0,
            'color1': (0.5, 0.5, 0.5)
        }
        self.world.create_object('pole', pole_definition)

        cart_definition = {
            'body_type': 'dynamic',
            'body_shape': 'box',
            'vertices': [(-30, 9), (6, 9), (-30, -9)],
            'initial_position': (VIEWPORT_W / 2, VIEWPORT_H / 2),
            'box_size': (60, 20)
        }
        self.world.create_object('cart', cart_definition)

        floor_definition = {
            'body_shape': 'box',
            'body_type': 'static',
            'initial_position': (VIEWPORT_W / 2, 10),
            'box_size': (10, 10)
        }

        self.world.create_object('floor', floor_definition)

        self.world.create_revolute_joint('cart', 'pole', local_anchor_b=(0, -70))
        self.world.create_prismatic_joint('floor', 'cart', anchor=(0, 0),
                                          axis=(1, 0), lower_translation=-3,
                                          upper_translation=3)

    def render(self, mode='human', close=False):
        if self.viewer is None:
            self.viewer = BarbellViewer(viewport_width=VIEWPORT_W, viewport_height=VIEWPORT_H)

        self.viewer.draw_objects(self.world.objects)
        return self.viewer.render(return_rgb_array=(mode == 'rgb_array'))
