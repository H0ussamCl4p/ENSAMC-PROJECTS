import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

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

time = infected_df.iloc[:, 0].values 
I = infected_df.iloc[:, 1].values / N  
R = recovered_df.iloc[:, 1].values / N
D = death_df.iloc[:, 1].values / N     
S = susceptible_df.iloc[:, 1].values / N  


I_interp = interp1d(time, I, kind='linear', fill_value='extrapolate')

Imax = 0.00019  
print(f"Valeur critique Imax définie à : {Imax:.6f}")

def equation(t):
    return I_interp(t) - Imax

def Newton(f, x0, epsilon=1e-6, nb_iter=150):
    x = x0
    compt = 0
    iterations = []
    def df(x, h=2):
        return (f(x + h) - f(x)) / h
    fx = f(x)
    iterations.append((compt, x, fx))
    dfx = df(x)
    delta_x = fx / dfx
    max_step = 10.0
    if abs(delta_x) > max_step:
        delta_x = max_step * (delta_x / abs(delta_x))
    x1 = x - delta_x
    while abs(x1 - x) > epsilon and compt < nb_iter:
        x = x1
        fx = f(x)
        iterations.append((compt, x, fx))
        dfx = df(x)
        delta_x = fx / dfx
        if abs(delta_x) > max_step:
            delta_x = max_step * (delta_x / abs(delta_x))
        x1 = x - delta_x
        compt += 1
    x = x1
    return x, compt, iterations

def secante(f, x0, x1, tol=1e-6, iter=100):
    compt = 0
    iterations = []
    while compt < iter:
        fx0 = f(x0)
        fx1 = f(x1)
        iterations.append((compt, x1, fx1))
        if abs(fx1) < tol:
            return x1, compt+1, iterations
        if abs(fx1 - fx0) < 1e-10:
            x_new = x1 + 0.01
        else:
            x_new = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
        max_step = 10.0
        if abs(x_new - x1) > max_step:
            x_new = x1 + max_step * ((x_new - x1) / abs(x_new - x1))
        if x_new < 0:
            x_new = 0.1
        x0, x1 = x1, x_new
        compt += 1
    return x1, compt , iterations

def intervalle_critique():
    return (1, 107)

class TempsCritiqueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Temps critique d'intervention sanitaire")
        self.geometry("700x500")
        self.resizable(False, False)
        self.a_intervalle, self.b_intervalle = intervalle_critique()
        self.t_guess = (self.a_intervalle + self.b_intervalle) / 2
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Détermination du temps critique pour une intervention sanitaire", font=("Arial", 16, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        info = (
            f"Valeur critique Imax = {Imax:.6f}\n"
            f"Intervalle : [{self.a_intervalle:.2f}, {self.b_intervalle:.2f}]"
        )
        ctk.CTkLabel(frame, text=info, font=("Arial", 13), text_color="#00ff99").pack(pady=(0, 10))
        self.input_t = ctk.CTkEntry(frame, placeholder_text=f"Valeur initiale (t) [ex: {self.t_guess:.2f}]")
        self.input_t.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)
        btn = ctk.CTkButton(frame, text="Calculer", command=self.on_calculate, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)

    def on_calculate(self):
        try:
            t_guess = float(self.input_t.get())
            resultats = []
            t_newton, iter_newton, _ = Newton(equation, t_guess)
            t_secante, iter_secante, _ = secante(equation, t_guess-1, t_guess)
            resultats.append(("Newton", t_newton, I_interp(t_newton)))
            resultats.append(("Sécante", t_secante, I_interp(t_secante)))
            
            text = (
                f"Newton : t = {t_newton:.4f} ({iter_newton} itérations)\n"
                f"Sécante : t = {t_secante:.4f} ({iter_secante} itérations)\n"
                f"Valeur moyenne : t = {np.mean([t_newton, t_secante]):.4f}"
            )
            self.result_label.configure(text=text, text_color="#00ff99")
            
            plt.figure(figsize=(12, 8))
            plt.plot(time, I, 'r-', label='Infectés (I)')
            plt.axhline(y=Imax, color='g', linestyle='--', label=f'Seuil critique Imax={Imax:.4f}')
            for methode, t_crit, _ in resultats:
                plt.scatter([t_crit], [Imax], marker='o', s=100, label=f'Temps critique ({methode}): t={t_crit:.2f}')
            plt.grid(True)
            plt.legend()
            plt.xlabel('Temps')
            plt.ylabel("Proportion d'infectés (I)")
            plt.title("Détermination du temps critique pour une intervention sanitaire")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            self.result_label.configure(text=f"Erreur : {e}", text_color="#ff3333")

if __name__ == "__main__":
    app = TempsCritiqueApp()
    app.mainloop()