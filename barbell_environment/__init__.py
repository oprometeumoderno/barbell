from gym.envs.classic_control.rendering import Viewer, Transform

from Box2D import b2World
from Box2D.b2 import (edgeShape, circleShape, fixtureDef, polygonShape, revoluteJointDef, contactListener)  # NOQA


class BarbellWorld(b2World):

    def __init__(self, gravity=(0, -1), do_sleep=True):
        self.colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        super().__init__(gravity=gravity, doSleep=do_sleep)

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

    def create_circle(self, body_type, initial_position,
                      angle=0, radius=1, density=1, friction=0.25,
                      color1=None, color2=None):
        body = self.create_body(body_type, initial_position, angle)
        body.CreateCircleFixture(radius=radius, density=density, friction=friction)
        self.paint_body(body, color1, color2)
        return body

    def create_box(self, body_type, initial_position,
                   angle=0, box_size=1, density=1, friction=0.25,
                   color1=None, color2=None):
        body = self.create_body(body_type, initial_position, angle)
        body.CreatePolygonFixture(box=box_size, density=density, friction=friction)
        self.paint_body(body, color1, color2)
        return body

    def create_polygon(self, body_type, initial_position, vertices,
                       angle=0, density=1, friction=0.25,
                       color1=None, color2=None):
        body = self.create_body(body_type, initial_position, angle)
        body.createPolygonFixture(vertices=vertices, density=density, friction=friction)
        self.paint_body(body, color1, color2)

    def create_distance_joint(self, body_a, body_b,
                              offset_a=(0, 0), offset_b=(0, 0)):
        self.CreateDistanceJoint(
            bodyA=body_a,
            bodyB=body_b,
            anchorA=body_a.position + offset_a,
            anchorB=body_b.position + offset_b
        )

    def create_revolute_joint(self, body_a, body_b,
                              local_anchor_a=(0, 0), local_anchor_b=(0, 0)):
        self.CreateRevoluteJoint(
            bodyA=body_a,
            bodyB=body_b,
            localAnchorA=local_anchor_a,
            localAnchorB=local_anchor_b
        )

    def create_prismatic_joint(self, body_a, body_b, anchor, axis,
                               lower_translation, upper_translation,
                               max_motor_force=0, enable_motor=False,
                               motor_speed=0, enable_limit=False):
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


class BarbellViewer(Viewer):

    def __init__(self, viewport_width, viewport_height):
        super().__init__(viewport_width, viewport_height)
        self.set_bounds(0, viewport_width, 0, viewport_height)

    def draw_objects(self, drawlist):
        for obj in drawlist:
            for f in drawlist[obj].fixtures:
                trans = f.body.transform
                if type(f.shape) is circleShape:
                    t = Transform(translation=trans * f.shape.pos)
                    self.draw_circle(f.shape.radius, 20, color=drawlist[obj].color1).add_attr(t)
                    self.draw_circle(f.shape.radius, 20, color=drawlist[obj].color2, filled=False, linewidth=2).add_attr(t)
                else:
                    path = [trans * v for v in f.shape.vertices]
                    self.draw_polygon(path, color=drawlist[obj].color1)
                    path.append(path[0])
