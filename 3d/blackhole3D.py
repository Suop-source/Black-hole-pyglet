import math
from pyglet.gl import glEnable, GL_DEPTH_TEST
from lib.transformations import rotate_y, rotate_x, rotate_z
import lib
from pyglet.math import Vec3
import numpy as np
import pyglet as py
import pyglet
import random as rdm
from pyglet.window import key



window = pyglet.window.Window(1280, 720)
batch = py.graphics.Batch()

key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)

glEnable(GL_DEPTH_TEST)  # Enable depth testing for proper occlusion


global_state = lib.GlobalState()
world_grid = lib.WorldGrid(py.graphics.Batch())

camera = lib.Camera(width=window.width, height=window.height,
                    fov=60,
                    near=0.01, far=2000.0)
camera.x = 700
camera.y = 50
camera.z = 0
camera_phi = 0.0
camera.distance = 700

point_light = lib.shapes.Sphere(x=700, y=0, z=0, radius=0.2, color=(255, 0, 0, 255), batch=batch) # A sphere to represent the light source


def updateCamera(dt):
    global camera_phi

    rotation_speed = np.pi/2 * dt  # radians per second

    if key_handler[key.D]:
        camera_phi -= rotation_speed
    if key_handler[key.A]:
        camera_phi += rotation_speed

    r = camera.distance # radius/distance from center
    light_radius = 700

    # Update camera position based on the angle, keeping it at a fixed distance from the origin
    camera.x = r * np.cos(camera_phi)  # R * cos(phi)
    camera.z = r * np.sin(camera_phi)  # R * sin(phi)
    camera.y = 0  # stays at y position

    camera_target = Vec3(0, 0, 0)  # black hole center

    # Update light position
    point_light.x = light_radius * np.cos(camera_phi) # R * cos(phi)
    point_light.z = light_radius * np.sin(camera_phi) # R * sin(phi)
    point_light.y = 1.5  # stays at y position

    #print("phi:", camera_phi) test to see if it rotates


class Sun:
    def __init__(self):
        self.sun = lib.Sphere(x=-3000, y=0, z = 0, radius=400, color=(200, 170, 10), batch=batch)


class BlackHole:
    def __init__(self):
        self.mass = 700
        self.radius = 90
        self.gravityRadius = 1000
        self.hole = lib.Sphere(x=0, y=0, z=0, radius=self.radius, color=(10, 10, 25, 255))
        self.glow = lib.Sphere(x=0, y=0, z=0, radius=self.radius+1.5, color=(255, 127, 0, 15))

    def attract(self, meteor, dt):
        dist = np.array([meteor.pos[0] - self.hole.x, meteor.pos[1] - self.hole.y, meteor.pos[2] - self.hole.z])

        distance = np.linalg.norm(dist) # Normalizing

        if distance - meteor.radius > self.gravityRadius:
            return np.array([0,0,0], dtype=float)
        
        if distance < self.radius:
            meteor.life = 60
            return np.array([0,0,0], dtype=float)
        
        G = 750000

        new_vector = -G * self.mass * dist / (distance**3) # (-G) so that it pulls towards

        return new_vector   # returns the new force vector

