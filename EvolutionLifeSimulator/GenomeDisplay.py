import turtle
from main import EvolutionSim
from Brain import Genome


class GenomeDisplay:
    def __init__(self, sim, genome):
        self.wn = turtle.Screen()
        self.wn_w = 1000
        self.wn_h = 800
        self.w = 900
        self.h = 600
        self.wn.setup(self.wn_w, self.wn_h, 0)
        self.wn.title('Genome Display')
        self.wn.bgcolor('black')
        self.wn.tracer(0)

        self.pen = turtle.Turtle()
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.speed(0)

        self.genome = genome
        self.sim = sim

        turtle.listen()
        turtle.onkey(self.genome.add_con_mutation, 'q')
        turtle.onkey(self.genome.add_node_mutation, 'w')
        turtle.onkey(self.genome.toggle_con_mutation, 'e')
        turtle.onkey(self.genome.shift_wt_mutation, 'r')
        turtle.onkey(self.genome.random_wt_mutation, 't')
        turtle.onkey(self.genome.mutate, 'y')

    def get_coord(self, node):
        x = (node.x - 0.5) * self.w
        y = (node.y - 0.5) * self.h - 50
        return x, y

    def set_genome(self, genome):
        self.genome = genome

    def render(self):
        self.pen.clear()
        for c in self.genome.get_con_genes():
            if c.enabled:
                fro = c.fro
                to = c.to
                if c.weight > 0:
                    self.pen.color('green')
                else:
                    self.pen.color('red')

                n1 = self.genome.node_g[fro]
                n2 = self.genome.node_g[to]
                x1, y1 = self.get_coord(n1)
                x2, y2 = self.get_coord(n2)
                self.pen.goto(x1, y1)
                self.pen.pendown()
                self.pen.width = 10
                self.pen.goto(x2, y2)
                self.pen.penup()
                self.pen.goto((x1 + x2) / 2, (y1 + y2) / 2 - 25)
                self.pen.write(f'{round(c.weight * 100) / 100}', font=("Arial", 10, "normal"))
                self.pen.penup()

        for n in self.genome.get_node_genes():
            self.pen.goto(self.get_coord(n))
            self.pen.shape('circle')
            self.pen.shapesize(0.8, 0.8)
            self.pen.color('Blue')
            self.pen.stamp()

    def run(self):
        while True:
            self.render()
            self.wn.update()


sim = EvolutionSim()
g = Genome(sim)
d = GenomeDisplay(sim,g)
print(len(g.node_g))
d.run()
