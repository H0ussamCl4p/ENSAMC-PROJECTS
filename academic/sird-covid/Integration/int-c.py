import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"
df_I = pd.read_excel(filepath, sheet_name="Infected").iloc[1:].reset_index(drop=True)
df_R = pd.read_excel(filepath, sheet_name="Recovered").iloc[1:].reset_index(drop=True)
df_D = pd.read_excel(filepath, sheet_name="DeathC").iloc[1:].reset_index(drop=True)
df_S = pd.read_excel(filepath, sheet_name="Susceptible").iloc[1:].reset_index(drop=True)
N = 265185520  
t = df_I.iloc[:, 0].values  
I_data = df_I.iloc[:, 1].values / N    
R_data = df_R.iloc[:, 1].values / N     
D_data = df_D.iloc[:, 1].values / N     
S_data = df_S.iloc[:, 1].values / N    

def calculate_dIdt(I, t):
    dIdt = np.zeros_like(I)
    dIdt[0] = (I[1] - I[0]) / (t[1] - t[0])
    for i in range(1, len(I)-1):
        dIdt[i] = (I[i+1] - I[i-1]) / (t[i+1] - t[i-1])
    dIdt[-1] = (I[-1] - I[-2]) / (t[-1] - t[-2])
    return dIdt

dIdt = calculate_dIdt(I_data, t)
peak_idx = np.argmax(I_data)
threshold = 0.000009

end_idx = None
for i in range(peak_idx, len(I_data)):
    if I_data[i] < threshold:
        end_idx = i
        break

n_to_peak = peak_idx
n_peak_to_end = end_idx - peak_idx if end_idx is not None else len(t) - peak_idx
n_total = end_idx if end_idx is not None else len(t) - 1

def rectangle_method(f, a, b, n):
    h = (t[b] - t[a]) / n
    integral = 0
    idx = np.linspace(a, b, n+1, dtype=int)
    for i in range(n):
        integral += f[idx[i]] * (t[idx[i+1]] - t[idx[i]])
    return integral

def trapezoid_method(f, a, b, n):
    integral = 0
    idx = np.linspace(a, b, n+1, dtype=int)
    for i in range(n):
        integral += 0.5 * (f[idx[i]] + f[idx[i+1]]) * (t[idx[i+1]] - t[idx[i]])
    return integral

def simpson_method(f, a, b, n):
    if n % 2 != 0:
        n += 1  
    integral = 0
    idx = np.linspace(a, b, n+1, dtype=int)
    for i in range(0, n, 2):
        if i+2 > n:
            break     
        h = (t[idx[i+2]] - t[idx[i]]) / 2
        integral += (h/6) * (f[idx[i]] + 4*f[idx[i+1]] + f[idx[i+2]])
    return integral

def calculate_cumulative_integral(f, a, b, n, method_name):
    idx = np.linspace(a, b, n+1, dtype=int)
    times = t[idx]
    cumulative_integral = np.zeros(n+1)
    if method_name == "Rectangle":
        for i in range(n):
            if i > 0:
                cumulative_integral[i+1] = cumulative_integral[i] + f[idx[i]] * (t[idx[i+1]] - t[idx[i]])
            else:
                cumulative_integral[i+1] = f[idx[i]] * (t[idx[i+1]] - t[idx[i]])
    elif method_name == "Trapèze":
        for i in range(n):
            if i > 0:
                cumulative_integral[i+1] = cumulative_integral[i] + 0.5 * (f[idx[i]] + f[idx[i+1]]) * (t[idx[i+1]] - t[idx[i]])
            else:
                cumulative_integral[i+1] = 0.5 * (f[idx[i]] + f[idx[i+1]]) * (t[idx[i+1]] - t[idx[i]])
    elif method_name == "Simpson":
        if n % 2 != 0:
            n -= 1
        for i in range(0, n, 2):
            if i+2 <= n:
                h = (t[idx[i+2]] - t[idx[i]]) / 2
                if i > 0:
                    cumulative_integral[i+2] = cumulative_integral[i] + (h/3) * (f[idx[i]] + 4*f[idx[i+1]] + f[idx[i+2]])
                else:
                    cumulative_integral[i+2] = (h/6) * (f[idx[i]] + 4*f[idx[i+1]] + f[idx[i+2]])
                if i+1 <= n:
                    cumulative_integral[i+1] = (cumulative_integral[i] + cumulative_integral[i+2]) / 2
    return times, cumulative_integral

class ScrollablePlotWindow(ctk.CTkToplevel):
    def __init__(self, fig, title="Graphique"):
        super().__init__()
        self.title(title)
        self.geometry("1200x900")

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = ctk.CTkCanvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = ctk.CTkFrame(canvas)
        scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_configure)

        fig_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
        fig_canvas.draw()
        fig_canvas.get_tk_widget().pack(fill="both", expand=True)

        def resize_canvas(event):
            canvas.itemconfig(scrollable_frame_id, width=event.width)
        canvas.bind("<Configure>", resize_canvas)