class Meteor:
    def __init__(self):
        self.radius = rdm.uniform(3, 20)
        self.mass = rdm.uniform(30, 200)
        self.speed = rdm.uniform(50, 200)
        self.life = 0
        self.lifetime = 60
        color = rdm.choice([(42, 42, 42), (110, 110, 110), (90, 62, 43), (168, 168, 168), (130, 145, 160)])

        spawnArea = rdm.choice(['top', 'bottom', 'left', 'right', 'front', 'back'])
        if spawnArea == 'top':
            self.x = rdm.uniform(-350, 350)
            self.y = 300
            self.z = rdm.uniform(-350, 350)
        elif spawnArea == 'bottom':
            self.x = rdm.uniform(-350, 350)
            self.y = -300
            self.z = rdm.uniform(-350, 350)
        elif spawnArea == 'left': 
            self.x = -300
            self.y = rdm.uniform(-350, 350)
            self.z = rdm.uniform(-350, 350)
        elif spawnArea == 'right':
            self.x = 300
            self.y = rdm.uniform(-350, 350)
            self.z = rdm.uniform(-350, 350)
        elif spawnArea == 'front':
            self.x = rdm.uniform(-350, 350)
            self.y = rdm.uniform(-350, 350)
            self.z = 300
        elif spawnArea == 'back':
            self.x = rdm.uniform(-350, 350)
            self.y = rdm.uniform(-350, 350)
            self.z = -300

        # Velocity vector pointing towards the center (0 - x, 0 - y, 0 - z)
        vx, vy, vz = -self.x, -self.y, -self.z

        # Convert those vectors into angles 
        yaw = math.atan2(vz, vx) # horizontal angle 
        pitch = math.atan2(vy, math.sqrt(vx**2 + vz**2)) # vertical angle 

        # Add randomness to the angles (decimal cause its in radians the angles)
        yaw += rdm.uniform(-0.9, 0.9)
        pitch += rdm.uniform(-0.5, 0.5)

        # Convert back to velocity vector with the speed
        vx = math.cos(pitch) * math.cos(yaw)
        vy = math.sin(pitch)
        vz = math.cos(pitch) * math.sin(yaw)

        # Building the direction vector
        vec = np.array([vx, vy, vz], dtype=float)
        vec /= np.linalg.norm(vec)

        self.velocity = vec * self.speed # Adding the speed to the vector
        self.color = color;
        self.rx, self.ry, self.rz = self.velocity
        self.pos = np.array([self.x, self.y, self.z], dtype=float)
        self.meteor = lib.Sphere(x=self.x, y=self.y, z=self.z, radius=self.radius, color=color, batch=batch)


    def update(self, dt):
        ax, ay, az = blackhole.attract(self, dt)

        self.life += dt

         # acceleration = force / mass: Newtons second law
        self.rx += (ax / self.mass) * dt
        self.ry += (ay / self.mass) * dt
        self.rz += (az / self.mass) * dt

        # move the meteor physically by updating its position based on velocity
        self.x += self.rx * dt
        self.y += self.ry * dt
        self.z += self.rz * dt

        # update the position vector 
        self.pos = np.array([self.x, self.y, self.z])

        # update meteor position visually
        self.meteor.x = self.x
        self.meteor.y = self.y
        self.meteor.z = self.z

        # update the velocity vector
        self.velocity = np.array([self.rx, self.ry, self.rz], dtype=float)

    def is_alive(self, dt):
        return self.life < self.lifetime
    
class Debris:
    def __init__(self, normal, position, color):
        self.x, self.y, self.z = position
        self.radius = rdm.uniform(0.5, 2.0)
        self.speed = rdm.randint(50, 100) # give extra speed
        self.mass = rdm.uniform(1, 10)
        self.life = 0.0
        self.lifetime = rdm.randint (5, 12)

        rand = np.random.normal(size=3) # Gives an array of 3 random floats
        rand /= np.linalg.norm(rand)    # normalize the array

        self.velocity = (rand + normal) * self.speed
        self.pos = np.array([self.x, self.y, self.z], dtype=float)

        self.debris = lib.Sphere(self.pos[0], self.pos[1], self.pos[2], self.radius, color=color, batch=batch)
    
    def update(self, dt):
        ax, ay, az = blackhole.attract(self, dt)
        self.life += dt

        self.velocity[0] += (ax / self.mass) * dt
        self.velocity[1] += (ay / self.mass) * dt
        self.velocity[2] += (az / self.mass) * dt

        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.z += self.velocity[2] * dt

        self.pos = np.array([self.x, self.y, self.z], dtype=float)

        self.debris.x = self.pos[0]
        self.debris.y = self.pos[1]
        self.debris.z = self.pos[2]

    def is_alive(self):
        return self.life < self.lifetime


