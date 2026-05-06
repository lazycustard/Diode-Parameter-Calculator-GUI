# Diode Parameter Calculator

A Python GUI application for analyzing diode I-V characteristics and calculating diode parameters from CSV data.

## Features

- Upload Keysight B1500A I/V Sweep CSV files
- Calculate Ideality Factor (n) and Saturation Current (Is)
- Interactive I-V curve plotting with zoom/pan
- Log/Linear scale toggle
- Custom axis ranges
- Export results

## Requirements

- Python 3.8+
- numpy
- matplotlib
- pandas

## Installation

### 1. Clone/Copy the Project

Copy the project folder to your desired location on any computer.

### 2. Install Dependencies

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
cd path/to/imt_pbl
pip install numpy matplotlib pandas
```

Or create a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate     # Mac/Linux
pip install numpy matplotlib pandas
```

## Project Structure

```
imt_pbl/
├── gui.py                    # Main application
├── csv_parser.py             # CSV parsing module
├── ideality_factor_and_Is.py # Ideality factor calculation
├── saturation_current.py     # Saturation current calculation
└── sample_diode_data.csv     # Sample data file
```

## Running the Application

### Step 1: Navigate to Project Folder

```bash
cd path/to/imt_pbl
```

### Step 2: Run the Application

```bash
python gui.py
```

The GUI window will open.

## How to Use

### 1. Upload CSV File
- Click **"📂 Upload CSV File"** button
- Select your Keysight B1500A I/V Sweep CSV file

### 2. Analyze Data
- Click **"🔬 Analyze Data"** button
- Results will appear in the Results section

### 3. Customize Graph
- **X:** Set X-axis range (e.g., -5 to 5)
- **Y:** Set Y-axis range (e.g., 1e-8 to 1e-2)
- **Apply:** Apply custom ranges
- **Log:** Toggle log/linear scale
- **+ / -:** Zoom in/out
- **Reset:** Reset to default view

### 4. Export Results
- Click **"��� Export"** button
- Choose file location to save results

## CSV File Format

The application accepts Keysight B1500A I/V Sweep format:

```csv
SetupTitle, I/V Sweep
...
DataName, V1, I1
DataValue, 0.1, 1.2e-9
DataValue, 0.2, 3.5e-9
...
```

Or simple format:

```csv
Voltage,Current
0.1,1.2e-9
0.2,3.5e-9
```

## Troubleshooting

### Error: Module not found
```
pip install numpy matplotlib pandas
```

### Error: tkinter not found
- **Windows:** Reinstall Python from python.org, ensure TCL/TK option is checked
- **Linux:** `sudo apt install python3-tk`
- **Mac:** `brew install python-tk@3.x`

### CSV parsing errors
- Ensure CSV file is not corrupted
- Verify file has proper DataValue entries
- Check file encoding is UTF-8

## Testing with Sample Data

A sample CSV file `sample_diode_data.csv` is included for testing.

## Quick Start Commands

```bash
# Full setup on fresh computer
cd path/to/imt_pbl
pip install numpy matplotlib pandas
python gui.py
```

## Notes

- Mouse hover over graph shows X,Y coordinates
- Use Log scale for better visualization of diode characteristics
- Y-axis typically uses scientific notation (1e-8 to 1e-2)