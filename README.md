# Evolution-Simulator
A 2D Evolution Simulation with Triangular Boid Creatures using Primitive Sensory Input And Evolving Neural Network Brains

ENVIRONMENT DYNAMICS
Uses the python turtle package for animation of a 2D world where the boid creatures inhabit

Food
green circles are plant food which spawn automatically and also dynamically serving to have a maximum population
red circles are meat which can only be produced via death of a creature

Creatures
The creatures are triangular and may choose the color to exhibit dynamically, they have 2 circle behind them indicating 
1. Health - an RGB color varying from green(full health) to red(zero health)
2. Diet - an RGB color varying from green(pure herbivore) to red(pure carnivore)

Their motion is simulated using numerical timestep integration physics

SENSES
The Creatures percieve through ray casting in +45, +30, 0, -30, -45 and 180 degrees
They only see color and each ray returns 3 values corresponding to the RGB values it sees
Another input corresponds to the number of creatures around it
Another is a constitutive input of 1

BRAIN
The brain is initially a sparsely connected neural network with simple linear connections between the inputs and outputs which may develop more complex structure through generations of mutations

OUTPUTS
the outputs of the brain are mapped to the creatures acceleration and the color of the animal
the last output corresponds to the animal wanting to attack other animals in the vicinity

UPDATE FUNCTION
Creatures initally start with a health of 80 which has a maximum of 200 and decays as 1 for every timestep and increases with food intake
Zero Health leads to death of creature

Herbivorous creatures dont gain any health from consuming meat and vice versa

When health reaches above its maximum, it lays an egg which hatches after an incubation time
creature emerging from the egg has a similar genome to parent with mutations accumulated

Eggs are white circles which hatch after an incubation time

Creatures may choose to attack other creatures which lowers the health of the victim creature

The simulation also uses simple grid bases optimization to lower the number of checks and increase speed

AIMS
We hope to observe the development of complex behavior, such as food seeking, herding, predator prey cycles, primitve communication through color and many more

FUTURE UPDATES
- To improve input features
- To use fully connected neural nets with only evolving weights instead of having changing topologies
- Include better optimization for the simulation

