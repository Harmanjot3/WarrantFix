import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
global  convergence_iteration_vppso, sgo_fitness_curve , vppso_fitness_curve ,n1
canvas = None
fig = None

class Person:
    def __init__(self, fitness, dim, minx, maxx):
        self.position = [0.0 for i in range(dim)]
        for i in range(dim):
            self.position[i] = minx + np.random.rand() * (maxx - minx)
        self.fitness = fitness(self.position)

class Particle1:
    def __init__(self, fitness, dim, minx, maxx):
        self.position = [0.0 for i in range(dim)]
        self.velocity = [0.0 for i in range(dim)]
        self.best_part_pos = [0.0 for i in range(dim)]
        for i in range(dim):
            self.position[i] = ((maxx - minx) * np.random.rand() + minx)
        self.fitness = fitness(self.position)
        self.best_part_pos = np.copy(self.position)
        self.best_part_fitnessVal = self.fitness

class Particle2:
    def __init__(self, fitness, dim):
        self.position = [0.0 for i in range(dim)]
        self.best_part_pos = [0.0 for i in range(dim)]
        self.fitness = fitness(self.position)

def sgo(fitness, max_iter, n, dim, minx, maxx):
    Fitness_Curve = np.zeros(max_iter)
    society = [Person(fitness, dim, minx, maxx) for i in range(n)]
    Xbest = [0.0 for i in range(dim)]
    c = 0.2
    Fbest = sys.float_info.max
    for i in range(n):
        if society[i].fitness < Fbest:
            Fbest = society[i].fitness
            Xbest = np.copy(society[i].position)
    Iter = 0
    while Iter < max_iter:
        for i in range(n):
            Xnew = [0.0 for i in range(dim)]
            for j in range(dim):
                Xnew[j] = c * society[i].position[j] + np.random.rand() * (Xbest[j] - society[i].position[j])
            for j in range(dim):
                Xnew[j] = max(Xnew[j], minx)
                Xnew[j] = min(Xnew[j], maxx)
            fnew = fitness(Xnew)
            if (fnew < society[i].fitness):
                society[i].position = Xnew
                society[i].fitness = fnew
            if (fnew < Fbest):
                Fbest = fnew
                Xbest = Xnew
        Fitness_Curve[Iter] = int(Fbest)
        Iter += 1

    return Xbest, Fitness_Curve

