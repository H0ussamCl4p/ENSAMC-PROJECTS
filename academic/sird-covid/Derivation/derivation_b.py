import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"
I_df = pd.read_excel(filepath, sheet_name="Infected")
R_df = pd.read_excel(filepath, sheet_name="Recovered")
D_df = pd.read_excel(filepath, sheet_name="Death")


a = 0.4
b = 0.0005 
dt = 2      
N = 265185520

dates = I_df.iloc[:, 0]
I = I_df.iloc[:, 1] / N  

dI_dt = np.zeros(len(I))
for i in range(len(I) - dt):
    dI_dt[i] = (I[i + dt] - I[i]) / dt

rc = np.zeros(len(I))
for i in range(len(I)):
    if I[i] > 0 and i < len(I) - dt:
        rc[i] = (1 / I[i]) * dI_dt[i]

results_df = pd.DataFrame({
    'Date': dates,
    'Infected': I,
    'dI/dt': dI_dt,
    'rc': rc
})

class GrowthRateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Taux de croissance rc de l'épidémie")
        self.geometry("600x300")
        self.resizable(False, False)
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Taux de croissance rc \npour les premières \nsemaines de l'épidémie", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        btn = ctk.CTkButton(frame, text="Afficher le graphique", command=self.plot_rc, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)

    def plot_rc(self):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        plt.plot(dates, I, 'b-', label="Nombre d'infectés")
        plt.title("Évolution du nombre d'infectés")
        plt.ylabel("Nombre de cas")
        plt.grid(True)
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(dates, rc, 'r-', label="Taux de croissance rc")
        plt.title("Évolution du taux de croissance rc")
        plt.xlabel("Date")
        plt.ylabel("rc")
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.savefig('taux_croissance_analyse.png')
        plt.show()
        self.result_label.configure(text="Graphique affiché et résultats exportés.", text_color="#00ff99")
        results_df.to_excel("resultats_taux_croissance.xlsx", index=False)

if __name__ == "__main__":
    app = GrowthRateApp()
    app.mainloop()