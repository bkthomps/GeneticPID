from multiprocessing import Process, Pipe
from random import random
import matplotlib.pyplot as plot
from control import TransferFunction, feedback, step_response, series, step_info

default_generations = 150
default_population = 50
default_crossover = 0.6
default_mutation = 0.25

F = TransferFunction(1, [1, 6, 11, 6, 0])
T = []
count = 0
while count < 100:
    T.append(count)
    count += 0.01


def compute_ise(Kp, Ti, Td):
    g = Kp * TransferFunction([Ti * Td, Ti, 1], [Ti, 0])
    sys = feedback(series(g, F), 1)
    sys_info = step_info(sys)
    _, y = step_response(sys, T)
    ise = sum((y - 1) ** 2)
    t_r = sys_info['RiseTime']
    t_s = sys_info['SettlingTime']
    m_p = sys_info['Overshoot']
    return ise, t_r, t_s, m_p


def genetic_algorithm(pipe, generation_count, population_size, crossover_prob, mutate_prob):
    parents = [[8.0, 4.0, 0.5], [12.0, 6.0, 1.5]]
    best_factor, best_tr, best_ts, best_mp = 0.0, 0.0, 0.0, 0.0
    best_factor_list = []
    i = 0
    while i < generation_count:
        children = []
        j = 0
        while j < population_size / 2 - 1:
            child_1 = parents[0].copy()
            child_2 = parents[1].copy()
            crossover(crossover_prob, child_1, child_2)
            mutate(mutate_prob, child_1)
            mutate(mutate_prob, child_2)
            children.append(child_1)
            children.append(child_2)
            j += 1
        parents.clear()
        factor_total = 0.0
        factor_list = []
        for child in children:
            try:
                ise, t_r, t_s, m_p = compute_ise(child[0], child[1], child[2])
                factor = 1 / ise
            except IndexError:
                factor, t_r, t_s, m_p = 0.0, 0.0, 0.0, 0.0
            factor_list.append(factor)
            factor_total += factor
            if factor > best_factor:
                best_factor = factor
                best_tr = t_r
                best_ts = t_s
                best_mp = m_p
        k = 0
        while len(parents) < 2:
            if factor_list[k] > random() * factor_total:
                parents.append(children[k])
            k = (k + 1) % len(children)
        best_factor_list.append(best_factor)
        i += 1
    pipe.send(best_factor_list)
    pipe.close()
    print("For gen={}, pop={}, cross={}, mut={} -> factor={}, t_r={}, t_s={}, m_p={}"
          .format(generation_count, population_size, crossover_prob, mutate_prob,
                  best_factor, best_tr, best_ts, best_mp))


def crossover(probability, child_1, child_2):
    coin_toss = 0.5
    if random() < probability:
        if random() < coin_toss:
            child_1[0], child_2[0] = child_2[0], child_1[0]
        if random() < coin_toss:
            child_1[1], child_2[1] = child_2[1], child_1[1]
        if random() < coin_toss:
            child_1[2], child_2[2] = child_2[2], child_1[2]


def mutate(probability, child):
    if random() < probability:
        child[0] = round(random() * (18.00 - 2.01) + 2.01, 2)
    if random() < probability:
        child[1] = round(random() * (9.42 - 1.06) + 1.06, 2)
    if random() < probability:
        child[2] = round(random() * (2.37 - 0.27) + 0.27, 2)


def graph(name, values):
    proc, parent, legend = [], [], []
    for v in values:
        p, c = Pipe()
        parent.append(p)
        switch = {
            "main": (c, default_generations, default_population, default_crossover, default_mutation),
            "generation": (c, v, default_population, default_crossover, default_mutation),
            "population": (c, default_generations, v, default_crossover, default_mutation),
            "crossover": (c, default_generations, default_population, v, default_mutation),
            "mutation": (c, default_generations, default_population, default_crossover, v)
        }
        proc.append(Process(target=genetic_algorithm, args=switch.get(name)))
        legend.append("{} = {}".format(name, v))
    for p in proc:
        p.start()
    for p in proc:
        p.join()
    for p in parent:
        plot.plot(p.recv())
    plot.legend(legend, loc='lower right')
    plot.ylabel("Fitness")
    plot.xlabel("Generation")
    plot.savefig("{}.png".format(name), bbox_inches='tight')


if __name__ == '__main__':
    graph("main", [None])
    graph("generation", [10, 25, 50, 100, 150])
    graph("population", [10, 20, 30, 40, 50])
    graph("crossover", [0.2, 0.4, 0.6, 0.8])
    graph("mutation", [0.1, 0.25, 0.4, 0.65, 0.9])