def vppso(fitness, max_iter, n, n1, dim, minx, maxx):
    Fitness_Curve = np.zeros(max_iter)
    c1 = 2
    c2 = 2
    best_fitness = []
    swarm = [Particle1(fitness, dim, minx, maxx) for i in range(n)]
    swarm1 = [Particle2(fitness, dim) for i in range(n1)]
    best_swarm_pos = [0.0 for i in range(dim)]
    best_swarm_fitnessVal = sys.float_info.max
    for i in range(n):
        if swarm[i].fitness < best_swarm_fitnessVal:
            best_swarm_fitnessVal = swarm[i].fitness
            best_swarm_pos = np.copy(swarm[i].position)
    Iter = 0
    alpha = 0.3
    V_max = 0.1 * (maxx - minx)
    V_min = -V_max
    while Iter < max_iter:
        w = np.exp(-((2.5 * Iter / max_iter) ** 2.5))
        for i in range(n):
            if (np.random.rand() < alpha):
                for k in range(dim):
                    exponent = np.random.rand() * w
                    if swarm[i].velocity[k] >= 0:
                        velocity_component = (swarm[i].velocity[k] ** exponent)
                    else:
                        velocity_component = (abs(swarm[i].velocity[k]) ** exponent) * (-1 if exponent % 2 == 0 else 1)
                    swarm[i].velocity[k] = velocity_component + (
                            c1 * np.random.rand() * (swarm[i].best_part_pos[k] - swarm[i].position[k])) + (
                                                   c2 * np.random.rand() * (
                                                           best_swarm_pos[k] - swarm[i].position[k]))
            else:
                swarm[i].velocity[:] = swarm[i].velocity[:]
            for k in range(dim):
                if swarm[i].velocity[k] < V_min:
                    swarm[i].velocity[k] = V_min
                elif swarm[i].velocity[k] > V_max:
                    swarm[i].velocity[k] = V_max
            for k in range(dim):
                swarm[i].position[k] += swarm[i].velocity[k]
                if swarm[i].position[k] < minx:
                    swarm[i].position[k] = minx
                elif swarm[i].position[k] > maxx:
                    swarm[i].position[k] = maxx
            swarm[i].fitness = fitness(swarm[i].position)
            if swarm[i].fitness < swarm[i].best_part_fitnessVal:
                swarm[i].best_part_fitnessVal = swarm[i].fitness
                swarm[i].best_part_pos = np.copy(swarm[i].position)
            if swarm[i].fitness < best_swarm_fitnessVal:
                best_swarm_fitnessVal = swarm[i].fitness
                best_swarm_pos = np.copy(swarm[i].position)
        for i in range(n1):
            for k in range(dim):
                CC = w * np.random.rand() * abs(best_swarm_pos[k]) ** w
                if np.random.rand() < 0.5:
                    swarm1[i].position[k] = best_swarm_pos[k] + CC
                else:
                    swarm1[i].position[k] = best_swarm_pos[k] - CC
            for k in range(dim):
                if swarm1[i].position[k] < minx:
                    swarm1[i].position[k] = minx
                elif swarm1[i].position[k] > maxx:
                    swarm1[i].position[k] = maxx
            swarm1[i].fitness = fitness(swarm1[i].position)
            if swarm1[i].fitness < best_swarm_fitnessVal:
                best_swarm_fitnessVal = swarm1[i].fitness
                best_swarm_pos = np.copy(swarm1[i].position)
        convergence_iteration_vppso = Iter

        Fitness_Curve[Iter] = int(best_swarm_fitnessVal)
        Iter += 1
    return best_swarm_pos, Fitness_Curve

def f1(position):  # rastrigin
    fitness_value = 0.0
    for i in range(len(position)):
        xi = position[i]
        fitness_value += (xi * xi) - (10 * np.cos(2 * np.pi * xi)) + 10
    return fitness_value

def f2(position):  # sphere
    fitness_value = 0.0
    for i in range(len(position)):
        xi = position[i]
        fitness_value += (xi * xi)
    return fitness_value

def f3(position):  # rosenbrock
    fitness_value = 0.0
    for i in range(len(position) - 1):
        xi = position[i]
        xi1 = position[i + 1]
        fitness_value += 100 * (xi1 - xi ** 2) ** 2 + (1 - xi) ** 2
    return fitness_value

def f4(position):  # griewank
    fitness_value = 0.0
    sum_term = 0.0
    prod_term = 1.0
    for i in range(len(position)):
        xi = position[i]
        sum_term += xi ** 2 / 4000
        prod_term *= np.cos(xi / np.sqrt(i + 1))
    fitness_value = 1 + sum_term - prod_term
    return fitness_value

def f5(position):  # ackley
    dim = len(position)
    sum_term = np.sum(np.square(position))
    cos_term = np.sum(np.cos(2 * np.pi * np.array(position)))
    fitness_value = -20 * np.exp(-0.2 * np.sqrt(sum_term / dim)) - np.exp(cos_term / dim) + 20 + np.exp(1)
    return fitness_value


def run_optimization(fitness_function, max_iter, n, n1, dim, minx, maxx):
    best_position, Fitness_Curve = sgo(fitness_function, max_iter, n, dim, minx, maxx)
    fitness_value = fitness_function(best_position)
    convergence_iteration = np.argmax(Fitness_Curve == int(fitness_value))

    # Calculate the SGO fitness curve separately
    sgo_best_position, sgo_fitness_curve = sgo(fitness_function, max_iter, n, dim, minx, maxx)

    # Calculate the VPPSO fitness curve separately
    vppso_best_position, vppso_fitness_curve = vppso(fitness_function, max_iter, n, n1, dim, minx, maxx)

    return best_position, fitness_value, convergence_iteration, Fitness_Curve, sgo_fitness_curve, vppso_best_position, vppso_fitness_curve