debrises = []
meteors = []
blackhole = BlackHole()
sun = Sun()


def spawnMeteor(dt):
    count = rdm.randint(1, 3)
    for _ in range(count):
        meteors.append(Meteor())

def updateMeteor(dt):
    for meteor in meteors:
        meteor.update(dt)
        
    meteors[:] = [m for m in meteors if m.is_alive(dt)] # Removes outdated meteors

def updateDebris(dt):
    for d in debrises:
        d.update(dt)

    # remove dead debris
    debrises[:] = [d for d in debrises if d.is_alive()]


def clearMeteors():
    for meteor in meteors:
        meteor.meteor.delete()
    meteors.clear()

def collision(dt):
    for i in range(len(meteors)):
        for j in range(i + 1, len(meteors)):
            m1 = meteors[i]
            m2 = meteors[j]

            # vector between the two meteors
            diff = m1.pos - m2.pos
            distance = np.linalg.norm(diff)

            min_distance = m1.radius + m2.radius

            if distance == 0:
                continue # Skips the whole for loop

            # check for collision
            if distance < min_distance:
                normal = diff / distance # normal
                
                # overlapping
                overlap = min_distance - distance
                m1.pos -= normal * (overlap / 2)
                m2.pos += normal * (overlap / 2)

                e = 0.8 # elasticity

                # Reduced Mass
                mass1 = m1.mass
                mass2 = m2.mass
                reducedM = (mass1 * mass2) / (mass1 + mass2)


                # Assigning the velocity of the two meteors to the vector between them
                v1 = np.dot(m1.velocity, normal)
                v2 = np.dot(m2.velocity, normal)

                # Impulse
                I = reducedM * (1 + e) * (v2 - v1)

                v1_new = v1 + I / mass1
                v2_new = v2 - I / mass2

                # New Normal vectors
                v1_new_nVector = v1_new * normal
                v2_new_nVector = v2_new * normal

                # Tangential velocity remains unchanged
                v1_T = m1.velocity - v1 * normal
                v2_T = m2.velocity - v2 * normal

                # Applying the new velocity vector to the meteors
                m1.velocity = v1_T + v1_new_nVector
                m2.velocity = v2_T + v2_new_nVector

                # Update the rx and ry of the meteors after collision
                m1.rx, m1.ry, m1.rz = m1.velocity
                m2.rx, m2.ry, m2.rz = m2.velocity    

                collisionPoint = (m1.pos + m2.pos) / 2
                for _ in range(rdm.randint(1, 2)):
                    debrises.append(Debris(normal, collisionPoint, m1.color))
                    debrises.append(Debris(normal, collisionPoint, m2.color))


@window.event
def on_draw():
    window.clear()

    light_position = np.array([point_light.x, point_light.y, point_light.z])
    global_state.update(camera.get_position(), light_position)


    # Update the camera matrices
    window.projection = camera.get_projection()
    window.view = camera.get_look_at()

    blackhole.hole.draw() # hole

    blackhole.glow.draw() # blending mix ish

    # Reset to normal blending for meteors
    batch.draw()
    
    world_grid.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == py.window.key.Q:
        clearMeteors()

@window.event
def on_key_press(symbol, modifiers):
    key_handler.on_key_press(symbol, modifiers)
    if symbol == key.Q:
        clearMeteors()

@window.event
def on_key_release(symbol, modifiers):
    key_handler.on_key_release(symbol, modifiers)



py.clock.schedule_interval(spawnMeteor, 1)
py.clock.schedule_interval(collision, 1/60)
py.clock.schedule_interval(updateDebris, 1/60)
py.clock.schedule_interval(updateMeteor, 1/60)
py.clock.schedule_interval(updateCamera, 1/100)
py.app.run()
