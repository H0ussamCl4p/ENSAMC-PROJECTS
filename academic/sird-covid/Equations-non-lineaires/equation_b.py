import customtkinter as ctk
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


S_c = (a + b) / r
P_c = 1 - S_c

S_interp = interp1d(time, S, kind='linear', fill_value='extrapolate')
I_interp = interp1d(time, I, kind='linear', fill_value='extrapolate')
R_interp = interp1d(time, R, kind='linear', fill_value='extrapolate')
D_interp = interp1d(time, D, kind='linear', fill_value='extrapolate')

def equation_immunite(t):
    return S_interp(t) - S_c

def immunite_atteinte(t):
    return 1 - S_interp(t)

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

def intervalle_immunite():
    return (1, 107)

class ImmuniteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Seuil d'immunité collective")
        self.geometry("700x500")
        self.resizable(False, False)
        self.a_intervalle, self.b_intervalle = intervalle_immunite()
        self.t_guess = (self.a_intervalle + self.b_intervalle) / 2
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Recherche du seuil d'immunité collective", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        info = (
            f"Seuil critique de susceptibles S_c = {S_c:.6f}\n"
            f"Seuil d'immunité collective P_c = {P_c:.6f} ({P_c*100:.2f}%)\n"
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
            t_newton, iter_newton, _ = Newton(equation_immunite, t_guess)
            t_secante, iter_secante, _ = secante(equation_immunite, t_guess - 1, t_guess)
            self.result_label.configure(
                text=(
                    f"Newton : t = {t_newton:.4f} ({iter_newton} itérations)\n"
                    f"Sécante : t = {t_secante:.4f} ({iter_secante} itérations)"
                ),
                text_color="#00ff99"
            )
        except Exception as e:
            self.result_label.configure(text=f"Erreur : {e}", text_color="#ff3333")

if __name__ == "__main__":
    app = ImmuniteApp()
    app.mainloop()