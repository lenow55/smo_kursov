import ciw
from matplotlib import pyplot as plt

norm_distrib = ciw.dists.Normal(mean=10, sd=1)

results = [round(norm_distrib.sample(), 3) for _ in range(100000)]

plt.hist(results, color="blue", edgecolor="black", bins=int(18000 / 5))
plt.show()
