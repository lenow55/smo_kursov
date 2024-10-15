import ciw
import math
import multiprocessing
from functools import partial
from custom_arrival_node import CustomArrivalNode


CustomPartialArrivalClass = partial(CustomArrivalNode, node_bypass_index=3)

N = ciw.create_network(
    arrival_distributions=[
        ciw.dists.Normal(mean=10, sd=1),  # Сообщения А -> B
        ciw.dists.Normal(mean=10, sd=1),  # Сообщения B -> A
        None,  # Сообщения на спутниковую линию приходят только при занятости каналов 1, 2
    ],
    service_distributions=[
        ciw.dists.Deterministic(value=10.0),  # Передача сообщения A -> B
        ciw.dists.Deterministic(value=10.0),  # Передача сообщения B -> A
        # Передача по спутниковой линии (полудуплекс - 1 сообщение в каждую сторону)
        ciw.dists.Normal(mean=10, sd=5 / 3),
    ],
    routing=ciw.routing.NetworkRouting(
        # После прохождения каждого из каналов сообщения покидают систему
        routers=[
            ciw.routing.Leave(),
            ciw.routing.Leave(),
            ciw.routing.Leave(),
        ]
    ),
    number_of_servers=[1, 1, 1],
    # У дуплексного канала с двух сторон по два слота для ожидания
    # у спутниковой линии очереди нет
    # При чём буферный регист должен быть занят даже во время
    # передачи сообщения каналом (так работают регистры и об этом в условии написано)
    # по этой причине реальная очередь перед каналами = 1
    queue_capacities=[1, 1, 0],
)

# ciw.seed(1)

# Q = ciw.Simulation(N, arrival_node_class=CustomPartialArrivalClass)

# Q.simulate_until_max_customers(max_customers=10, progress_bar=True, method="Arrive")
# Q.simulate_until_max_time(max_simulation_time=60000, progress_bar=True)

# recs = Q.get_all_records()
# print(len([r for r in recs if r.record_type == "rejection"]))
# print(len([r for r in recs if r.record_type == "service"]))
# print(len(recs))
#
# blockages = [r.time_blocked for r in recs]
# print(max(blockages))
#
#
# sorted_rec = sorted(recs, key=lambda r: r.id_number)
# sorted_rec1 = filter(lambda r: r.node == 3, sorted_rec)
# print([(r.arrival_date, r.exit_date) for r in sorted_rec1])
# sorted_rec2 = filter(lambda r: r.node == 4, sorted_rec)
# print([(r.arrival_date, r.exit_date) for r in sorted_rec2])
#
# # print(len([r for r in ]))
# indiv = Q.get_all_individuals()
# print(len(indiv))
# print([r.node for r in indiv])
#
# print([r.service_end_date for r in indiv])
#
# print([r.data_records[-1].exit_date for r in Q.nodes[-1].all_individuals])

# print(Q.transitive_nodes[0].server_utilisation)
# print(Q.transitive_nodes[0].id_number)
# print(Q.transitive_nodes[1].server_utilisation)
# print(Q.transitive_nodes[1].id_number)
# print(Q.transitive_nodes[2].server_utilisation)
# print(Q.transitive_nodes[2].id_number)
#
# recs = Q.get_all_records(only=["rejection"])
# print(len(recs))

max_time = 60000
repetitions = 100


def get_mean_wait(network, seed: int = 0, max_time: int = 10000) -> float:
    """Return the mean waiting time for a given network"""
    ciw.seed(seed)
    CustomPartialArrivalClass = partial(CustomArrivalNode, node_bypass_index=3)
    Q = ciw.Simulation(network, arrival_node_class=CustomPartialArrivalClass)
    Q.simulate_until_max_time(max_simulation_time=max_time)
    recs = Q.get_all_records()
    waits = [float(r.waiting_time) for r in recs if not math.isnan(r.waiting_time)]
    mean_wait = sum(waits) / len(waits)
    return mean_wait


if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=4)
    args = [(N, seed, max_time) for seed in range(repetitions)]
    waits = pool.starmap(get_mean_wait, args)
    print(sum(waits) / repetitions)
