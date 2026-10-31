import math
import numpy as np
import pyglet as py
import random as rdm


window = py.window.Window(1280, 720)
batch = py.graphics.Batch()


class BlackHole:
    def __init__(self):
        self.mass = 250
        self.radius = 70
        self.gravityRadius = 1000
        self.outsideHole = py.shapes.Circle(window.width / 2, window.height / 2, self.radius, color=(255, 127, 0), batch=batch)

        self.glow_layers = []
        for i in range(1, 6):  # 5 glow rings
            glow = py.shapes.Circle(
                window.width / 2,
                window.height / 2,
                self.radius * (0.7 + i * 0.5),  # each ring bigger
                color=(255, 150, 50),
                batch=batch
            )
            glow.opacity = int(80 / i)  # out er rings more transparent
            self.glow_layers.append(glow)

        self.insideHole = py.shapes.Circle(window.width / 2, window.height / 2, self.radius-1, color=(20, 20, 20), batch=batch)


    def rotate(self, dt):
        self.outsideHole.rotation -= 0.5 * dt
        self.insideHole.rotation += 0.5 * dt

    def attract(self, particle, dt):
        meteor = particle
        dist = np.array([meteor.pos[0] - window.width / 2, meteor.pos[1] - window.height / 2]) # vector from meteor to blackhole center

        distance = np.linalg.norm(dist)

        if distance + meteor.radius > self.gravityRadius:
            return np.array([0, 0], dtype=float)  # No force if outside gravity radius
        
        if distance - meteor.radius < self.insideHole.radius:
            particle.life = 60
            return np.array([0, 0], dtype=float)  # returns zero force
        
        G = 1500000

        new_vector = -G * self.mass * dist / (distance**3) # (-G) so that it pulls towards

        return new_vector   # returns the new force vector




class Roids:
    def __init__(self):
        # Tools
        self.radius = rdm.uniform(7, 25)
        self.mass = rdm.uniform(80, 200)
        self.speed = rdm.uniform(70, 150)
        self.life = 0
        self.lifetime = 60

        # Spawning point
        side = rdm.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = rdm.uniform(0, window.width)
            self.y = window.height + 90
            angle = rdm.uniform(7*math.pi/6, 11*math.pi/6)
        elif side == 'bottom':
            self.x = rdm.uniform(0, window.width)
            self.y = -90
            angle = rdm.uniform(math.pi / 6, (5 * math.pi) / 6)
        elif side == 'left':
            self.x = -90
            self.y = rdm.uniform(0, window.height)
            angle = rdm.uniform(-math.pi/3, math.pi/3)
        else:  # right
            self.x = window.width + 90
            self.y = rdm.uniform(0, window.height)
            angle = rdm.uniform(2*math.pi/3, 4*math.pi/3)

        self.colorOptions = rdm.choice([(42, 42, 42), (110, 110, 110), (90, 62, 43), (168, 168, 168), (130, 145, 160)])
        
        # Asteroids buildup
        self.pos = np.array([self.x, self.y], dtype=float)
        self.meteor = py.shapes.Circle(self.pos[0], self.pos[1], self.radius, color=self.colorOptions, batch=batch)
        self.rx = np.cos(angle) * self.speed # velocity in x direction
        self.ry = np.sin(angle) * self.speed # velocity in y direction
        self.velocity = np.array([self.rx, self.ry], dtype=float)

    def update(self, dt):
        ax, ay = blackhole.attract(self, dt)

        # acceleration = force / mass: Newtons second law
        self.rx += (ax / self.mass) * dt
        self.ry += (ay / self.mass) * dt

        # move the meteor physically by updating its position based on velocity
        self.x += self.rx * dt
        self.y += self.ry * dt

        # update the position vector 
        self.pos = np.array([self.x, self.y])

        # update meteor position visually
        self.meteor.x = self.x
        self.meteor.y = self.y

        # update the velocity vector
        self.velocity = np.array([self.rx, self.ry], dtype=float)

        self.life += dt

    def is_alive(self, dt):
        return self.life < self.lifetime
    