def show_results_window():
    fig = plt.figure(figsize=(14, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(t, I_data, 'b-', label='I(t) - données réelles', linewidth=2)
    rect_times, rect_cum = calculate_cumulative_integral(dIdt, peak_idx, end_idx, n_peak_to_end, "Rectangle")
    trap_times, trap_cum = calculate_cumulative_integral(dIdt, peak_idx, end_idx, n_peak_to_end, "Trapèze")
    simp_times, simp_cum = calculate_cumulative_integral(dIdt, peak_idx, end_idx, n_peak_to_end, "Simpson")
    exact_integral = I_data[end_idx] - I_data[peak_idx]
    norm_rect_cum = rect_cum / rect_cum[-1] * exact_integral + I_data[peak_idx]
    norm_trap_cum = trap_cum / trap_cum[-1] * exact_integral + I_data[peak_idx]
    norm_simp_cum = simp_cum / simp_cum[-1] * exact_integral + I_data[peak_idx]

    ax1.plot(rect_times, norm_rect_cum, 'r-', label='Estimation par rectangles')
    ax1.plot(trap_times, norm_trap_cum, 'g-', label='Estimation par trapèzes')
    ax1.plot(simp_times, norm_simp_cum, 'm-', label='Estimation par Simpson')
    ax1.axvline(x=t[peak_idx], color='k', linestyle='--', label=f'Pic (jour {t[peak_idx]:.1f})')
    ax1.axhline(y=threshold, color='k', linestyle=':', label=f'Seuil ({threshold*100:.4f}%)')
    rect_end = trap_end = simp_end = None
    for i in range(len(rect_times)):
        if norm_rect_cum[i] <= threshold:
            rect_end = rect_times[i]
            break
    for i in range(len(trap_times)):
        if norm_trap_cum[i] <= threshold:
            trap_end = trap_times[i]
            break
    for i in range(len(simp_times)):
        if norm_simp_cum[i] <= threshold:
            simp_end = simp_times[i]
            break
    if rect_end is not None:
        ax1.axvline(x=rect_end, color='r', linestyle='--')
    if trap_end is not None:
        ax1.axvline(x=trap_end, color='g', linestyle='--')
    if simp_end is not None:
        ax1.axvline(x=simp_end, color='m', linestyle='--')
    ax1.axvline(x=t[end_idx], color='cyan', linestyle='--', label=f'Fin réelle (jour {t[end_idx]:.1f})')
    ax1.set_title('Comparaison des méthodes d\'intégration pour la détermination de l\'arrêt de l\'épidémie')
    ax1.set_xlabel('Temps (jours)')
    ax1.set_ylabel('Fraction de la population')
    ax1.grid(True)
    ax1.legend()
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(t, I_data, 'b-', label='I(t) - données réelles', linewidth=2)
    ax2.plot(rect_times, norm_rect_cum, 'r-', label='Estimation par rectangles')
    ax2.plot(trap_times, norm_trap_cum, 'g-', label='Estimation par trapèzes')
    ax2.plot(simp_times, norm_simp_cum, 'm-', label='Estimation par Simpson')
    ax2.axhline(y=threshold, color='k', linestyle=':', label=f'Seuil ({threshold*100:.4f}%)')
    if rect_end is not None:
        ax2.axvline(x=rect_end, color='r', linestyle='--', label=f'Fin par rectangles (jour {rect_end:.1f})')
    if trap_end is not None:
        ax2.axvline(x=trap_end, color='g', linestyle='--', label=f'Fin par trapèzes (jour {trap_end:.1f})')
    if simp_end is not None:
        ax2.axvline(x=simp_end, color='m', linestyle='--', label=f'Fin par Simpson (jour {simp_end:.1f})')
    ax2.axvline(x=t[end_idx], color='cyan', linestyle='--', label=f'Fin réelle (jour {t[end_idx]:.1f})')
    ax2.set_ylim(0, threshold*10)
    zoom_start_idx = np.argmin(np.abs(t - (t[end_idx] - 50)))
    ax2.set_xlim(t[zoom_start_idx], t[end_idx] + 20)
    ax2.set_title('Zoom sur la région du seuil pour la détermination de l\'arrêt de l\'épidémie')
    ax2.set_xlabel('Temps (jours)')
    ax2.set_ylabel('Fraction de la population')
    ax2.grid(True)
    ax2.legend()
    fig.tight_layout()
    ScrollablePlotWindow(fig, title="Comparaison méthodes d'intégration")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Méthodes d'intégration - SIRD")
    app.geometry("400x200")
    ctk.CTkLabel(app, text="Méthodes d'intégration numérique\nSIRD - Visualisation interactive", font=("Arial", 16, "bold")).pack(pady=20)
    ctk.CTkButton(app, text="Afficher les résultats", command=show_results_window).pack(pady=10)
    ctk.CTkButton(app, text="Quitter", command=app.destroy).pack(pady=10)
    app.mainloop()