import random
import numpy as np


class Food:
    def __init__(self, sim):
        xm = round(sim.w / 2) - 1
        ym = round(sim.h / 2) - 1

        self.pos = np.array([random.randint(-xm, xm), random.randint(-ym, ym)], dtype='float64')
        self.grid = [0, 0]
        self.is_eaten = False
        self.is_meat = False
        self.nutrition = sim.food_nutrition
        self.meat_timer = 1000
        self.radius = 4
        self.is_food = True

    def render(self, pen):
        pen.goto(float(self.pos[0]), float(self.pos[1]))
        pen.shape('circle')
        pen.shapesize(0.2, 0.2)
        if not self.is_meat:
            pen.color((0, 255, 0))
        else:
            pen.color((255, 0, 0))
        pen.stamp()

    def update(self):
        if self.is_meat:
            self.meat_timer -= 1
            if self.meat_timer == 0:
                self.is_meat = False
