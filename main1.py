import tkinter as tk
from tkinter import messagebox, scrolledtext
import copy
import random
from collections import deque
import time


# Sudoku Solver Class with Optional Arc Consistency
class Sudoku:
    def __init__(self, apply_ac3=True):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.apply_ac3 = apply_ac3
        self.domains = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
        self.arcs = self.initialize_arcs()

    def find_empty(self):
        """Find the next empty cell (row, col)."""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None

    def generate_random_puzzle(self, num_clues=25):
        """Generate a random Sudoku puzzle with a given number of clues."""
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.generate_solution()
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        removed = 0
        while removed < 81 - num_clues:
            row, col = cells.pop()
            temp = self.board[row][col]
            self.board[row][col] = 0
            board_copy = [row[:] for row in self.board]
            if not self.unique_solution():
                self.board[row][col] = temp
            else:
                removed += 1
        return self.board

    def generate_solution(self):
        """Generate a complete solution for Sudoku using backtracking."""
        empty = self.find_empty()
        if not empty:
            return True
        row, col = empty
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        for num in numbers:
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                if self.generate_solution():
                    return True
                self.board[row][col] = 0
        return False

    def unique_solution(self):
        """Check if the current board has a unique solution."""
        solutions = []

        def find_all_solutions():
            empty = self.find_empty()
            if not empty:
                solutions.append([row[:] for row in self.board])
                return len(solutions) > 1
            row, col = empty
            for num in range(1, 10):
                if self.is_valid(row, col, num):
                    self.board[row][col] = num
                    if find_all_solutions():
                        return True
                    self.board[row][col] = 0
            return False

        board_copy = [row[:] for row in self.board]
        find_all_solutions()
        self.board = board_copy
        return len(solutions) == 1

    def validate_board(self):
        """Check if the current board is valid."""
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    self.board[row][col] = 0
                    if not self.is_valid(row, col, num):
                        self.board[row][col] = num
                        return False
                    self.board[row][col] = num
        return True

    def initialize_arcs(self):
        arcs = []
        for i in range(9):
            for j in range(9):
                for k in range(9):
                    if i != k:
                        arcs.append(((i, j), (k, j)))
                    if j != k:
                        arcs.append(((i, j), (i, k)))
                subgrid_x, subgrid_y = i // 3 * 3, j // 3 * 3
                for dx in range(3):
                    for dy in range(3):
                        ni, nj = subgrid_x + dx, subgrid_y + dy
                        if (i, j) != (ni, nj):
                            arcs.append(((i, j), (ni, nj)))
        return arcs

    def revise(self, xi, xj):
        revised = False
        xi_domain = self.domains[xi[0]][xi[1]]
        xj_domain = self.domains[xj[0]][xj[1]]
        for x in set(xi_domain):
            if not any(x != y for y in xj_domain):
                xi_domain.remove(x)
                revised = True
                print(f"Domain reduced for {xi}: {xi_domain} & Domains reduced for {xj}: {xj_domain}")
        return revised

    def ac3(self):
        queue = deque(self.arcs)
        while queue:
            (xi, xj) = queue.popleft()
            if self.revise(xi, xj):
                if len(self.domains[xi[0]][xi[1]]) == 0:
                    print(f"Domain for {xi} reduced to empty set. Puzzle unsolvable.")
                    return False
                for xk in self.get_neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def backtracking_solver(self):
        empty_cell = self.find_empty_cell()
        if not empty_cell:
            return True
        i, j = empty_cell
        for value in self.domains[i][j]:
            if self.is_valid(i, j, value):
                self.board[i][j] = value
                snapshot = copy.deepcopy(self.domains)
                self.domains[i][j] = {value}
                if not self.apply_ac3 or (self.ac3() and self.backtracking_solver()):
                    return True
                self.board[i][j] = 0
                self.domains = snapshot
        return False

    def get_neighbors(self, cell):
        i, j = cell
        neighbors = set()
        for k in range(9):
            if k != i:
                neighbors.add((k, j))
            if k != j:
                neighbors.add((i, k))
        subgrid_x, subgrid_y = i // 3 * 3, j // 3 * 3
        for dx in range(3):
            for dy in range(3):
                ni, nj = subgrid_x + dx, subgrid_y + dy
                if (ni, nj) != (i, j):
                    neighbors.add((ni, nj))
        return neighbors

    def find_empty_cell(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None

    def is_valid(self, i, j, value):
        for k in range(9):
            if self.board[i][k] == value or self.board[k][j] == value:
                return False
        subgrid_x, subgrid_y = i // 3 * 3, j // 3 * 3
        for dx in range(3):
            for dy in range(3):
                if self.board[subgrid_x + dx][subgrid_y + dy] == value:
                    return False
        return True


class SudokuGUI:
    def __init__(self, root, sudoku):
        self.root = root
        self.sudoku = sudoku
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.create_gui()

    def create_gui(self):
        self.root.title("Sudoku Solver")
        frame = tk.Frame(self.root)
        frame.pack()

        for i in range(9):
            for j in range(9):
                entry = tk.Entry(
                    frame,
                    width=2,
                    font=("Arial", 18),
                    justify="center",
                    bd=1,
                    relief="solid"
                )
                entry.bind("<KeyRelease>", lambda event, r=i, c=j: self.validate_entry(r, c))
                entry.grid(row=i, column=j, pady=(3 if i % 3 == 0 else 1), padx=(3 if j % 3 == 0 else 1))
                self.entries[i][j] = entry

        generate_button = tk.Button(self.root, text="Generate Puzzle", command=self.generate_puzzle)
        generate_button.pack(pady=5)

        validate_button = tk.Button(self.root, text="Validate", command=self.validate_solution)
        validate_button.pack(pady=5)

        solve_button = tk.Button(self.root, text="Solve", command=self.solve)
        solve_button.pack(pady=10)

        clear_button = tk.Button(self.root, text="Clear", command=self.clear_board)
        clear_button.pack(pady=5)

    def validate_entry(self, row, col):
        value = self.entries[row][col].get()
        if value.isdigit() and self.sudoku.validate_input(row, col, int(value)):
            self.entries[row][col].config(fg="black")
        else:
            self.entries[row][col].config(fg="red")

    def get_board_from_entries(self):
        for i in range(9):
            for j in range(9):
                value = self.entries[i][j].get()
                self.sudoku.board[i][j] = int(value) if value.isdigit() else 0
        self.sudoku.domains = [
            [
                {self.sudoku.board[i][j]} if self.sudoku.board[i][j] != 0 else set(range(1, 10))
                for j in range(9)
            ]
            for i in range(9)
        ]

    def display_board(self):
        for i in range(9):
            for j in range(9):
                value = self.sudoku.board[i][j]
                self.entries[i][j].delete(0, tk.END)
                if value != 0:
                    self.entries[i][j].insert(0, str(value))

    def generate_puzzle(self):
        self.sudoku.generate_random_puzzle()
        self.display_board()

    def solve(self):
        self.get_board_from_entries()
        if not self.sudoku.validate_board():
            messagebox.showerror("Error", "Invalid Sudoku board! Please check your input.")
            return
        start_time = time.time()
        if not self.sudoku.backtracking_solver():
            messagebox.showerror("Error", "No solution exists!")
        end_time = time.time()
        print(f"Solving time: {end_time - start_time:.4f} seconds")
        self.display_board()

    def clear_board(self):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                self.sudoku.board[i][j] = 0

    def validate_solution(self):
        self.get_board_from_entries()
        if self.sudoku.validate_board():
            messagebox.showinfo("Validation", "This Sudoku board is valid!")
        else:
            messagebox.showerror("Validation", "This Sudoku board is invalid!")


if __name__ == "__main__":
    root = tk.Tk()
    sudoku = Sudoku(apply_ac3=True)
    gui = SudokuGUI(root, sudoku)
    root.mainloop()
