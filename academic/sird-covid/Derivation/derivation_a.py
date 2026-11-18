import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

a = 0.4
b = 0.005  
N = 265185520
dt = 2  

filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"
infected_df = pd.read_excel(filepath, sheet_name="Infected")
recovered_df = pd.read_excel(filepath, sheet_name="Recovered")
death_df = pd.read_excel(filepath, sheet_name="Death")

time = infected_df.iloc[:, 0].values
I = infected_df.iloc[:, 1].values / N
R = recovered_df.iloc[:, 1].values / N
D = death_df.iloc[:, 1].values / N
S = (N - I - R - D) / N

dI_dt = np.zeros_like(I, dtype=float)
for i in range(1, len(I) - 1):
    dI_dt[i] = (I[i + 1] - I[i - 1]) / dt
dI_dt[0] = (I[1] - I[0]) / dt
dI_dt[-1] = (I[-1] - I[-2]) / dt

r = np.zeros_like(I, dtype=float)
for i in range(len(I)):
    r[i] = (dI_dt[i] + (a + b) * I[i]) / (S[i] * I[i])

results = pd.DataFrame({
    'Time': time,
    'r': r
})

class DerivationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Évolution du taux de transmission (r)")
        self.geometry("500x300")
        self.resizable(False, False)
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Évolution du taux de transmission \n(r) au fil du temps", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        btn = ctk.CTkButton(frame, text="Afficher le graphique", command=self.plot_r, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)

    def plot_r(self):
        plt.figure(figsize=(10, 6))
        plt.plot(time, r, 'o-', markersize=3)
        plt.title('Évolution du taux de transmission (r) au fil du temps')
        plt.xlabel('Temps')
        plt.ylabel('r')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        self.result_label.configure(text="Graphique affiché et résultats exportés.", text_color="#00ff99")
        results.to_excel("resultats_taux_transmission.xlsx", index=False)

if __name__ == "__main__":
    app = DerivationApp()
    app.mainloop()