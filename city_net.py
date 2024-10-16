import ciw
import pandas as pd
import multiprocessing
from functools import partial
from custom_arrival_node import CustomArrivalNode


CustomPartialArrivalClass = partial(CustomArrivalNode, node_bypass_index=3)

N = ciw.create_network(
    arrival_distributions=[
        ciw.dists.Uniform(lower=7, upper=13),  # Сообщения А -> B
        ciw.dists.Uniform(lower=7, upper=13),  # Сообщения B -> A
        None,  # Сообщения на спутниковую линию приходят только при занятости каналов 1, 2
    ],
    service_distributions=[
        ciw.dists.Deterministic(value=10.0),  # Передача сообщения A -> B
        ciw.dists.Deterministic(value=10.0),  # Передача сообщения B -> A
        # Передача по спутниковой линии (полудуплекс - 1 сообщение в каждую сторону)
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

max_time = 60000
repetitions = 5


def get_mean_wait4node(Q: ciw.Simulation, node_id: int):
    recs = Q.get_all_records()
    node_filter = filter(
        lambda r: r.node == node_id and r.record_type == "service", recs
    )
    waits = [float(r.waiting_time + r.service_time) for r in node_filter]
    mean_wait = sum(waits) / len(waits)
    return mean_wait


def get_mean_qs_report(
    network, seed: int = 0, max_time: int = 10000
) -> dict[str, float | int | None]:
    """Return the mean report"""
    ciw.seed(seed)
    CustomPartialArrivalClass = partial(CustomArrivalNode, node_bypass_index=3)
    Q = ciw.Simulation(network, arrival_node_class=CustomPartialArrivalClass)
    Q.simulate_until_max_time(max_simulation_time=max_time, progress_bar=False)

    mean_wait_1 = get_mean_wait4node(Q, 1)
    mean_wait_2 = get_mean_wait4node(Q, 2)
    recs = Q.get_all_records()
    node1_records = [r for r in recs if r.node == 1 and r.record_type == "service"]
    node2_records = [r for r in recs if r.node == 2 and r.record_type == "service"]
    node3_records = [r for r in recs if r.node == 3 and r.record_type == "service"]
    count_entires_node1 = len(node1_records)
    count_entires_node2 = len(node2_records)
    count_entires_node3 = len(node3_records)
    rejected_records = [r for r in recs if r.record_type == "rejection"]
    count_rejected_records = len(rejected_records)
    report_dict = {
        "Ср. ожидание регистры A2B": mean_wait_1,
        "Ср. ожидание регистры B2A": mean_wait_2,
        "Кол-во вызовов канала A2B": count_entires_node1,
        "Кол-во вызовов канала B2A": count_entires_node2,
        "Кол-во вызовов канала StarLink": count_entires_node3,
        "Загрузка канала A2B": Q.transitive_nodes[0].server_utilisation,
        "Загрузка канала B2A": Q.transitive_nodes[1].server_utilisation,
        "Загрузка канала StarLink": Q.transitive_nodes[2].server_utilisation,
        "Кол-во отброшенных сообщений": count_rejected_records,
        "Seed": seed,
    }

    return report_dict


if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=1)
    args = [(N, seed, max_time) for seed in range(1, repetitions + 1)]
    reports_dicts = pool.starmap(get_mean_qs_report, args)
    reports_dicts = sorted(reports_dicts, key=lambda i: i["Seed"])
    report_df = pd.DataFrame(reports_dicts)
    report_df.to_excel("report.xlsx")
