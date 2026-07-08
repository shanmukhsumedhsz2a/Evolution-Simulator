import random
import operator
import math


def hashfunc(to, fro):
    return to * 100000 + fro


class NodeGene:
    def __init__(self, i):
        self.i = i
        self.x = 0
        self.y = 0

    def copy(self):
        n = NodeGene(self.i)
        n.x = self.x
        n.y = self.y

        return n


class ConnectionGene:
    def __init__(self, to, fro):
        self.to = to
        self.fro = fro
        self.weight = random.random() * random.choice([-1, 1])
        self.hash = hashfunc(to, fro)
        self.enabled = True

    def copy(self):
        c = ConnectionGene(self.to, self.fro)
        c.weight = self.weight
        c.enabled = self.enabled
        c.broken = self.broken
        c.broken_id = 0
        c.id = self.id
        return c


class Genome:
    def __init__(self, sim):
        self.node_g = {}
        self.conn_g = {}
        self.sim = sim

        self.initialize()

    def initialize(self):
        for i in range(self.sim.num_inputs):
            n = NodeGene(i+1)
            n.x = 0.1
            n.y = ((i + 1) / self.sim.num_inputs) + (random.random() * 2 - 1)/10
            self.add_node(n)

        for i in range(self.sim.num_outputs):
            n = NodeGene(len(self.node_g)+i + 1)
            n.x = 0.9
            n.y = ((i + 1) / self.sim.num_outputs) + (random.random() * 2 - 1)/10
            self.add_node(n)

        for _ in range(self.sim.initial_connection):
            self.add_con_mutation()

    def add_node(self, node):
        if node.i not in self.node_g:
            self.node_g.update({node.i: node})

    def add_con_gene(self, con):
        if con.hash not in self.conn_g:
            self.conn_g.update({con.hash: con})

    def get_con_genes(self):
        g = []
        for i in self.conn_g:
            g.append(self.conn_g[i])
        return g

    def get_node_genes(self):
        n = []
        for i in self.node_g:
            n.append(self.node_g[i])

        return n

    def add_node_mutation(self):
        if len(self.get_con_genes()) == 0:
            return

        c = random.choice(self.get_con_genes())
        i = 0
        while not c.enabled and i<10:
            i += 1
            c = random.choice(self.get_con_genes())

        a = c.to
        b = c.fro
        i = len(self.node_g) + 1
        n = NodeGene(i)
        n.x = (self.node_g[a].x + self.node_g[b].x) / 2
        n.y = (self.node_g[a].y + self.node_g[b].y) / 2 + (random.random() * 0.1 - 0.05)
        c.enabled = False
        self.add_node(n)
        c1 = ConnectionGene(i,b)
        c1.weight = 1
        c2 = ConnectionGene(a, i)
        c2.weight = c.weight

        self.add_con_gene(c1)
        self.add_con_gene(c2)

    def add_con_mutation(self):
        for _ in range(1000):
            [a, b] = random.choices(self.get_node_genes(), k=2)
            if a.x > b.x:
                c = ConnectionGene(a.i, b.i)
                self.add_con_gene(c)
                return
            elif b.x > a.x:
                c = ConnectionGene(b.i, a.i)
                self.add_con_gene(c)
                return

    def shift_wt_mutation(self):
        if len(self.get_con_genes()) == 0:
            return
        c = random.choice(self.get_con_genes())
        c.weight += (random.random() * 2 - 1) * self.sim.MUTATION_SHIFT_FACTOR

    def random_wt_mutation(self):
        if len(self.get_con_genes()) == 0:
            return
        c = random.choice(self.get_con_genes())
        c.weight = (random.random() * 2 - 1)

    def toggle_con_mutation(self):
        if len(self.get_con_genes()) == 0:
            return
        c = random.choice(self.get_con_genes())
        c.enabled = not c.enabled

    def mutate(self):
        if self.sim.WT_SHIFT_PROB > random.random():
            self.shift_wt_mutation()
        if self.sim.WT_RANDOM_PROB > random.random():
            self.random_wt_mutation()
        if self.sim.WT_TOGGLE_PROB > random.random():
            self.toggle_con_mutation()
        if self.sim.LINK_ADD_PROB > random.random():
            self.add_con_mutation()
        if self.sim.NODE_ADD_PROB > random.random():
            self.add_node_mutation()


# All Activation Functions
def sigmoid(inp):
    try:
        y = 1 + math.exp(-inp)
        z = 1 / y
        return z
    except:
        return 0


def tanh(inp):
    y = 1 + math.exp(-2 * inp)
    z = 2 / y
    return z - 1


def linear(inp):
    return inp


def relu(inp):
    if inp > 0:
        return inp
    else:
        return 0


def leaky_relu(inp, c=0.1):
    if inp > 0:
        return inp
    else:
        return inp * c


class Node:
    def __init__(self, gene, activation=sigmoid):
        self.outp = 0
        self.con = []
        self.i = gene.i
        self.x = gene.x
        self.activation = activation

    def calculate(self):
        self.outp = 0
        for c in self.con:
            if c.enabled:
                self.outp += c.fro.outp * c.weight

        self.outp = self.activation(self.outp)

    def set_output(self, x):
        self.outp = x


class Connection:
    def __init__(self, gene, to, fro):
        self.to = to
        self.fro = fro
        self.weight = gene.weight
        self.enabled = gene.enabled


class Net:
    def __init__(self, genome):
        self.genome = genome
        self.input_nodes = []
        self.outp_node = []
        self.hidden_nodes = []
        self.node_map = {}
        self.connections = []

        for node_g in self.genome.get_node_genes():
            if node_g.i not in self.node_map:
                n = Node(node_g)
                self.node_map.update({n.i: n})
                if node_g.x == 0.1:
                    self.input_nodes.append(n)
                elif node_g.x == 0.9:
                    self.outp_node.append(n)
                else:
                    self.hidden_nodes.append(n)

        self.hidden_nodes.sort(key=operator.attrgetter('x'))
        self.input_nodes.sort(key=operator.attrgetter('i'))
        self.outp_node.sort(key=operator.attrgetter('i'))

        for c_g in self.genome.get_con_genes():
            to = self.node_map[c_g.to]
            fro = self.node_map[c_g.fro]
            c = Connection(c_g, to, fro)
            to.con.append(c)
            self.connections.append(c)

    def calculate(self, input_array):
        if len(input_array) == len(self.input_nodes):
            for i in range(len(input_array)):
                self.input_nodes[i].set_output(input_array[i])

            for n in self.hidden_nodes:
                n.calculate()

            outp = []
            for o in self.outp_node:
                o.calculate()
                outp.append(o.outp)

            return outp

        else:
            print('ERROR: Input size is wrong')