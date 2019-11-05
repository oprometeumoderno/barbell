import gym
import random
from barbell_environment import BarbellWorld, BarbellViewer
FPS = 50  # desired FPS rate

VIEWPORT_W = 600
VIEWPORT_H = 400
GRAVITY = (0, -100)

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
        return [
            self.drawlist['cart'].position
        ]

    def done(self):
        angle = abs(self.drawlist['cart'].joints[0].joint.angle)
        angle *= RAD_TO_DEG
        if angle <= 40 or angle >= 320 or self.current_epoch <= 200:
            return False
        else:
            return True

    def step(self, action):
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

        pole = self.world.create_box(
            body_type='dynamic',
            initial_position=(VIEWPORT_W / 2, VIEWPORT_H),
            box_size=(5, 70),
            angle=random.randint(-17, 17) * DEG_TO_RAD,
            color1=(0.5, 0.5, 0.5)
        )
        self.drawlist['pole'] = pole

        cart = self.world.create_box(
            body_type='dynamic',
            initial_position=(VIEWPORT_W / 2, VIEWPORT_H / 2),
            box_size=(60, 20)
        )
        self.drawlist['cart'] = cart

        floor = self.world.create_box(
            body_type='static',
            initial_position=(VIEWPORT_W / 2, 10),
            box_size=(10, 10)
        )

        self.world.create_revolute_joint(cart, pole, local_anchor_b=(0, -70))
        self.world.create_prismatic_joint(floor, cart, anchor=(0, 0),
                                          axis=(1, 0), lower_translation=-3,
                                          upper_translation=3)

    def render(self, mode='human', close=False):
        if self.viewer is None:
                    self.viewer = BarbellViewer(viewport_width=VIEWPORT_W, viewport_height=VIEWPORT_H)

        self.viewer.draw_objects(self.drawlist)
        return self.viewer.render(return_rgb_array=(mode == 'rgb_array'))
