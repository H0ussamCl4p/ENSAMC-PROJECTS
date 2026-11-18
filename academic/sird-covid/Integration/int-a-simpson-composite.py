import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def run_sird():
    r = 0.6
    a = 0.4
    b = 0.005
    N = 265185520

    filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"

    infected_df = pd.read_excel(filepath, sheet_name="Infected")
    recovered_df = pd.read_excel(filepath, sheet_name="RecoveredC")
    death_df = pd.read_excel(filepath, sheet_name="DeathC")
    susceptible_df = pd.read_excel(filepath, sheet_name="Susceptible")

    infected_df = infected_df.iloc[1:].reset_index(drop=True)
    recovered_df = recovered_df.iloc[1:].reset_index(drop=True)
    death_df = death_df.iloc[1:].reset_index(drop=True)
    susceptible_df = susceptible_df.iloc[1:].reset_index(drop=True)

    I = infected_df.iloc[:, 1].values / N
    R = recovered_df.iloc[:, 1].values / N
    D = death_df.iloc[:, 1].values / N
    S = susceptible_df.iloc[:, 1].values / N

    n = 54
    h = 2
    t0 = 1
    tf = 107
    t_values = np.linspace(t0, tf, n+1)
    S_values = np.zeros(n+1)
    I_values = np.zeros(n+1)
    R_values = np.zeros(n+1)
    D_values = np.zeros(n+1)

    S_values[0] = S[0]
    I_values[0] = I[0]
    R_values[0] = R[0]
    D_values[0] = D[0]

    for i in range(n):
        S, I, R, D = S_values[i], I_values[i], R_values[i], D_values[i]
        dSdt = -r * S * I
        dIdt = r * S * I - (a + b) * I
        dRdt = a * I
        dDdt = b * I

        k1_S, k1_I, k1_R, k1_D = h * dSdt, h * dIdt, h * dRdt, h * dDdt
        k2_S, k2_I, k2_R, k2_D = h * (-r * (S + k1_S/2) * (I + k1_I/2)), \
                                  h * (r * (S + k1_S/2) * (I + k1_I/2) - (a + b) * (I + k1_I/2)), \
                                  h * (a * (I + k1_I/2)), \
                                  h * (b * (I + k1_I/2))
        k3_S, k3_I, k3_R, k3_D = h * (-r * (S + k2_S/2) * (I + k2_I/2)), \
                                  h * (r * (S + k2_S/2) * (I + k2_I/2) - (a + b) * (I + k2_I/2)), \
                                  h * (a * (I + k2_I/2)), \
                                  h * (b * (I + k2_I/2))
        k4_S, k4_I, k4_R, k4_D = h * (-r * (S + k3_S) * (I + k3_I)), \
                                  h * (r * (S + k3_S) * (I + k3_I) - (a + b) * (I + k3_I)), \
                                  h * (a * (I + k3_I)), \
                                  h * (b * (I + k3_I))
        S_values[i+1] = S + (k1_S + 2*k2_S + 2*k3_S + k4_S) / 6
        I_values[i+1] = I + (k1_I + 2*k2_I + 2*k3_I + k4_I) / 6
        R_values[i+1] = R + (k1_R + 2*k2_R + 2*k3_R + k4_R) / 6
        D_values[i+1] = D + (k1_D + 2*k2_D + 2*k3_D + k4_D) / 6

    def simpson_composite(f_values, h):
        n_points = len(f_values)
        if n_points % 2 == 0:
            raise ValueError("Le nombre de points doit être impair pour la méthode de Simpson.")
        integral = f_values[0] + f_values[-1]
        integral += 4 * np.sum(f_values[1:-1:2])
        integral += 2 * np.sum(f_values[2:-2:2])
        return integral * h / 6

    dSdt_values = -r * S_values * I_values
    dRdt_values = a * I_values

    integral_dSdt_simpson = simpson_composite(dSdt_values, h)
    integral_dRdt_simpson = simpson_composite(dRdt_values, h)

    return t_values, S_values, I_values, R_values, D_values, integral_dSdt_simpson, integral_dRdt_simpson

class SIRDApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SIRD - Simpson Composite (CustomTkinter)")
        self.geometry("900x700")
        self.resizable(True, True)
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text="Modèle SIRD avec Intégration de Simpson Composite", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))

        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14, "bold"), text_color="#00ff99")
        self.result_label.pack(pady=10)

        self.plot_frame = ctk.CTkFrame(frame)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkButton(frame, text="Lancer le modèle", command=self.run_model, fg_color="#4CBB17", text_color="#fff", hover_color="#222").pack(pady=15)

    def run_model(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        try:
            t, S, I, R, D, intS, intR = run_sird()
            self.result_label.configure(
                text=f"∫dS/dt ≈ {intS:.6f}   |   ∫dR/dt ≈ {intR:.6f}",
                text_color="#00ff99"
            )
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(t, S, label="Susceptibles S(t)", color="#61afef")
            ax.plot(t, I, label="Infectés I(t)", color="#e06c75")
            ax.plot(t, R, label="Guéris R(t)", color="#98c379")
            ax.plot(t, D, label="Décédés D(t)", color="#abb2bf")
            ax.set_xlabel("Temps t", color="#fff")
            ax.set_ylabel("Fractions de la population", color="#fff")
            ax.set_title("Évolution des populations dans le modèle SIRD", color="#fff")
            ax.legend(facecolor="#23272e", edgecolor="#6272a4")
            ax.grid(True, color="#44475a")
            ax.set_facecolor("#23272e")
            ax.tick_params(colors="#fff")
            fig.patch.set_facecolor("#23272e")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

if __name__ == "__main__":
    app = SIRDApp()
    app.mainloop()