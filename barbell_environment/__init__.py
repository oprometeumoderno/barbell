import yaml
import os

from gym.envs.classic_control.rendering import Viewer, Transform
from barbell_utils import get_color

from Box2D import b2World, b2Vec2
from Box2D.b2 import (edgeShape, circleShape, fixtureDef, polygonShape, revoluteJointDef, contactListener)  # NOQA


class BarbellWorld(b2World):

    def __init__(self, gravity=None):
        self.colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        self.objects = {}
        self.jointslist = {}
        self.default_values = yaml.load(
            open("%s/default_values.yaml" % os.path.dirname(__file__), 'r')
        )

        if gravity is None:
            self._gravity = self.default_values['DOMAIN']['gravity']
        else:
            self._gravity = gravity
        self.ppm = self.default_values['DOMAIN']['ppm']

        super().__init__(gravity=self._gravity, doSleep=self.default_values['DOMAIN']['do_sleep'])

    def overwrite_default_values(self, section, values_dict):
        for key in self.default_values[section]:
            if key in values_dict:
                self.default_values[key] = values_dict[key]
        self.ppm = self.default_values['DOMAIN']['ppm']

    def fill_with_default_values(self, d):
        for key in self.default_values['PART']:
            if key not in d:
                d[key] = self.default_values['PART'][key]
        return d

    def create_objects(self, objects):
        for obj in objects:
            self.create_object(obj, objects[obj])

    def destroy_object(self, obj):
        self.DestroyBody(self.objects[obj])
        del self.objects[obj]

    def create_joints(self, joints):
        for joint in joints:
            self.create_joint(joint['type'],
                              joint['connects'][0],
                              joint['connects'][1],
                              joint)

    def create_object(self, name, args):
        if type(args) == str:
            obj_dict = yaml.load(args)
        elif type(args) == dict:
            obj_dict = args

        obj_dict = self.fill_with_default_values(obj_dict)
        if obj_dict['body_shape'] == 'box':
            self.objects[name] = self.create_box(obj_dict)
        elif obj_dict['body_shape'] == 'circle':
            self.objects[name] = self.create_circle(obj_dict)
        elif obj_dict['body_shape'] == 'polygon':
            self.objects[name] = self.create_polygon(obj_dict)

    def create_body(self, body_type, initial_position, angle, z_index=0):
        # pygame coordinates to box2d
        initial_position = (initial_position[0] / self.ppm, initial_position[1] / self.ppm)
        if body_type == 'static':
            return self.CreateStaticBody(position=initial_position, angle=angle, userData={'z_index': z_index})
        elif body_type == 'dynamic':
            return self.CreateDynamicBody(position=initial_position, angle=angle, userData={'z_index': z_index})

    def paint_body(self, body, color1, color2):
        if color1 is None:
            body.color1 = self.colors[0]
        elif type(color1) == str:
            body.color1 = get_color(color1)
        else:
            body.color1 = color1

        if color2 is None:
            body.color2 = self.colors[1]
        elif type(color2) == str:
            body.color2 = get_color(color2)
        else:
            body.color2 = color2

    def create_circle(self, args):
        body = self.create_body(args['body_type'], args['initial_position'], args['angle'], args['z_index'])
        body.CreateCircleFixture(radius=args['radius'] / self.ppm, density=args['density'], friction=args['friction'])
        self.paint_body(body, args['color1'], args['color2'])
        return body

    def create_box(self, args):
        body = self.create_body(args['body_type'],
                                args['initial_position'],
                                args['angle'],
                                args['z_index'])
        box_size = (args['box_size'][0] / self.ppm, args['box_size'][1] / self.ppm)
        body.CreatePolygonFixture(box=box_size, density=args['density'], friction=args['friction'])
        self.paint_body(body, args['color1'], args['color2'])
        return body

    def create_polygon(self, args):
        vertices = []
        for v in args['vertices']:
            vertices.append(b2Vec2(v[0], v[1]) / self.ppm)
        body = self.create_body(args['body_type'],
                                args['initial_position'],
                                args['angle'])
        body.CreatePolygonFixture(shape=polygonShape(vertices=vertices),
                                  density=args['density'],
                                  friction=args['friction'])

        self.paint_body(body, args['color1'], args['color2'])
        return body

    def create_joint(self, joint_type, body_a, body_b, kwargs):
        joint_key = "%s_%s" % (body_a, body_b)
        if joint_type == 'distance':
            offset_a = kwargs.get('offset_a') or (0, 0)
            offset_b = kwargs.get('offset_b') or (0, 0)
            if joint_key not in self.jointslist:
                self.jointslist[joint_key] = [self.create_distance_joint(body_a,
                                                                         body_b,
                                                                         offset_a,
                                                                         offset_b)]
            else:
                self.jointslist[joint_key].append(self.create_distance_joint(body_a,
                                                                             body_b,
                                                                             offset_a,
                                                                             offset_b))
        elif joint_type == 'revolute':
            local_anchor_a = kwargs.get('local_anchor_a') or (0, 0)
            local_anchor_b = kwargs.get('local_anchor_b') or (0, 0)
            if joint_key not in self.jointslist:
                self.jointslist[joint_key] = [self.create_revolute_joint(body_a,
                                                                         body_b,
                                                                         local_anchor_a,
                                                                         local_anchor_b)]
            else:
                self.jointslist[joint_key].append(self.create_revolute_joint(body_a,
                                                                             body_b,
                                                                             local_anchor_a,
                                                                             local_anchor_b))
        elif joint_type == 'prismatic':
            anchor = kwargs['anchor']
            axis = kwargs['axis']
            lower_translation = kwargs['lower_translation']
            upper_translation = kwargs['upper_translation']
            max_motor_force = kwargs.get('max_motor_force') or 0
            enable_motor = kwargs.get('enable_motor') or False
            motor_speed = kwargs.get('motor_speed') or 0
            enable_limit = kwargs.get('enable_limit') or False
            if joint_key not in self.jointslist:
                self.jointslist[joint_key] = [self.create_prismatic_joint(body_a, body_b, anchor, axis,
                                                                          lower_translation, upper_translation,
                                                                          max_motor_force, enable_motor,
                                                                          motor_speed, enable_limit)]
            else:
                self.jointslist.append(self.create_prismatic_joint(body_a, body_b, anchor, axis,
                                                                   lower_translation, upper_translation,
                                                                   max_motor_force, enable_motor,
                                                                   motor_speed, enable_limit))

    def create_distance_joint(self, body_a_name, body_b_name,
                              offset_a=(0, 0), offset_b=(0, 0)):
        body_a = self.objects[body_a_name]
        body_b = self.objects[body_b_name]
        return self.CreateDistanceJoint(
            bodyA=body_a,
            bodyB=body_b,
            anchorA=body_a.position + b2Vec2(offset_a) / self.ppm,
            anchorB=body_b.position + b2Vec2(offset_b) / self.ppm
        )

    def create_revolute_joint(self, body_a_name, body_b_name,
                              local_anchor_a=(0, 0), local_anchor_b=(0, 0)):
        body_a = self.objects[body_a_name]
        body_b = self.objects[body_b_name]
        self.CreateRevoluteJoint(
            bodyA=body_a,
            bodyB=body_b,
            localAnchorA=b2Vec2(local_anchor_a) / self.ppm,
            localAnchorB=b2Vec2(local_anchor_b) / self.ppm
        )

    def create_prismatic_joint(self, body_a_name, body_b_name, anchor, axis,
                               lower_translation, upper_translation,
                               max_motor_force=0, enable_motor=False,
                               motor_speed=0, enable_limit=False):
        body_a = self.objects[body_a_name]
        body_b = self.objects[body_b_name]
        self.CreatePrismaticJoint(
            bodyA=body_a,
            bodyB=body_b,
            anchor=anchor,
            axis=axis,
            maxMotorForce=max_motor_force,
            enableMotor=enable_motor,
            motorSpeed=motor_speed,
            lowerTranslation=lower_translation,
            upperTranslation=upper_translation,
            enableLimit=enable_limit
        )

    def apply_force(self, force_type, body, force_vector, anchor=(0.0, 0.0)):
        if force_type == 'rotate':
            self.objects[body].ApplyTorque(force_vector, True)
            return

        if force_type == "local":
            force_vector = self.objects[body].GetWorldVector(localVector=force_vector)
        elif force_type == "global":
            force_vector = b2Vec2(force_vector[0], force_vector[1])

        point = self.objects[body].GetWorldPoint(localPoint=(0.0, 0.0))
        self.objects[body].ApplyForce(force_vector, point, True)


