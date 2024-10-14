from functools import partial
from typing import override
import ciw


class CustomArrivalNode(ciw.ArrivalNode):
    @override
    def __init__(self, simulation, node_bypass_index: int):
        self.node_bypass_index = node_bypass_index
        super().__init__(simulation)

    @override
    def release_individual(self, next_node, next_individual):
        """
        Either rejects the next_individual die to lack of capacity,
        or sends that individual to baulk or not.
        """
        if (next_node.number_of_individuals >= next_node.node_capacity) or (
            self.simulation.number_of_individuals >= self.system_capacity
        ):
            # self.record_rejection(next_node, next_individual)
            # self.simulation.nodes[-1].accept(next_individual, completed=False)
            self.decide_baulk(
                self.simulation.nodes[self.node_bypass_index], next_individual
            )
        else:
            self.decide_baulk(next_node, next_individual)


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
