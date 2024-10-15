import ciw
import math
import multiprocessing
from functools import partial
from custom_arrival_node import CustomArrivalNode


CustomPartialArrivalClass = partial(CustomArrivalNode, node_bypass_index=3)

N = ciw.create_network(
    arrival_distributions=[
        # ciw.dists.Normal(mean=10, sd=1),  # Сообщения А -> B
        # ciw.dists.Normal(mean=10, sd=1),  # Сообщения B -> A
        ciw.dists.Uniform(lower=7, upper=13),  # Сообщения А -> B
        ciw.dists.Uniform(lower=7, upper=13),  # Сообщения B -> A
        None,  # Сообщения на спутниковую линию приходят только при занятости каналов 1, 2
    ],
    service_distributions=[
        ciw.dists.Deterministic(value=10.0),  # Передача сообщения A -> B
        ciw.dists.Deterministic(value=10.0),  # Передача сообщения B -> A
        # Передача по спутниковой линии (полудуплекс - 1 сообщение в каждую сторону)
        # ciw.dists.Normal(mean=10, sd=5 / 3),
        ciw.dists.Uniform(lower=5, upper=15),
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

ciw.seed(1)

Q = ciw.Simulation(N, arrival_node_class=CustomPartialArrivalClass)

# Q.simulate_until_max_customers(max_customers=10, progress_bar=True, method="Arrive")
Q.simulate_until_max_time(max_simulation_time=600000, progress_bar=True)

recs = Q.get_all_records()
node1_records = filter(lambda r: r.node == 1 and r.record_type == "service", recs)
node2_records = filter(lambda r: r.node == 2 and r.record_type == "service", recs)
node3_records = filter(lambda r: r.node == 3 and r.record_type == "service", recs)
nodeR1_records = filter(lambda r: r.node == 1 and r.record_type == "rejection", recs)
nodeR2_records = filter(lambda r: r.node == 2 and r.record_type == "rejection", recs)
waits = [float(r.waiting_time + r.service_time) for r in node1_records]
mean_wait = sum(waits) / len(waits)
print(mean_wait)
print(len(waits))
print(len(list(node2_records)))
print(len(list(node3_records)))
list_nodeR1 = list(nodeR1_records)
list_nodeR2 = list(nodeR2_records)
print(len(list_nodeR1))
print(len(list_nodeR2))

print(list_nodeR1[:5])
print(list_nodeR2[:5])
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

print(Q.transitive_nodes[0].server_utilisation)
print(Q.transitive_nodes[0].id_number)
print(Q.transitive_nodes[1].server_utilisation)
print(Q.transitive_nodes[1].id_number)
print(Q.transitive_nodes[2].server_utilisation)
print(Q.transitive_nodes[2].id_number)
#
# recs = Q.get_all_records(only=["rejection"])
# print(len(recs))

# max_time = 60000
# repetitions = 2
#
#
# def get_mean_wait(network, seed: int = 0, max_time: int = 10000) -> float:
#     """Return the mean waiting time for a given network"""
#     ciw.seed(seed)
#     CustomPartialArrivalClass = partial(CustomArrivalNode, node_bypass_index=3)
#     Q = ciw.Simulation(network, arrival_node_class=CustomPartialArrivalClass)
#     Q.simulate_until_max_time(max_simulation_time=max_time)
#     # recs = Q.get_all_records()
#     recs = Q.nodes[1].all_individuals
#     waits = [
#         float(r.data_records[0].waiting_time)
#         for r in recs
#         if not math.isnan(r.data_records[0].waiting_time)
#     ]
#     mean_wait = sum(waits) / len(waits)
#     return mean_wait
#
#
# if __name__ == "__main__":
#     pool = multiprocessing.Pool(processes=1)
#     args = [(N, seed, max_time) for seed in range(repetitions)]
#     waits = pool.starmap(get_mean_wait, args)
#     print(sum(waits) / repetitions)
