import ciw
from custom_arrival_node import CustomArrivalNode


CustomPartialArrivalClass = partial(CustomArrivalNode, node_bypass_index=3)

N = ciw.create_network(
    arrival_distributions=[
        ciw.dists.Deterministic(value=4.0),
        ciw.dists.Deterministic(value=4.0),
        None,
        None,
    ],
    service_distributions=[
        ciw.dists.Uniform(lower=3.5, upper=4.5),
        ciw.dists.Uniform(lower=3.5, upper=4.5),
        ciw.dists.Uniform(lower=3.5, upper=4.5),
        ciw.dists.Uniform(lower=3.5, upper=4.5),
    ],
    routing=[
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0],
    ],
    number_of_servers=[1, 1, 1, 1],
    queue_capacities=[3, 3, 3, 3],
)

ciw.seed(1)

# Q = ciw.Simulation(N, arrival_node_class=CustomPartialArrivalClass)
Q = ciw.Simulation(N)

Q.simulate_until_max_customers(max_customers=5, progress_bar=True, method="Arrive")

recs = Q.get_all_records()
print(len([r for r in recs if r.record_type == "rejection"]))
print(len(recs))
print(recs)

blockages = [r.time_blocked for r in recs]
print(max(blockages))
