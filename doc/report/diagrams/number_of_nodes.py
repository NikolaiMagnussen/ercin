import matplotlib.pyplot as plt
import numpy as np

UIO  = [91884, 49652, 29108, 20010, 13704]
NTNU = [49652, 77011, 17610, 17287, 8854]
UIB  = [29108, 17610, 41590, 8970, 2736]
UIT  = [20010, 17287, 8970, 22261, 2841]
NMBU = [13704, 8854, 2736, 2841, 17763]
total  = [279253, 226961, 128493, 82298, 52400]
others = []
data = [UIO, NTNU, UIB, UIT, NMBU]

for t, inst in enumerate(data):
    diff = 0
    for i in inst:
        diff += i
    others.append(total[t] - diff)

data.append(others)
data.append(total)

for t in data:
    print(t)

columns = ['UIO', 'NTNU', 'UIB','UIT', 'NMBU']
rows = ['UIO', 'NTNU', 'UIB', 'UIT', 'NMBU', 'others', 'total']

colors = plt.cm.BuPu(np.linspace(0.5, 0, len(rows)))

# Initialize the vertical-offset for the stacked bar chart.
y_offset = np.zeros(len(columns))

for row in range(0, len(data) - 1):
    plt.bar(np.arange(len(columns)), data[row], 0.4, bottom=y_offset, color=colors[row])
    y_offset = y_offset + data[row]
cell_text = []
for row in range(0, len(data)):
    cell_text.append(['%d' % x for x in data[row]])

# Add a table at the bottom of the axes
the_table = plt.table(cellText=cell_text,
                      rowLabels=rows,
                      rowColours=colors,
                      colLabels=columns,
                      loc='bottom')

# Adjust layout to make room for the table:
plt.subplots_adjust(left=0.2, bottom=0.25)

plt.ylabel("Publications")
plt.xticks([])
plt.grid(True, axis='y', linestyle="--", alpha=0.3)
plt.yticks([0, 50000, 100000, 150000, 200000, 250000, 300000])
plt.title("Publications between institutions")

plt.show()
