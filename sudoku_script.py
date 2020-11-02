import os

index = 3
count = 1
output_file = open("/home/mano/PycharmProjects/csp/results.txt", "w")

commands = ["python3 solver.py sudoku /home/mano/PycharmProjects/csp/puzzles/easy.txt --method fc",
            "python3 solver.py sudoku /home/mano/PycharmProjects/csp/puzzles/medium.txt --method fc",
            "python3 solver.py sudoku /home/mano/PycharmProjects/csp/puzzles/hard.txt --method fc",
            "python3 solver.py sudoku /home/mano/PycharmProjects/csp/puzzles/easy.txt --method ac3",
            "python3 solver.py sudoku /home/mano/PycharmProjects/csp/puzzles/medium.txt --method ac3",
            "python3 solver.py sudoku /home/mano/PycharmProjects/csp/puzzles/hard.txt --method ac3"
            ]

#run commands and save # of calls
total = 0
for i in range(0, count, 1):
    os.system(commands[index])