class BarbellViewer(Viewer):

    def __init__(self, viewport_width=None, viewport_height=None):
        self.default_values = yaml.load(
            open("%s/default_values.yaml" % os.path.dirname(__file__), 'r')
        )

        self.ppm = self.default_values['DOMAIN']['ppm']

        if viewport_height is None:
            self._viewport_height = self.default_values['DOMAIN']['viewport_height']
        else:
            self._viewport_height = viewport_height

        if viewport_width is None:
            self._viewport_width = self.default_values['DOMAIN']['viewport_width']
        else:
            self._viewport_width = viewport_width
        super().__init__(self._viewport_width, self._viewport_height)
        self.set_bounds(0, self._viewport_width, 0, self._viewport_height)

    def overwrite_default_values(self, section, values_dict):
        for key in self.default_values[section]:
            if key in values_dict:
                self.default_values[key] = values_dict[key]

    def move_camera(self, objects, offset):
        # return
        for obj in objects:
            objects[obj].position = objects[obj].position + (b2Vec2(offset) / self.ppm)

    def draw_objects(self, objects):
        to_draw = []
        for key in objects:
            to_draw.append((key, objects[key].userData['z_index']))
        to_draw = sorted(to_draw, key=lambda x: x[1])
        for key, index in to_draw:
            for f in objects[key].fixtures:
                if type(f.shape) is circleShape:
                    t = Transform(translation=f.body.position * self.ppm)
                    self.draw_circle(f.shape.radius * self.ppm, 20, color=objects[key].color1).add_attr(t)
                    self.draw_circle(f.shape.radius * self.ppm, 20, color=objects[key].color2, filled=False, linewidth=2).add_attr(t)
                else:
                    trans = f.body.transform
                    path = [(trans * v) * self.ppm for v in f.shape.vertices]
                    path.append(path[0])
                    self.draw_polygon(path, color=objects[key].color1)


class BarbellContact(contactListener):
    def init(self):
        super().__init__(self)


class BarbellStatistics():
    def __init__(self, env_name):
        self.env_name = env_name
        self.filename = './%s.csv' % (self.env_name)

    def save(self, epoch, total_reward):
        with open(self.filename, 'a+') as out:
            out.write("%s\n" % ",".join((str(epoch), str(total_reward))))