def create_gui():
    global convergence_frame
    def reset_values():
        function_var.set(function_options[0])
        max_iter_entry.delete(0, tk.END)
        dim_entry.delete(0, tk.END)
        minx_entry.delete(0, tk.END)
        maxx_entry.delete(0, tk.END)
        vppso_swarm1_entry.delete(0, tk.END)
        vppso_swarm2_entry.delete(0, tk.END)
        sgo_population_entry.delete(0, tk.END)
        result_label.config(text="")
        convergence_label.config(text="")
        global canvas
        if canvas:
            canvas.get_tk_widget().destroy()
            canvas = None
    def update_results():
        global convergence_iteration_vppso, sgo_fitness_curve, vppso_fitness_curve, canvas, fig, convergence_frame, Fitness_Curve, convergence_iteration
        convergence_iteration_vppso = 0
        sgo_fitness_curve = None
        vppso_fitness_curve = None
        global canvas , fig


        selected_function = function_var.get()
        fitness_function = None
        if selected_function == "Rastrigin":
            fitness_function = f1
        elif selected_function == "Sphere":
            fitness_function = f2
        elif selected_function == "Rosenbrock":
            fitness_function = f3
        elif selected_function == "Griewank":
            fitness_function = f4
        elif selected_function == "Ackley":
            fitness_function = f5

        if fitness_function:
            if fitness_function:
                max_iter = int(max_iter_entry.get())
                sgo_population = int(sgo_population_entry.get())
                vppso_swarm1_size = int(vppso_swarm1_entry.get())
                vppso_swarm2_size = int(vppso_swarm2_entry.get())
                dim = int(dim_entry.get())
                minx = float(minx_entry.get())
                maxx = float(maxx_entry.get())
                vppso_swarm2_size = int(vppso_swarm2_entry.get())  # Get the value from the GUI

                # Check for out of range values
                if not (-200 <= minx <= 200):
                    messagebox.showerror("Error", "MIN X should be in the range of -200 to 200.")
                    return
                if not (-200 <= maxx <= 200):
                    messagebox.showerror("Error", "MAX X should be in the range of -200 to 200.")
                    return
                if not (1 <= sgo_population <= 500):
                    messagebox.showerror("Error", "SGO Population should be in the range of 1 to 500.")
                    return
            vppso_swarm2_size = int(vppso_swarm2_entry.get())  # Get the value from the GUI

            best_position, fitness_value, convergence_iteration, Fitness_Curve, sgo_fitness_curve, vppso_best_position, vppso_fitness_curve = run_optimization(
                fitness_function, max_iter, sgo_population, vppso_swarm2_size, dim, minx, maxx)

            result_label.config(text=f"Best Fitness: {fitness_value}")
            convergence_label.config(text=f"Convergence Iteration: {convergence_iteration}")
            canvas = None

            # Clear the previous figure and canvas
        if fig:
            plt.close(fig)
        if canvas:
            canvas.get_tk_widget().destroy()

        # Remove the entire convergence_frame
        convergence_frame.pack_forget()

        # Recreate the convergence_frame
        convergence_frame = tk.Frame(root, padx=20, pady=20)
        convergence_frame.pack(side=tk.LEFT)

        # Create a new figure for the graph
        fig = plt.figure(figsize=(8, 6))

        # Plot the convergence curve
        plt.plot(Fitness_Curve, label='Optimization Fitness Curve')
        plt.plot(sgo_fitness_curve, label='SGO Fitness Curve', linestyle='solid')
        plt.plot(vppso_fitness_curve, label='VPPSO Fitness Curve', linestyle='solid')
        plt.axvline(x=convergence_iteration, color='g', linestyle='--', label='Convergence Point (SGO)')
        plt.axvline(x=convergence_iteration_vppso, color='r', linestyle='--', label='Convergence Point (VPPSO)')
        plt.title('Convergence curve')
        plt.xlabel('Iteration')
        plt.ylabel('Best Fitness')
        plt.legend()
        plt.grid(True)

        # Create a new canvas for the graph
        canvas = FigureCanvasTkAgg(fig, master=convergence_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    # Create the main application window
    root = tk.Tk()
    root.configure(bg='white')
    root.title("Optimization GUI")

    style = ttk.Style()
    style.theme_use('alt')

    # Set the background color for the TFrame widget type
    style.configure('TFrame', background='white')

    # Create a frame for input parameters with some padding
    input_frame = ttk.Frame(root)
    input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a label for function selection
    label = tk.Label(input_frame, text="Select a Function:")
    label.pack()

    # Create a dropdown menu for function selection
    function_options = ["Rastrigin", "Sphere", "Rosenbrock", "Griewank", "Ackley"]
    function_var = tk.StringVar(input_frame)
    function_var.set(function_options[0])
    function_dropdown = tk.OptionMenu(input_frame, function_var, *function_options)
    function_dropdown.pack()

    # Create input fields for common parameters
    common_params_label = tk.Label(input_frame, text="Common Parameters")
    common_params_label.pack()

    max_iter_label = tk.Label(input_frame, text="Max Iterations:")
    max_iter_label.pack()
    max_iter_entry = tk.Entry(input_frame)
    max_iter_entry.pack()

    dim_label = tk.Label(input_frame, text="Dimension:")
    dim_label.pack()
    dim_entry = tk.Entry(input_frame)
    dim_entry.pack()

    minx_label = tk.Label(input_frame, text="Min X:")
    minx_label.pack()
    minx_entry = tk.Entry(input_frame)
    minx_entry.pack()

    maxx_label = tk.Label(input_frame, text="Max X:")
    maxx_label.pack()
    maxx_entry = tk.Entry(input_frame)
    maxx_entry.pack()

    # Create a section for VPPSO parameters
    vppso_params_label = tk.Label(input_frame, text="VPPSO Values")
    vppso_params_label.pack()

    vppso_swarm1_label = tk.Label(input_frame, text="Swarm 1 Size:")
    vppso_swarm1_label.pack()
    vppso_swarm1_entry = tk.Entry(input_frame)
    vppso_swarm1_entry.pack()

    vppso_swarm2_label = tk.Label(input_frame, text="Swarm 2 Size:")
    vppso_swarm2_label.pack()
    vppso_swarm2_entry = tk.Entry(input_frame)
    vppso_swarm2_entry.pack()

    # Create a section for SGO parameters
    sgo_params_label = tk.Label(input_frame, text="SGO Values")
    sgo_params_label.pack()

    sgo_population_label = tk.Label(input_frame, text="SGO Population:")
    sgo_population_label.pack()
    sgo_population_entry = tk.Entry(input_frame)
    sgo_population_entry.pack()

    # Create a button to start optimization
    optimize_button = tk.Button(input_frame, text="Optimize", command=update_results)
    optimize_button.pack()

    reset_button = tk.Button(input_frame, text="Reset", command=reset_values)
    reset_button.pack()

    # Create labels for results
    result_label = tk.Label(input_frame, text="")
    result_label.pack()

    convergence_label = tk.Label(input_frame, text="")
    convergence_label.pack()

    # Create a border line
    border_line = tk.Frame(root, width=2, bg='gray')
    border_line.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Create a frame for convergence graph and points with some padding
    convergence_frame = ttk.Frame(root, padding="10 10 10 10")
    convergence_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a label for the convergence graph
    convergence_graph_label = tk.Label(convergence_frame, text="Convergence Graph")
    convergence_graph_label.pack()

    # Initialize convergence points for VPPSO and SGO
    convergence_iteration_vppso = 0

    # Initialize the canvas widget
    canvas = None

    # Run the main event loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()