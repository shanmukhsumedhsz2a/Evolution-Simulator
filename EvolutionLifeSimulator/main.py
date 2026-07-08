import turtle
import random
import time
import math
import numpy as np
from Food import Food
from Creature import Creature

width = 1400
height = 800
grid_length = 50

turtle.colormode(255)


def hash_assign(x, y, gr1, gr2):
    x += width / 2
    y += height / 2

    coord_1 = math.floor(x / grid_length)
    if coord_1 == gr1:
        coord_1 -= 1

    coord_2 = math.floor(y / grid_length)
    if coord_2 == gr2:
        coord_2 -= 1
    return coord_1, coord_2


class Grid:
    def __init__(self, w, h):
        self.food_grid = []
        self.creature_grid = []
        self.w = w
        self.h = h

    def reset(self):
        self.food_grid = []
        self.creature_grid = []
        for i in range(self.w):
            self.food_grid.append([])
            self.creature_grid.append([])
            for j in range(self.h):
                self.food_grid[i].append([])
                self.creature_grid[i].append([])

    def update(self, food_list, creature_list):
        self.reset()
        for f in food_list:
            x, y = hash_assign(f.pos[0], f.pos[1], self.w, self.h)
            self.food_grid[x][y].append(f)
            f.grid = [x, y]
        for c in creature_list:
            x, y = hash_assign(c.pos[0], c.pos[1], self.w, self.h)
            self.creature_grid[x][y].append(c)
            c.grid = [x, y]

    def get_grid(self, x, y):
        return self.food_grid[x][y], self.creature_grid[x][y]

    def get_lists_for_coord(self, grid):
        x = grid[0]
        y = grid[1]
        xr = [x - 1, x, x + 1]
        yr = [y - 1, y, y + 1]
        if x == self.w - 1:
            xr = [x - 1, x, 0]
        if y == self.h - 1:
            yr = [y - 1, y, 0]

        creatures = []
        food = []

        for x in xr:
            for y in yr:
                f, c = self.get_grid(x, y)
                creatures += c
                food += f

        return food, creatures


class EvolutionSim:
    def __init__(self):
        self.wn = turtle.Screen()
        self.w = width
        self.h = height
        self.wn.setup(self.w + 200, self.h + 200, 0)
        self.wn.title('Evolution Simulator')
        self.wn.bgcolor('black')
        self.wn.tracer(0)
        self.wn.listen()
        self.wn.onkey(self.toggle_display,'q')
        #self.wn.onkey(self.reset_paricles,'w')

        self.pen = turtle.Turtle()
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.speed(0)
        self.display = True

        self.grid = Grid(round(self.w / grid_length), round(self.h / grid_length))

        self.max_food = 1000
        self.food_nutrition = 40
        self.max_creatures = 100
        self.food_list = []

        self.friction = 1
        self.num_inputs = 20
        self.num_outputs = 6
        self.initial_connection = 10
        self.creature_list = [Creature(self) for _ in range(100)]
        self.attack_damage = 10
        self.egg_cost = 80
        self.food_factor = 40
        self.frame_cost = 0.4
        self.meat_per_creature = 2
        self.eggs = []

        # Mutation Parameters
        self.MUTATION_SHIFT_FACTOR = 0.3
        self.WT_SHIFT_PROB = 0.7
        self.WT_RANDOM_PROB = 0.2
        self.WT_TOGGLE_PROB = 0.0
        self.NODE_ADD_PROB = 0.3
        self.LINK_ADD_PROB = 0.3
        self.DIET_fACTOR_MUTATE_PROB = 0.2

        self.frame_rate = 0
        self.frame = 0

        self.initialize_env()

    def initialize_env(self):
        for _ in range(round(self.max_food / 4)):
            self.food_list.append(Food(self))

    def render(self):
        self.pen.clear()
        w = self.w + 10
        h = self.h + 10
        self.pen.goto(w / 2, h / 2)
        self.pen.pendown()
        self.pen.color('white')
        self.pen.goto(-w / 2, h / 2)
        self.pen.goto(-w / 2, -h / 2)
        self.pen.goto(w / 2, -h / 2)
        self.pen.goto(w / 2, h / 2)
        self.pen.penup()

        self.pen.goto(-(w / 2), (h / 2) + 10)
        self.pen.pendown()
        self.pen.write(f'Current FrameRate: {self.frame_rate}', font=("Arial", 14, "normal"))
        self.pen.penup()

        self.pen.goto((w / 2) - 140, (h / 2) + 18)
        self.pen.pendown()
        self.pen.write(f'Frame Number: {self.frame} ', font=("Arial", 14, "normal"))
        self.pen.penup()

        for food in self.food_list:
            food.render(self.pen)
        for creature in self.creature_list:
            creature.render(self.pen)
        for egg in self.eggs:
            egg.render(self.pen)

    def kill_creature(self, creature):
        for _ in range(self.meat_per_creature):
            f = Food(self)
            f.pos = creature.pos
            f.is_meat = True
            self.food_list.append(f)

    def attack(self, c1, c2):
        if c1.attack:
            c2.health -= self.attack_damage

    def add_food(self):
        plant_food = 0
        for f in self.food_list:
            if not f.is_meat:
                plant_food += 1
        self.max_food = self.food_factor * self.max_creatures / (1 + len(self.creature_list))
        print(self.max_food)
        if plant_food < self.max_food:
            if random.random() > 0.8:
                self.food_list.append(Food(self))

    def update(self):
        rem_food = []
        rem_creatures = []
        rem_eggs = []

        self.grid.update(self.food_list, self.creature_list)

        for c in self.creature_list:
            c.update()
            if c.is_dead:
                rem_creatures.append(c)

        for e in self.eggs:
            e.update()
            if e.incubation_frames == 0:
                self.creature_list.append(e.hatch())
                rem_eggs.append(e)

        for f in self.food_list:
            f.update()
            if f.is_eaten:
                rem_food.append(f)

        for f in rem_food:
            self.food_list.remove(f)
        for c in rem_creatures:
            self.creature_list.remove(c)
        for e in rem_eggs:
            self.eggs.remove(e)

        self.add_food()

    def toggle_display(self):
        self.display = not self.display

    def run(self):
        running = True
        while running:
            t1 = time.time()
            self.frame += 1
            self.wn.update()
            self.update()
            if self.display:
                self.render()
            t2 = time.time()
            fr = 1 / (t2 - t1)
            self.frame_rate = round(fr * 10) / 10


if __name__ == '__main__':
    sim = EvolutionSim()
    sim.run()
