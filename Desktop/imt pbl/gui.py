"""
Diode Parameter Calculator - Enhanced GUI
Supports Keysight B1500A I/V Sweep CSV format
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from csv_parser import load_diode_data, preprocess_data
from ideality_factor_and_Is import analyze_diode
from saturation_current import calculate_saturation_current


class DiodeParameterCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Diode Parameter Calculator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self.file_path = None
        self.voltage_data = None
        self.current_data = None
        self.parameters = None
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#2c3e50")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#7f8c8d")
        style.configure("Result.TLabel", font=("Segoe UI", 12), foreground="#2c3e50")
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground="#2c3e50")
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
        style.configure("Accent.TButton", background="#3498db", foreground="white")
        
        style.map("Accent.TButton", background=[('active', '#2980b9')])
        
        style.configure("Card.TFrame", background="#ecf0f1", relief="solid", borderwidth=1)
        
    def setup_ui(self):
        self.root.configure(bg="#f5f6fa")
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="⚡ Diode Parameter Calculator", style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Analyze I/V characteristics and extract diode parameters", style="Subtitle.TLabel")
        subtitle_label.pack()
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        self.setup_upload_section(left_frame)
        self.setup_controls_section(left_frame)
        self.setup_results_section(left_frame)
        
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.setup_graph_section(right_frame)
        
        self.setup_status_bar(main_frame)
        
    def setup_upload_section(self, parent):
        upload_card = ttk.LabelFrame(parent, text="📂 Data Upload", padding="15")
        upload_card.pack(pady=(0, 10), fill=tk.X)
        
        self.upload_btn = ttk.Button(upload_card, text="Upload CSV File", command=self.upload_file, style="Accent.TButton")
        self.upload_btn.pack(pady=5)
        
        self.file_label = ttk.Label(upload_card, text="No file selected", foreground="gray", font=("Segoe UI", 9, "italic"), wraplength=250)
        self.file_label.pack(pady=5)
        
        self.data_info_label = ttk.Label(upload_card, text="", foreground="#3498db", font=("Segoe UI", 9))
        self.data_info_label.pack(pady=2)
        
    def setup_controls_section(self, parent):
        controls_card = ttk.LabelFrame(parent, text="🎛️ Controls", padding="15")
        controls_card.pack(pady=(0, 10), fill=tk.X)
        
        self.analyze_btn = ttk.Button(controls_card, text="🔬 Analyze Data", command=self.analyze_data, style="Accent.TButton")
        self.analyze_btn.pack(pady=5, fill=tk.X)
        self.analyze_btn.state(["disabled"])
        
        button_frame = ttk.Frame(controls_card)
        button_frame.pack(pady=10, fill=tk.X)
        
        self.export_btn = ttk.Button(button_frame, text="📊 Export", command=self.export_results, state="disabled")
        self.export_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        
        self.reset_btn = ttk.Button(button_frame, text="🔄 Reset", command=self.reset)
        self.reset_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))
        
    def setup_results_section(self, parent):
        results_card = ttk.LabelFrame(parent, text="📋 Results", padding="15")
        results_card.pack(pady=(0, 10), fill=tk.BOTH, expand=True)
        
        params_frame = ttk.Frame(results_card)
        params_frame.pack(fill=tk.X)
        
        self.create_result_label(params_frame, "ideality", "Ideality Factor (n)", "🔶")
        self.create_result_label(params_frame, "saturation", "Saturation Current (Is)", "⚡")
        self.create_result_label(params_frame, "turnon", "Turn-on Voltage", "📈")
        self.create_result_label(params_frame, "datapoints", "Valid Data Points", "📊")
        self.create_result_label(params_frame, "rs", "Series Resistance", "🔗")
        
        separator = ttk.Separator(results_card, orient='horizontal')
        separator.pack(pady=10, fill=tk.X)
        
        stats_frame = ttk.Frame(results_card)
        stats_frame.pack(fill=tk.X)
        
        self.create_stat_label(stats_frame, "vmax", "Max Voltage", "V")
        self.create_stat_label(stats_frame, "imax", "Max Current", "A")
        self.create_stat_label(stats_frame, "slope", "Slope (nq/kT)", "1/V")
        
    def create_result_label(self, parent, key, text, icon):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)
        
        icon_label = ttk.Label(frame, text=icon, font=("Segoe UI", 10))
        icon_label.pack(side=tk.LEFT, padx=(0, 5))
        
        label = ttk.Label(frame, text=f"{text}: --", style="Result.TLabel")
        label.pack(side=tk.LEFT)
        
        setattr(self, f"{key}_label", label)
        
    def create_stat_label(self, parent, key, text, unit):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        label = ttk.Label(frame, text=f"{text}: --", font=("Segoe UI", 9), foreground="#7f8c8d")
        label.pack(side=tk.LEFT)
        
        setattr(self, f"{key}_label", label)
        
    def setup_graph_section(self, parent):
        graph_card = ttk.LabelFrame(parent, text="📈 I-V Characteristic", padding="5")
        graph_card.pack(fill=tk.BOTH, expand=True)
        
        # Controls row
        control_frame = ttk.Frame(graph_card, height=30)
        control_frame.pack(fill=tk.X, pady=2)
        control_frame.pack_propagate(False)
        
        # X range
        self.x_min_var = tk.StringVar(value="-5")
        self.x_max_var = tk.StringVar(value="5")
        ttk.Label(control_frame, text="X:", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(2, 0))
        ttk.Entry(control_frame, textvariable=self.x_min_var, width=5).pack(side=tk.LEFT, padx=1)
        ttk.Label(control_frame, text=":", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Entry(control_frame, textvariable=self.x_max_var, width=5).pack(side=tk.LEFT, padx=1)
        
        # Y range
        self.y_min_var = tk.StringVar(value="1e-8")
        self.y_max_var = tk.StringVar(value="1e-2")
        ttk.Label(control_frame, text="Y:", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Entry(control_frame, textvariable=self.y_min_var, width=7).pack(side=tk.LEFT, padx=1)
        ttk.Label(control_frame, text=":", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Entry(control_frame, textvariable=self.y_max_var, width=7).pack(side=tk.LEFT, padx=1)
        
        # Apply button
        ttk.Button(control_frame, text="Apply", command=self.apply_axis_range, width=5).pack(side=tk.LEFT, padx=5)
        
        # Scale toggle
        self.log_scale_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Log", variable=self.log_scale_var, command=self.toggle_scale).pack(side=tk.LEFT, padx=5)
        
        # Zoom buttons
        ttk.Button(control_frame, text="+", command=self.zoom_in, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="-", command=self.zoom_out, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Reset", command=self.reset_zoom, width=5).pack(side=tk.LEFT, padx=2)
        
        # Chart area
        self.figure = plt.figure(figsize=(5, 4), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
    def setup_status_bar(self, parent):
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready - Upload a CSV file to begin", foreground="#7f8c8d", font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(status_frame, text="v1.0", foreground="#bdc3c7", font=("Segoe UI", 8))
        version_label.pack(side=tk.RIGHT)
        
    def plot_empty_graph(self):
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        ax.text(0.5, 0.5, 'Upload data to see I-V curve', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='#bdc3c7')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.figure.tight_layout()
        self.canvas.draw()
        
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path = file_path
            file_name = file_path.split('/')[-1]
            self.file_label.config(text=f"📁 {file_name}", foreground="#2c3e50")
            self.load_data()
            
    def load_data(self):
        try:
            data = load_diode_data(self.file_path)
            self.voltage_data = data['V']
            self.current_data = data['I']
            
            v_range = f"{self.voltage_data.min():.2f}V to {self.voltage_data.max():.2f}V"
            self.data_info_label.config(text=f"⚡ {len(self.voltage_data)} points | {v_range}")
            
            # Auto-set Y range based on data
            max_curr = float(np.max(np.abs(self.current_data)))
            exp_val = int(np.floor(np.log10(max_curr)))
            y_max_auto = round(max_curr / (10**exp_val), 1) * (10**exp_val)
            self.y_max_var.set(f"{y_max_auto:.2e}")
            self.y_min_var.set(f"{10**(exp_val-6):.0e}")
            
            # Auto-set X range based on data
            x_min_auto = float(np.min(self.voltage_data))
            x_max_auto = float(np.max(self.voltage_data))
            self.x_min_var.set(int(x_min_auto) - 1)
            self.x_max_var.set(int(x_max_auto) + 1)
            
            self.analyze_btn.state(["!disabled"])
            self.update_status(f"Loaded {len(self.voltage_data)} data points successfully")
            
        except Exception as e:
            import traceback
            messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")
            self.file_path = None
            self.file_label.config(text="No file selected", foreground="gray")
            self.data_info_label.config(text="")
            
    def analyze_data(self):
        if self.file_path is None:
            messagebox.showwarning("Warning", "Please upload a CSV file first.")
            return
            
        try:
            V_forward, I_forward = preprocess_data(self.voltage_data, self.current_data)
            
            if len(V_forward) < 5:
                messagebox.showerror("Error", "Insufficient forward bias data points. Need at least 5 points with V>0 and I>0.")
                return
            
            # Use external modules for calculations
            T = 300  # Room temperature
            
            # Use calculate_saturation_current from saturation_current.py for Is
            Is = calculate_saturation_current(self.file_path)
            
            # Use analyze_diode from ideality_factor_and_Is.py for ideality factor (n)
            _, n = analyze_diode(self.file_path, T)
            
            # Calculate turn-on voltage
            v_on_idx = np.argmax(I_forward > I_forward[0] * 1.1)
            v_on = float(V_forward[v_on_idx]) if v_on_idx > 0 else 0.0
            
            self.parameters = {
                'ideality_factor': n,
                'saturation_current': Is,
                'turn_on_voltage': v_on,
                'data_points': len(V_forward),
                'series_resistance': 0
            }
            
            self.ideality_label.config(text=f"Ideality Factor (n): {n:.4f}")
            self.saturation_label.config(text=f"Saturation Current (Is): {Is:.4e} A")
            self.turnon_label.config(text=f"Turn-on Voltage: {v_on:.3f} V")
            self.datapoints_label.config(text=f"Valid Data Points: {len(V_forward)}")
            
            self.rs_label.config(text=f"Series Resistance: 0 Ω")
            
            self.vmax_label.config(text=f"Max Voltage: {float(self.voltage_data.max()):.3f} V")
            self.imax_label.config(text=f"Max Current: {float(self.current_data.max()):.3e} A")
            
            k = 1.380649e-23
            q = 1.602176634e-19
            theoretical_slope = q / (k * T)
            self.slope_label.config(text=f"Slope (q/kT): {theoretical_slope:.1f} 1/V")
            
            self.export_btn.state(["!disabled"])
            
            self.plot_iv_curve()
            self.update_status("Analysis completed successfully")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Analysis Error", f"Error during analysis:\n{str(e)}")
            
    def plot_iv_curve(self):
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.set_facecolor('#f8f9fa')
        self.current_ax = ax
        
        is_log = self.log_scale_var.get()
        
        # Use absolute values for log scale, full values for linear
        if is_log:
            # For log scale, use abs values
            abs_current = np.abs(self.current_data)
            abs_current = np.where(abs_current > 0, abs_current, 1e-15)  # Avoid log(0)
            
            ax.semilogy(self.voltage_data, abs_current, 'b-', linewidth=1.5, alpha=0.7, label='|Current|')
            
            V_forward, I_forward = preprocess_data(self.voltage_data, self.current_data)
            if len(V_forward) > 0:
                ax.semilogy(V_forward, I_forward, 'r.', markersize=6, alpha=0.8, label='Forward Bias')
                
                ln_I = np.log(I_forward)
                coeffs = np.polyfit(V_forward, ln_I, 1)
                V_fit = np.linspace(max(0.1, V_forward.min()), V_forward.max(), 100)
                I_fit = np.exp(coeffs[0] * V_fit + coeffs[1])
                ax.semilogy(V_fit, I_fit, 'g--', linewidth=1.5, alpha=0.8, label='Linear Fit')
            
            title_scale = "Semi-log"
        else:
            # Linear scale - show raw data including negative
            ax.plot(self.voltage_data, self.current_data, 'b-', linewidth=1.5, alpha=0.7, label='I-V Curve')
            
            V_forward, I_forward = preprocess_data(self.voltage_data, self.current_data)
            if len(V_forward) > 0:
                ax.plot(V_forward, I_forward, 'r.', markersize=6, alpha=0.8, label='Forward Bias')
            
            title_scale = "Linear"
        
        ax.set_title(f'Diode I-V Characteristic ({title_scale})', fontsize=14, fontweight='bold', pad=10)
        
        ax.set_xlabel('Voltage (V)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Current (A)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best', framealpha=0.9)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def apply_axis_range(self):
        if not hasattr(self, 'current_ax') or self.current_ax is None:
            return
        try:
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            y_min = float(self.y_min_var.get())
            y_max = float(self.y_max_var.get())
            
            self.current_ax.set_xlim(x_min, x_max)
            self.current_ax.set_ylim(y_min, y_max)
            self.figure.canvas.draw()
            self.update_status("Range applied")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid range: {e}")
            
    def on_mouse_move(self, event):
        if event.inaxes and hasattr(self, 'current_ax'):
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                self.update_status(f"X: {x:.3f}  Y: {y:.3e}")
            
    def toggle_scale(self):
        self.plot_iv_curve()
        
    def zoom_in(self):
        if not hasattr(self, 'current_ax') or self.current_ax is None:
            return
        try:
            xlim = self.current_ax.get_xlim()
            x_center = (xlim[0] + xlim[1]) / 2
            x_range = xlim[1] - xlim[0]
            new_range = x_range * 0.5
            self.current_ax.set_xlim(x_center - new_range/2, x_center + new_range/2)
            
            is_log = self.log_scale_var.get()
            if not is_log:
                ylim = self.current_ax.get_ylim()
                y_center = (ylim[0] + ylim[1]) / 2
                y_range = ylim[1] - ylim[0]
                new_y_range = y_range * 0.5
                self.current_ax.set_ylim(y_center - new_y_range/2, y_center + new_y_range/2)
            
            self.figure.canvas.draw()
        except:
            pass
        
    def zoom_out(self):
        if not hasattr(self, 'current_ax') or self.current_ax is None:
            return
        try:
            xlim = self.current_ax.get_xlim()
            x_center = (xlim[0] + xlim[1]) / 2
            x_range = xlim[1] - xlim[0]
            new_range = min(x_range * 2, 100)  # Limit max range
            self.current_ax.set_xlim(x_center - new_range/2, x_center + new_range/2)
            
            is_log = self.log_scale_var.get()
            if not is_log:
                ylim = self.current_ax.get_ylim()
                y_center = (ylim[0] + ylim[1]) / 2
                y_range = ylim[1] - ylim[0]
                new_y_range = min(y_range * 2, 1)
                self.current_ax.set_ylim(max(0, y_center - new_y_range/2), y_center + new_y_range/2)
            
            self.figure.canvas.draw()
        except:
            pass
        
    def reset_zoom(self):
        self.plot_iv_curve()
        self.update_status("Zoom reset")
        
    def on_click(self, event):
        if event.inaxes == self.current_ax and event.button == 1:
            self.drag_start = (event.xdata, event.ydata)
            
    def on_release(self, event):
        if hasattr(self, 'drag_start') and self.drag_start and event.inaxes == self.current_ax:
            dx = self.drag_start[0] - event.xdata
            dy = self.drag_start[1] - event.ydata
            
            xlim = self.current_ax.get_xlim()
            ylim = self.current_ax.get_ylim()
            
            self.current_ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
            self.current_ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
            self.figure.canvas.draw()
            self.drag_start = None
        
    def export_results(self):
        if self.parameters is None:
            messagebox.showwarning("Warning", "No analysis results to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("Diode Parameter Analysis Results\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Ideality Factor (n): {self.parameters['ideality_factor']:.6f}\n")
                    f.write(f"Saturation Current (Is): {self.parameters['saturation_current']:.6e} A\n")
                    f.write(f"Turn-on Voltage: {self.parameters['turn_on_voltage']:.4f} V\n")
                    f.write(f"Valid Data Points: {self.parameters['data_points']}\n")
                    if 'series_resistance' in self.parameters:
                        f.write(f"Series Resistance: {self.parameters['series_resistance']:.6f} Ω\n")
                    f.write("\n" + "=" * 40 + "\n")
                    f.write(f"File: {self.file_path}\n")
                    
                messagebox.showinfo("Success", f"Results saved to:\n{file_path}")
                self.update_status("Results exported successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results:\n{str(e)}")
                
    def update_status(self, message):
        self.status_label.config(text=message, foreground="#27ae60")
        
    def reset(self):
        self.file_path = None
        self.voltage_data = None
        self.current_data = None
        self.parameters = None
        
        self.file_label.config(text="No file selected", foreground="gray")
        self.data_info_label.config(text="")
        
        self.ideality_label.config(text="Ideality Factor (n): --")
        self.saturation_label.config(text="Saturation Current (Is): --")
        self.turnon_label.config(text="Turn-on Voltage: --")
        self.datapoints_label.config(text="Valid Data Points: --")
        self.rs_label.config(text="Series Resistance: --")
        
        self.vmax_label.config(text="Max Voltage: --")
        self.imax_label.config(text="Max Current: --")
        self.slope_label.config(text="Slope (q/kT): --")
        
        self.plot_empty_graph()
        
        self.analyze_btn.state(["disabled"])
        self.export_btn.state(["disabled"])
        self.update_status("Ready - Upload a CSV file to begin")


def main():
    root = tk.Tk()
    app = DiodeParameterCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()