import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

file_path = ""

# Function to extract and calculate Is
def calculate_saturation_current(file_path):
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

    # Convert to DataFrame
    data = pd.DataFrame({
        "Voltage": voltages,
        "Current": currents
    })

    # Reverse region
    reverse_data = data[data['Voltage'] < 0]

    # Calculate Is
    Is = abs(reverse_data['Current'].mean())

    return Is


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

        Is = calculate_saturation_current(file_path)
        result_label.config(text=f"Is = {Is:.6e} A")

    except Exception as e:
        result_label.config(text="Error in calculation")
        print(e)


if __name__ == "__main__":
    # GUI setup
    root = tk.Tk()
    root.title("Diode Analyzer")
    root.geometry("400x250")

    btn_upload = tk.Button(root, text="Upload CSV", command=upload_file)
    btn_upload.pack(pady=10)

    btn_calculate = tk.Button(root, text="Calculate", command=calculate)
    btn_calculate.pack(pady=10)

    result_label = tk.Label(root, text="Result")
    result_label.pack(pady=20)

    root.mainloop()