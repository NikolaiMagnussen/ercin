import matplotlib.pyplot as plt
import numpy as np

UIO  = 279253
NTNU = 226961
UIB  = 128493
UIT  = 82298
NMBU = 52400

data = [UIO, NTNU, UIB, UIT, NMBU]
n_groups = 5

fig, ax = plt.subplots()
index = np.arange(n_groups)

ax.set_xlabel('Institutions')
ax.set_ylabel('Publications')
ax.grid(True, axis='y', linestyle="--", alpha=0.3)
rects = ax.bar(index, data, color='b')

ax.set_title('')
ax.set_xticklabels(('', 'UIO', 'NTNU', 'UIB', 'UIT', 'NMBU'))
plt.show()
