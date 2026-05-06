"""
CSV Parser for Keysight B1500A I/V Sweep Data
Handles the specific CSV format with metadata header and DataValue entries
"""

import numpy as np


def parse_b1500_csv(file_path):
    """
    Parse Keysight B1500A I/V Sweep CSV data.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
    
    Returns:
    --------
    dict
        Dictionary containing 'V' (voltage) and 'I' (current) arrays
    """
    voltage = []
    current = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    data_name_v = None
    data_name_i = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('DataName,'):
            parts = line.split(',')
            if len(parts) >= 3:
                data_name_v = parts[1].strip()
                data_name_i = parts[2].strip()
                continue
        
        if line.startswith('DataValue,'):
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    v = float(parts[1])
                    i = float(parts[2])
                    voltage.append(v)
                    current.append(i)
                except ValueError:
                    continue
    
    if len(voltage) == 0:
        raise ValueError("No DataValue entries found in CSV")
    
    return {
        'V': np.array(voltage),
        'I': np.array(current)
    }


def load_diode_data(file_path):
    """
    Load diode I/V data from CSV file.
    Supports both simple format (Voltage,Current) and Keysight B1500A format.
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read(5000)
        
        if 'SetupTitle' in content or 'DataValue' in content:
            return parse_b1500_csv(file_path)
        
        import pandas as pd
        df = pd.read_csv(file_path)
        if 'Voltage' in df.columns and 'Current' in df.columns:
            return {
                'V': df['Voltage'].values,
                'I': df['Current'].values
            }
        elif 'V' in df.columns and 'I' in df.columns:
            return {
                'V': df['V'].values,
                'I': df['I'].values
            }
        else:
            raise ValueError("CSV must contain 'Voltage' and 'Current' columns")
                
    except Exception as e:
        raise Exception(f"Failed to load CSV: {str(e)}")


def preprocess_data(V, I):
    """
    Preprocess I/V data for diode parameter calculation.
    Filters valid data points (positive V and I for forward bias region).
    
    Parameters:
    -----------
    V : array-like
        Voltage values
    I : array-like
        Current values
    
    Returns:
    --------
    tuple
        (V_filtered, I_filtered) - filtered arrays
    """
    V = np.array(V)
    I = np.array(I)
    
    forward_mask = (V > 0) & (I > 0)
    V_forward = V[forward_mask]
    I_forward = I[forward_mask]
    
    return V_forward, I_forward


def extract_diode_parameters(V, I):
    """
    Extract diode parameters from I/V data.
    
    Parameters:
    -----------
    V : array-like
        Voltage values
    I : array-like
        Current values
    
    Returns:
    --------
    dict
        Dictionary containing calculated parameters
    """
    k = 1.380649e-23
    q = 1.602176634e-19
    T = 300
    
    V_forward, I_forward = preprocess_data(V, I)
    
    if len(V_forward) < 2:
        raise ValueError("Insufficient forward bias data points")
    
    ln_I = np.log(I_forward)
    coeffs = np.polyfit(V_forward, ln_I, 1)
    slope = coeffs[0]
    intercept = coeffs[1]
    
    n = (k * T / q) * slope
    Is = np.exp(intercept)
    
    Rs = 0
    
    v_on = V_forward[np.argmax(I_forward > I_forward[0] * 1.1)]
    
    return {
        'ideality_factor': n,
        'saturation_current': Is,
        'series_resistance': Rs,
        'turn_on_voltage': v_on,
        'data_points': len(V_forward)
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        data = load_diode_data(sys.argv[1])
        params = extract_diode_parameters(data['V'], data['I'])
        
        print(f"Loaded {params['data_points']} data points")
        print(f"Ideality Factor (n): {params['ideality_factor']:.4f}")
        print(f"Saturation Current (Is): {params['saturation_current']:.4e} A")
        print(f"Turn-on Voltage: {params['turn_on_voltage']:.4f} V")
    else:
        print("Usage: python csv_parser.py <csv_file>")