class Debris:
    def __init__(self, normal, position, colorOpt):
        self.x, self.y = position
        self.radius = rdm.uniform(0.5, 2.0)
        self.speed = rdm.randint(50, 100) # give extra speed
        self.mass = rdm.uniform(4, 12)
        self.life = 0.0
        self.lifetime = rdm.randint (5, 7)

        rand = np.random.normal(size=2) # Gives an array of 2 random floats
        rand /= np.linalg.norm(rand)    # normalize the array

        self.velocity = (rand + normal) * self.speed
        self.pos = np.array([self.x, self.y], dtype=float)

        self.debris = py.shapes.Circle(self.x, self.y, self.radius, color=colorOpt, batch=batch)

    
    def update(self, dt):
        ax, ay = blackhole.attract(self, dt)
        self.life += dt

        # acceleration = force / mass
        self.velocity[0] += (ax / self.mass) * dt
        self.velocity[1] += (ay / self.mass) * dt

        # update position
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        # update vector
        self.pos = np.array([self.x, self.y])

        # update visual
        self.debris.x = self.pos[0]
        self.debris.y = self.pos[1]


    def is_alive(self):
        return self.life < self.lifetime


debrises = []
blackhole = BlackHole()
meteors = []

def updateDebris(dt):
    for d in debrises:
        d.update(dt)

        debrises[:] = [d for d in debrises if d.is_alive()]

def spawnMeteor(dt):
    count = rdm.randint(1, 3)
    for _ in range(count):
        m = Roids() 

        # Check against all existing meteors
        safe = True
        for other in meteors:
            dist = np.linalg.norm(m.pos - other.pos)
            if dist < m.radius + other.radius + 10:
                safe = False
                break # to stop the for loop

        if safe:
            meteors.append(m)
            break
        else: 
            m.meteor.delete()
    
def updateMeteor(dt):
    for meteor in meteors:
        meteor.update(dt)

    meteors[:] = [m for m in meteors if m.is_alive(dt)]

def clearMeteors():
    for meteor in meteors:
        meteor.meteor.delete()
    meteors.clear()
    for debris in debrises:
        debris.debris.delete()
    debrises.clear()

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
                overlap = min_distance - distance
                m1.pos -= normal * (overlap * 0.5)
                m2.pos += normal * (overlap * 0.5)

                # update meteor position
                m1.meteor.x = m1.pos[0]
                m1.meteor.y = m1.pos[1]
                m2.meteor.x = m2.pos[0]
                m2.meteor.y = m2.pos[1]


                e = 0.8 # elasticity

                # Reduced Mass
                mass1 = m1.mass
                mass2 = m2.mass
                reducedM = (mass1 * mass2) / (mass1 + mass2)


                # Assigning the velocity of the two meteors to the vector between them
                v1 = np.dot(m1.velocity, normal)
                v2 = np.dot(m2.velocity, normal)
                v_rel = v1 - v2

                # if the meteors are moving away from each other skip the collision
                # should fix meteors sticking to eachother.
                if v_rel >= 0:
                    continue


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
                m1.rx, m1.ry = m1.velocity
                m2.rx, m2.ry = m2.velocity


                collisionPoint = (m1.pos + m2.pos) / 2
                for _ in range(rdm.randint(2, 3)):
                    debrises.append(Debris(normal, collisionPoint, m1.colorOptions))
                    debrises.append(Debris(normal, collisionPoint, m2.colorOptions))


@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == py.window.key.Q:
        clearMeteors()



py.clock.schedule_interval(spawnMeteor, 1)
py.clock.schedule_interval(collision, 1/60)
py.clock.schedule_interval(updateMeteor, 1/60)
py.clock.schedule_interval(updateDebris, 1/60)
py.app.run()
