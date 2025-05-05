import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"
infected_df = pd.read_excel(filepath, sheet_name="Comparaison")
time = infected_df.iloc[:, 0].values   # Première colonne = temps
I_Bali = infected_df.iloc[:, 1].values  # Deuxième colonne = nombre d'infectés à Bali
I_Bengkulu = infected_df.iloc[:, 2].values  # Troisième colonne = nombre d'infectés à Bengkulu 

vitesse_Bali = np.zeros_like(I_Bali, dtype=float)
vitesse_Bengkulu = np.zeros_like(I_Bengkulu, dtype=float)
for i in range(1, len(time)):
    delta_t = 2
    vitesse_Bali[i] = (I_Bali[i] - I_Bali[i-1]) / delta_t
    vitesse_Bengkulu[i] = (I_Bengkulu[i] - I_Bengkulu[i-1]) / delta_t

resultats_df = pd.DataFrame({
    'Date': time,
    'I_Bali': I_Bali,
    'I_Bengkulu': I_Bengkulu,
    'Vitesse_Bali': vitesse_Bali,
    'Vitesse_Bengkulu': vitesse_Bengkulu
})

class VitessePropagationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Comparaison de la vitesse de propagation")
        self.geometry("700x350")
        self.resizable(False, False)
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Comparaison de la vitesse de propagation du virus \nentre Bali et Bengkulu", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        stats = (
            f"Vitesse moyenne à Bali: {np.mean(vitesse_Bali[1:]):.2f} cas/unité de temps\n"
            f"Vitesse moyenne à Bengkulu: {np.mean(vitesse_Bengkulu[1:]):.2f} cas/unité de temps\n"
            f"Vitesse maximale à Bali: {np.max(vitesse_Bali[1:]):.2f} cas/unité de temps\n"
            f"Vitesse maximale à Bengkulu: {np.max(vitesse_Bengkulu[1:]):.2f} cas/unité de temps"
        )
        ctk.CTkLabel(frame, text=stats, font=("Arial", 13), text_color="#00ff99").pack(pady=(0, 10))
        btn = ctk.CTkButton(frame, text="Afficher le graphique", command=self.plot_vitesse, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)

    def plot_vitesse(self):
        plt.figure(figsize=(14, 7))
        plt.plot(range(len(time)), vitesse_Bali, 'b-', linewidth=2, label='Vitesse de propagation à Bali')
        plt.plot(range(len(time)), vitesse_Bengkulu, 'r-', linewidth=2, label='Vitesse de propagation à Bengkulu')
        plt.scatter(range(len(time)), vitesse_Bali, color='blue', s=30, alpha=0.7)
        plt.scatter(range(len(time)), vitesse_Bengkulu, color='red', s=30, alpha=0.7)
        plt.xlabel('Index temporel', fontsize=12)
        plt.ylabel('Vitesse de propagation (nouveaux cas par unité de temps)', fontsize=12)
        plt.title('Comparaison de la vitesse de propagation du virus entre Bali et Bengkulu', fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
        self.result_label.configure(text="Graphique affiché.", text_color="#00ff99")

if __name__ == "__main__":
    app = VitessePropagationApp()
    app.mainloop()