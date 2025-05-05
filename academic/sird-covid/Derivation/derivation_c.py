import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

N = 276_800_000
dt = 2
filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"
infected_df = pd.read_excel(filepath, sheet_name="Infected")
infected_df = infected_df.iloc[1:].reset_index(drop=True)
time = infected_df.iloc[:, 0].values
I = infected_df.iloc[:, 1].values / N

dI_dt = np.zeros(len(I))
for i in range(len(I) - dt):
    dI_dt[i] = (I[i + dt] - I[i]) / dt

min_idx = np.argmin(dI_dt)
tc = time[min_idx]
min_dIdt = dI_dt[min_idx]

class DerivationMinApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Recherche du minimum de dI/dt")
        self.geometry("500x300")
        self.resizable(False, False)
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Recherche du minimum de dI/dt", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        info = (
            f"Le minimum de dI/dt est {min_dIdt:.4e}\n"
            f"et se situe autour de t = {tc} (unité de temps)."
        )
        ctk.CTkLabel(frame, text=info, font=("Arial", 13), text_color="#00ff99").pack(pady=(0, 10))
        btn = ctk.CTkButton(frame, text="Afficher le graphique", command=self.plot_min, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)

    def plot_min(self):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        plt.plot(time, I, label='I(t)', color='red')
        plt.xlabel('Temps')
        plt.ylabel("Nombre d'infectés")
        plt.title("Évolution du nombre d'infectés")
        plt.legend()
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(time, dI_dt, label='dI/dt modèle', color='blue')
        plt.axvline(tc, color='k', linestyle='--', label=f"Min dI/dt à t = {tc}")
        plt.xlabel('Temps')
        plt.ylabel("dI/dt")
        plt.title("Dérivée théorique de I(t)")
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()
        self.result_label.configure(text="Graphique affiché.", text_color="#00ff99")

if __name__ == "__main__":
    app = DerivationMinApp()
    app.mainloop()