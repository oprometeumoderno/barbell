import yaml
import os

from gym.envs.classic_control.rendering import Viewer, Transform

from Box2D import b2World, b2Vec2
from Box2D.b2 import (edgeShape, circleShape, fixtureDef, polygonShape, revoluteJointDef, contactListener)  # NOQA


class BarbellWorld(b2World):

    def __init__(self, gravity=(0, -1), do_sleep=True):
        self.colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        self.objects = {}
        self.default_values = yaml.load(
            open("%s/default_values.yaml" % os.path.dirname(__file__), 'r')
        )
        super().__init__(gravity=gravity, doSleep=do_sleep)

    def fill_with_default_values(self, d):
        for key in self.default_values['PART']:
            if key not in d:
                d[key] = self.default_values['PART'][key]
        return d

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

        # print(self.fill_with_default_values(obj_dict))

    def create_body(self, body_type, initial_position, angle):
        if body_type == 'static':
            return self.CreateStaticBody(position=initial_position, angle=angle)
        elif body_type == 'dynamic':
            return self.CreateDynamicBody(position=initial_position, angle=angle)

    def paint_body(self, body, color1, color2):
        if color1 is None:
            body.color1 = self.colors[0]
        else:
            body.color1 = color1

        if color2 is None:
            body.color2 = self.colors[1]
        else:
            body.color2 = color2

    def create_circle(self, args):
        body = self.create_body(args['body_type'], args['initial_position'], args['angle'])
        body.CreateCircleFixture(radius=args['radius'], density=args['density'], friction=args['friction'])
        self.paint_body(body, args['color1'], args['color2'])
        return body

    def create_box(self, args):
        body = self.create_body(args['body_type'],
                                args['initial_position'],
                                args['angle'])
        body.CreatePolygonFixture(box=args['box_size'], density=args['density'], friction=args['friction'])
        self.paint_body(body, args['color1'], args['color2'])
        return body

    def create_polygon(self, args):
        body = self.create_body(args['body_type'],
                                args['initial_position'],
                                args['angle'])
        body.CreatePolygonFixture(shape=polygonShape(vertices=args['vertices']),
                                  density=args['density'],
                                  friction=args['friction'])

        self.paint_body(body, args['color1'], args['color2'])
        return body

    def create_distance_joint(self, body_a_name, body_b_name,
                              offset_a=(0, 0), offset_b=(0, 0)):
        body_a = self.objects[body_a_name]
        body_b = self.objects[body_b_name]
        self.CreateDistanceJoint(
            bodyA=body_a,
            bodyB=body_b,
            anchorA=body_a.position + offset_a,
            anchorB=body_b.position + offset_b
        )

    def create_revolute_joint(self, body_a_name, body_b_name,
                              local_anchor_a=(0, 0), local_anchor_b=(0, 0)):
        body_a = self.objects[body_a_name]
        body_b = self.objects[body_b_name]
        self.CreateRevoluteJoint(
            bodyA=body_a,
            bodyB=body_b,
            localAnchorA=local_anchor_a,
            localAnchorB=local_anchor_b
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

    def __init__(self, viewport_width, viewport_height):
        super().__init__(viewport_width, viewport_height)
        self.set_bounds(0, viewport_width, 0, viewport_height)

    def draw_objects(self, objects):
        for obj in objects:
            for f in objects[obj].fixtures:
                trans = f.body.transform
                if type(f.shape) is circleShape:
                    t = Transform(translation=trans * f.shape.pos)
                    self.draw_circle(f.shape.radius, 20, color=objects[obj].color1).add_attr(t)
                    self.draw_circle(f.shape.radius, 20, color=objects[obj].color2, filled=False, linewidth=2).add_attr(t)
                else:
                    path = [trans * v for v in f.shape.vertices]
                    self.draw_polygon(path, color=objects[obj].color1)
                    path.append(path[0])
