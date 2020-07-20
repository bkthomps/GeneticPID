from random import random
import matplotlib.pyplot as plot
from control import TransferFunction, feedback, step_response, series, step_info

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


def genetic_algorithm(generation_count, population_size, crossover_prob, mutate_prob):
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
        print(i, best_factor)
        best_factor_list.append(best_factor)
        i += 1
    print("Best: t_r = ", best_tr, ", t_s = ", best_ts, ", m_p", best_mp)
    plot.plot(best_factor_list)
    plot.ylabel("Fitness")
    plot.xlabel("Generation")
    plot.show()


def crossover(probability, child_1, child_2):
    cross_one = random() < probability
    cross_two = random() < probability
    if cross_one and cross_two:
        child_1[1], child_2[1] = child_2[1], child_1[1]
    elif cross_one:
        child_1[0], child_2[0] = child_2[0], child_1[0]
    elif cross_two:
        child_1[2], child_2[2] = child_2[2], child_1[2]
        return


def mutate(probability, child):
    if random() < probability:
        child[0] = round(random() * (18.00 - 2.01) + 2.01, 2)
    if random() < probability:
        child[1] = round(random() * (9.42 - 1.06) + 1.06, 2)
    if random() < probability:
        child[2] = round(random() * (2.37 - 0.27) + 0.27, 2)


if __name__ == '__main__':
    generations = 150  # default 150
    population = 50  # default 50
    crossover_probability = 0.6  # default 0.6
    mutation_probability = 0.25  # default 0.25
    genetic_algorithm(generations, population, crossover_probability, mutation_probability)
