import ciw

# Определяем параметры системы
arrival_distributions = [ciw.dists.Exponential(rate=5), ciw.dists.Exponential(rate=7)]

service_distribution = [
    ciw.dists.Exponential(rate=3),
    ciw.dists.Exponential(rate=3),
]  # Один сервис с Exponential распределением (параметр 3)

# Создаем сеть с двумя очередями и одним сервером
network = ciw.create_network(
    arrival_distributions=arrival_distributions,  # Два потока заявок
    service_distributions=service_distribution,
    number_of_servers=[2, 2],  # Один сервер на каждую очередь
)

# Запускаем симуляцию
simulation = ciw.Simulation(network)

# Моделируем на протяжении 1000 временных единиц
simulation.simulate_until_max_time(100)

# Получаем данные о клиентах
records = simulation.get_all_records()

# Выводим информацию о каждом обслуженном клиенте
for record in records:
    print(
        f"Пользователь {record.id_number} из очереди {record.node} прибыл в {record.arrival_time} и был обслужен в {record.exit_time}"
    )
