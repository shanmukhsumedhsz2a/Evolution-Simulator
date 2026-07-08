import random
import numpy as np
import math
from Brain import Genome, Net


def magnitude(vec):
    return np.linalg.norm(vec)


def map(x, xmin, xmax, map1, map2):
    span1 = xmax - xmin
    span2 = map2 - map1

    w = (x - xmin) * span2 / span1

    out = map1 + w
    return out


def map_color(x, xmin=0, xmax=1, negative=False):
    if not negative:
        i = round(map(x, xmin, xmax, 0, 255))
        if i < 0:
            i = 0
        if i > 255:
            i = 255
        return i
    else:
        i = round(map(x, xmin, xmax, 255, 0))
        if i < 0:
            i = 0
        if i > 255:
            i = 255
        return i


class Creature:
    def __init__(self, sim, genome=None):
        self.sim = sim
        xm = round(sim.w / 2) - 1
        ym = round(sim.h / 2) - 1

        self.pos = np.array([round(random.randint(-xm, xm)), round(random.randint(-ym, ym))], dtype='float64')
        self.vel = np.array([random.randint(-5, 5), random.randint(-5, 5)], dtype='float64')
        self.acc = np.array(np.array([0, 0], dtype='float64'))
        self.heading = 0
        self.max_speed = 3
        self.radius = 5

        self.grid = [0, 0]

        self.health = 80
        self.max_health = 200
        self.diet_factor = random.randint(7, 10) / 10
        self.attack = 0
        if genome is None:
            self.genome = Genome(sim)
        else:
            self.genome = genome
            self.mutate()

        self.brain = Net(self.genome)
        self.color = (0, 0, 0)
        self.inputs = [0 for _ in range(sim.num_inputs)]
        self.is_dead = False
        self.is_food = False

    def render(self, pen):
        pen.goto(round(self.pos[0]), round(self.pos[1]))
        pen.shape('triangle')

        angle = math.degrees(np.arccos(
            self.vel.dot(np.array([1.0, 0.0])) / (
                    np.linalg.norm(self.vel) * np.linalg.norm(np.array([1.0, 0.0])))))
        if self.vel[1] < 0:
            angle *= -1
        if np.linalg.norm(self.vel) == 0:
            angle = 0

        pen.setheading(angle)

        self.heading = angle

        pen.shapesize(0.2, 0.3)
        pen.color(self.color)
        pen.stamp()
        if self.attack:
            pen.shape('circle')
            pen.shapesize(0.2, 0.2)
            pen.color(255, 0, 0)
            pen.stamp()

        diet_indicator = self.pos - 10 * np.array(
            [math.cos(angle * math.pi / 180), math.sin(angle * math.pi / 180)],
            dtype='float64') - 3 * np.array(
            [math.cos((angle + 90) * math.pi / 180), math.sin((angle + 90) * math.pi / 180)],
            dtype='float64')

        pen.goto(round(diet_indicator[0]), round(diet_indicator[1]))
        pen.shape('square')
        pen.shapesize(0.075, 0.075)
        pen.setheading(angle)
        pen.color((map_color(self.diet_factor, negative=True), map_color(self.diet_factor), 0))
        pen.stamp()

        health_indicator = self.pos - 10 * np.array(
            [math.cos(angle * math.pi / 180), math.sin(angle * math.pi / 180)],
            dtype='float64') + 3 * np.array(
            [math.cos((angle + 90) * math.pi / 180), math.sin((angle + 90) * math.pi / 180)],
            dtype='float64')

        pen.goto(round(health_indicator[0]), round(health_indicator[1]))
        pen.shape('circle')
        pen.shapesize(0.1, 0.1)
        pen.setheading(angle)

        pen.color((map_color(self.health, 0, xmax=self.max_health, negative=True),
                   map_color(self.health, 0, xmax=self.max_health), 0))
        pen.stamp()

    def update_phy(self):
        self.vel += self.acc
        self.pos += self.vel
        self.vel *= self.sim.friction

        if self.pos[0] > self.sim.w / 2:
            newp = np.array([-self.sim.w / 2, self.pos[1]])
            self.pos = newp
        elif self.pos[0] < -self.sim.w / 2:
            newp = np.array([self.sim.w / 2, self.pos[1]])
            self.pos = newp

        if self.pos[1] > self.sim.h / 2:
            newp = np.array([self.pos[0], -self.sim.h / 2])
            self.pos = newp
        elif self.pos[1] < -self.sim.h / 2:
            newp = np.array([self.pos[0], self.sim.h / 2])
            self.pos = newp

        speed = np.linalg.norm(self.vel)
        if speed > self.max_speed:
            self.vel /= speed
            self.vel *= self.max_speed

        self.acc *= 0

    def eat(self, food):
        if not food.is_meat:
            nutrition = food.nutrition * map(self.diet_factor, 0, 1, -0.5, 1.5)
        else:
            nutrition = food.nutrition * map(self.diet_factor, 0, 1, 1.5, -0.5)

        food.is_eaten = True
        self.health += nutrition

    def mutate(self):
        self.genome.mutate()
        if random.random() < self.sim.DIET_fACTOR_MUTATE_PROB:
            self.diet_factor += random.choice([0, 0, 0, -0.1, -0.2, 0.1, 0.2])
            if self.diet_factor < 0:
                self.diet_factor = 0
            if self.diet_factor > 1:
                self.diet_factor = 1

    def die(self):
        self.sim.kill_creature(self)

    def update(self):
        self.update_sim()
        self.update_creature()
        self.update_phy()

    def cast_ray(self, heading, cs, fs, jump=5):
        pos = self.pos.copy()
        dpos = jump * np.array([math.cos(heading * math.pi / 180), math.sin(heading * math.pi / 180)])
        vis = 10
        objects = cs + fs
        for i in range(vis):
            pos += dpos
            for o in objects:
                if magnitude(pos - o.pos) < o.radius:
                    if not o.is_food:
                        return list(o.color)
                    if o.is_food:
                        if o.is_meat:
                            return [255, 0, 0]
                        else:
                            return [0, 255, 0]
        return [0, 0, 0]

    def update_sim(self):
        food, creatures = self.sim.grid.get_lists_for_coord(self.grid)
        creatures.remove(self)

        inp4 = 0

        for f in food:
            if magnitude(f.pos - self.pos) < self.radius:
                self.eat(f)

        for c in creatures:
            inp4 += 0.1
            if magnitude(c.pos - self.pos) < self.radius:
                self.sim.attack(self, c)

        inp1 = self.cast_ray(self.heading - 45, creatures, food)
        inp2 = self.cast_ray(self.heading, creatures, food)
        inp3 = self.cast_ray(self.heading - 30, creatures, food)
        inp5 = self.cast_ray(self.heading + 45, creatures, food)
        inp6 = self.cast_ray(self.heading + 30, creatures, food)
        inp7 = self.cast_ray(self.heading + 180, creatures, food)
        self.inputs = inp1 + inp2 + inp3 + [inp4] + [1] + inp5 + inp6 + inp7

    def update_creature(self):
        if self.health > self.max_health:
            self.health -= self.sim.egg_cost
            self.lay_egg()

        self.health -= self.sim.frame_cost
        if self.health < 0:
            self.health = 0
            self.is_dead = True
            self.die()

        x = self.brain.calculate(self.inputs)

        self.acc = np.array([x[0], x[1]], dtype='float64') * 2 - 1
        self.color = (round(x[2] * 255), round(x[3] * 255), round(x[4] * 255))
        #self.color = (0, 0, round(x[4] * 255))
        if x[5] > 0.8:
            self.attack = True

        else:
            self.attack = False

    def lay_egg(self):
        self.sim.eggs.append(Egg(self.genome, self.sim, self.pos))


class Egg:
    def __init__(self, genome, sim, pos):
        self.incubation_frames = 200
        self.pos = pos.copy()
        self.genome = genome
        self.sim = sim

    def update(self):
        self.incubation_frames -= 1

    def hatch(self):
        c = Creature(self.sim, genome=self.genome)
        c.pos = self.pos
        return c

    def render(self, pen):
        pen.goto(float(self.pos[0]), float(self.pos[1]))
        pen.shape('circle')
        pen.shapesize(0.2, 0.2)
        pen.color(255, 255, 255)
        pen.stamp()
