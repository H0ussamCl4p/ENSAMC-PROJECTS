import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

a = 0.4
r = 0.6
dt = 2
N = 265185520

filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"

infected_df = pd.read_excel(filepath, sheet_name="Infected")
recovered_df = pd.read_excel(filepath, sheet_name="RecoveredC")
death_df = pd.read_excel(filepath, sheet_name="DeathC")
infected_df = infected_df.iloc[1:].reset_index(drop=True)
recovered_df = recovered_df.iloc[1:].reset_index(drop=True)
death_df = death_df.iloc[1:].reset_index(drop=True)

time = infected_df.iloc[:, 0].values
I = infected_df.iloc[:, 1].values
R = recovered_df.iloc[:, 1].values
D = death_df.iloc[:, 1].values

I = I / N
S = (N - I - R - D) / N
R = R / N

dS_dt = []
dR_dt = []
time_deriv = []
n = len(time)
for k in range(n - dt):
    ds = (S[k + dt] - S[k]) / dt
    dr = (R[k + dt] - R[k]) / dt
    dS_dt.append(ds)
    dR_dt.append(dr)
    time_deriv.append(time[k])
dS_dt = np.array(dS_dt)
dR_dt = np.array(dR_dt)
time_deriv = np.array(time_deriv)

variation_df = pd.DataFrame({
    'Temps': time_deriv,
    'dS/dt': dS_dt,
    'dR/dt': dR_dt
})

class DerivationSRApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Taux de variation de S(t) et R(t)")
        self.geometry("600x300")
        self.resizable(False, False)
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Taux de variation de S(t) et R(t)", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        stats = (
            f"Taux de variation moyen de S(t) : {np.mean(dS_dt):.4e} par unité de temps\n"
            f"Taux de variation moyen de R(t) : {np.mean(dR_dt):.4e} par unité de temps"
        )
        ctk.CTkLabel(frame, text=stats, font=("Arial", 13), text_color="#00ff99").pack(pady=(0, 10))
        btn = ctk.CTkButton(frame, text="Afficher les graphiques", command=self.plot_variations, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)

    def plot_variations(self):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.plot(time, S, 'g-o', label='S(t)')
        plt.xlabel("Temps")
        plt.ylabel("S(t)")
        plt.title("Population Susceptible")
        plt.legend()
        plt.grid(True)
        plt.subplot(2, 2, 2)
        plt.plot(time, R, 'b-o', label='R(t)')
        plt.xlabel("Temps")
        plt.ylabel("R(t)")
        plt.title("Population Rétablie (cumulée)")
        plt.legend()
        plt.grid(True)
        plt.subplot(2, 2, 3)
        plt.plot(time_deriv, dS_dt, 'g--', label='dS/dt (numérique)')
        plt.xlabel("Temps (milieu de l'intervalle)")
        plt.ylabel("dS/dt")
        plt.title("Taux de variation de S(t)")
        plt.legend()
        plt.grid(True)
        plt.subplot(2, 2, 4)
        plt.plot(time_deriv, dR_dt, 'b--', label='dR/dt (numérique)')
        plt.xlabel("Temps (milieu de l'intervalle)")
        plt.ylabel("dR/dt")
        plt.title("Taux de variation de R(t)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        self.result_label.configure(text="Graphiques affichés.", text_color="#00ff99")

if __name__ == "__main__":
    app = DerivationSRApp()
    app.mainloop()