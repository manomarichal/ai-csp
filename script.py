import os
import numpy
import matplotlib.pyplot as plt
index = 0
count = 1000
output_file = open("/home/mano/PycharmProjects/csp/results.txt", "w")

commands = ["python3 solver.py queens --n 10",
            "python3 solver.py queens --method fc --n 30",
            "python3 solver.py queens --method ac3 --n 30",
            "python3 solver.py queens --method ac3 --n 50",
            ]

#run commands and save # of calls
values = []
total = 0
for i in range(0, count, 1):
    os.system(commands[index])
    input_file = open("/home/mano/PycharmProjects/csp/results_temp.txt", "r")
    value = int(input_file.read())
    values.append(value)
    total += value

output_file.write("=========")
output_file.write("\ncommand: " + commands[index])
output_file.write("\ncount: " + str(count))
output_file.write("\n=========")
output_file.write("\naverage: " + str(numpy.average(values)))
output_file.write("\nstandard deviation: " + str(numpy.std(values)))
output_file.write("\n=========")
output_file.close()

help_set = sorted(list(set(values)))
counts = []
for val in help_set:
    counts.append(values.count(val))

y_pos = numpy.arange(len(help_set))

plt.bar(y_pos, counts, align='center',color='r', alpha=0.5)
plt.xticks(y_pos, help_set, rotation=90, horizontalalignment='center')

plt.gca().margins(x=0)
plt.gcf().canvas.draw()
tl = plt.gca().get_xticklabels()
maxsize = max([t.get_window_extent().width for t in tl])
m = 0.2 # inch margin
s = maxsize/plt.gcf().dpi*len(help_set)+2*m
margin = m/plt.gcf().get_size_inches()[0]

plt.gcf().subplots_adjust(left=margin, right=1.-margin)
plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

plt.ylabel('')
plt.title('Amount of calls')
plt.show()