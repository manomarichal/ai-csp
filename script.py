import os
import numpy
index = 3
count = 10
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
output_file.write("\nresults:")
help_set = set(values)
for val in help_set:
    output_file.write('\n{0}  {1}'.format(val, values.count(val)))
output_file.write("\n=========")
output_file.write("\naverage: " + str(numpy.average(values)))
output_file.write("\nstandard deviation: " + str(numpy.std(values)))
output_file.write("\n=========")
output_file.close()

