import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

file_path = ""

# Constants
q = 1.602e-19   # Electron charge (C)
k = 1.38e-23    # Boltzmann constant (J/K)

# Function to extract and calculate Is and n
def analyze_diode(file_path, T):
    voltages = []
    currents = []

    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith("DataValue"):
                parts = line.strip().split(",")

                try:
                    voltage = float(parts[1])
                    current = float(parts[2])

                    voltages.append(voltage)
                    currents.append(current)
                except:
                    continue

    # Convert to numpy arrays
    V = np.array(voltages)
    I = np.array(currents)

    # -----------------------------
    # 1. Reverse Saturation Current (Is)
    # -----------------------------
    reverse_I = I[V < 0]

    if len(reverse_I) == 0:
        Is = 0
    else:
        Is = abs(np.mean(reverse_I))

    # -----------------------------
    # 2. Ideality Factor (n)
    # -----------------------------
    mask = (V > 0) & (I > 0)
    V_forward = V[mask]
    I_forward = I[mask]

    # Avoid log issues
    I_forward = np.where(I_forward <= 0, 1e-12, I_forward)

    ln_I = np.log(I_forward)

    # Linear fit
    slope, intercept = np.polyfit(V_forward, ln_I, 1)

    n = q / (k * T * slope)

    return Is, n


# GUI functions
def upload_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    
    if file_path:
        result_label.config(text="File uploaded successfully")


def calculate():
    try:
        if not file_path:
            messagebox.showerror("Error", "Please upload a file first")
            return

        # Get temperature from user
        T = float(temp_entry.get())

        if T <= 0:
            messagebox.showerror("Error", "Temperature must be > 0 K")
            return

        Is, n = analyze_diode(file_path, T)

        result_label.config(
            text=f"Reverse Saturation Current (Is) = {Is:.6e} A\n"
                 f"Ideality Factor (n) = {n:.3f}"
        )

    except ValueError:
        messagebox.showerror("Error", "Enter valid temperature")
    except Exception as e:
        result_label.config(text="Error in calculation")
        print(e)


if __name__ == "__main__":
    # GUI setup
    root = tk.Tk()
    root.title("Diode Analyzer")
    root.geometry("420x320")

    btn_upload = tk.Button(root, text="Upload CSV", command=upload_file)
    btn_upload.pack(pady=10)

    # Temperature input
    temp_label = tk.Label(root, text="Enter Temperature (K):")
    temp_label.pack()

    temp_entry = tk.Entry(root)
    temp_entry.pack(pady=5)

    btn_calculate = tk.Button(root, text="Calculate Is and n", command=calculate)
    btn_calculate.pack(pady=10)

    result_label = tk.Label(root, text="Result", justify="center")
    result_label.pack(pady=20)

    root.mainloop()
