import customtkinter as ctk
import numpy as np
import pandas as pd
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

S_theo = (a + b) / r

S_interp = interp1d(time, S, kind='linear', fill_value='extrapolate')
I_interp = interp1d(time, I, kind='linear', fill_value='extrapolate')

def equation_pic_S(t):
    return S_interp(t) - S_theo

def dIdt(t):
    return r * S_interp(t) * I_interp(t) - (a + b) * I_interp(t)

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

def g(t, alpha=0.1):
    return t + alpha * (S_theo - S_interp(t))

def point_fixe(g, x0, epsilon=1e-6, iter=90):
    x = x0
    compt = 0
    iterations = []
    while compt < iter:
        x1 = g(x)
        iterations.append((compt, x, x1))
        if abs(x1 - x) < epsilon:
            return x1, compt + 1, iterations
        x = x1
        compt += 1
    return x, compt, iterations

def secante(f, x0, x1, tol=1e-6, iter=100):
    compt = 0
    iterations = []
    while compt < iter:
        fx0 = f(x0)
        fx1 = f(x1)
        iterations.append((compt, x1, fx1))
        if abs(fx1) < tol:
            return x1, compt + 1, iterations
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
    return x1, compt, iterations

def intervalles_pic():
    intervalles = []
    intervalles.append((0, 107))
    return intervalles

class EquationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Recherche du pic épidémique")
        self.geometry("700x500")
        self.resizable(False, False)

        self.t_max_approx = time[np.argmax(I)]
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Recherche du pic épidémique", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        self.input_t = ctk.CTkEntry(frame, placeholder_text=f"Valeur initiale (t) [ex: {self.t_max_approx:.2f}]")
        self.input_t.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)
        btn = ctk.CTkButton(frame, text="Calculer", command=self.on_calculate, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)

    def on_calculate(self):
        try:
            t_guess = float(self.input_t.get())
            t_newton, iter_newton, _ = Newton(equation_pic_S, t_guess)
            t_point_fixe, iter_point_fixe, _ = point_fixe(g, t_guess)
            t_secante, iter_secante, _ = secante(equation_pic_S, t_guess - 1, t_guess)
            self.result_label.configure(
                text=(
                    f"Newton : t = {t_newton:.4f} ({iter_newton} itérations)\n"
                    f"Point fixe : t = {t_point_fixe:.4f} ({iter_point_fixe} itérations)\n"
                    f"Sécante : t = {t_secante:.4f} ({iter_secante} itérations)"
                ),
                text_color="#00ff99"
            )
        except Exception as e:
            self.result_label.configure(text=f"Erreur : {e}", text_color="#ff3333")

if __name__ == "__main__":
    app = EquationApp()
    app.mainloop()