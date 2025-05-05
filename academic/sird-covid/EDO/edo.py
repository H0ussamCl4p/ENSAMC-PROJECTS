import customtkinter as ctk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"
infected_df = pd.read_excel(filepath, sheet_name="Infected")
recovered_df = pd.read_excel(filepath, sheet_name="RecoveredC")
death_df = pd.read_excel(filepath, sheet_name="DeathC")
susceptible_df = pd.read_excel(filepath, sheet_name="Susceptible")

N = 265185520

dates = infected_df.iloc[:, 0].values
infected_real = infected_df.iloc[:, 1].values / N
recovered_real = recovered_df.iloc[:, 1].values / N
death_real = death_df.iloc[:, 1].values / N
susceptible_real = susceptible_df.iloc[:, 1].values / N

a = 0.4211
b = 0.0051
r = 0.6007

t_start = 0
n = len(dates)
h = 1

T = np.arange(t_start, t_start + n*h, h)
if len(T) > n:
    T = T[:n]

def euler_explicit(S0, I0, R0, D0, r, a, b, h, n):
    S = [S0]
    I = [I0]
    R = [R0]
    D = [D0]
    for i in range(n-1):
        dSdt = -r * S[i] * I[i]
        dIdt = r * S[i] * I[i] - (a + b) * I[i]
        dRdt = a * I[i]
        dDdt = b * I[i]
        S.append(S[i] + h * dSdt)
        I.append(I[i] + h * dIdt)
        R.append(R[i] + h * dRdt)
        D.append(D[i] + h * dDdt)
    return S, I, R, D

def euler_implicit(S0, I0, R0, D0, r, a, b, h, n):
    S = [S0]
    I = [I0]
    R = [R0]
    D = [D0]
    for i in range(n-1):
        S_new = S[i] / (1 + h * r * I[i])
        I_new = I[i] + h * (r * S_new * I[i] - (a + b) * I[i])
        R_new = R[i] + h * a * I[i]
        D_new = D[i] + h * b * I[i]
        S.append(S_new)
        I.append(I_new)
        R.append(R_new)
        D.append(D_new)
    return S, I, R, D

def runge_kutta4(S0, I0, R0, D0, r, a, b, h, n):
    S = [S0]
    I = [I0]
    R = [R0]
    D = [D0]
    for i in range(n-1):
        k1_S = -r * S[i] * I[i]
        k1_I = r * S[i] * I[i] - (a + b) * I[i]
        k1_R = a * I[i]
        k1_D = b * I[i]
        k2_S = -r * (S[i] + h/2 * k1_S) * (I[i] + h/2 * k1_I)
        k2_I = r * (S[i] + h/2 * k1_S) * (I[i] + h/2 * k1_I) - (a + b) * (I[i] + h/2 * k1_I)
        k2_R = a * (I[i] + h/2 * k1_I)
        k2_D = b * (I[i] + h/2 * k1_I)
        k3_S = -r * (S[i] + h/2 * k2_S) * (I[i] + h/2 * k2_I)
        k3_I = r * (S[i] + h/2 * k2_S) * (I[i] + h/2 * k2_I) - (a + b) * (I[i] + h/2 * k2_I)
        k3_R = a * (I[i] + h/2 * k2_I)
        k3_D = b * (I[i] + h/2 * k2_I)
        k4_S = -r * (S[i] + h * k3_S) * (I[i] + h * k3_I)
        k4_I = r * (S[i] + h * k3_S) * (I[i] + h * k3_I) - (a + b) * (I[i] + h * k3_I)
        k4_R = a * (I[i] + h * k3_I)
        k4_D = b * (I[i] + h * k3_I)
        S.append(S[i] + h/6 * (k1_S + 2*k2_S + 2*k3_S + k4_S))
        I.append(I[i] + h/6 * (k1_I + 2*k2_I + 2*k3_I + k4_I))
        R.append(R[i] + h/6 * (k1_R + 2*k2_R + 2*k3_R + k4_R))
        D.append(D[i] + h/6 * (k1_D + 2*k2_D + 2*k3_D + k4_D))
    return S, I, R, D

S0 = susceptible_real[0]
I0 = infected_real[0]
R0 = recovered_real[0]
D0 = death_real[0]
S_euler, I_euler, R_euler, D_euler = euler_explicit(S0, I0, R0, D0, r, a, b, h, n)
S_implicit, I_implicit, R_implicit, D_implicit = euler_implicit(S0, I0, R0, D0, r, a, b, h, n)
S_rk, I_rk, R_rk, D_rk = runge_kutta4(S0, I0, R0, D0, r, a, b, h, n)

S_euler_data = [susceptible_real[0]]
I_euler_data = [infected_real[0]]
R_euler_data = [recovered_real[0]]
D_euler_data = [death_real[0]]
for i in range(n-1):
    dSdt = -r * susceptible_real[i] * infected_real[i]
    dIdt = r * susceptible_real[i] * infected_real[i] - (a + b) * infected_real[i]
    dRdt = a * infected_real[i]
    dDdt = b * infected_real[i]
    S_euler_data.append(susceptible_real[i] + h * dSdt)
    I_euler_data.append(infected_real[i] + h * dIdt)
    R_euler_data.append(recovered_real[i] + h * dRdt)
    D_euler_data.append(death_real[i] + h * dDdt)

S_implicit_data = [susceptible_real[0]]
I_implicit_data = [infected_real[0]]
R_implicit_data = [recovered_real[0]]
D_implicit_data = [death_real[0]]
for i in range(n-1):
    S_new = susceptible_real[i] / (1 + h * r * infected_real[i])
    I_new = infected_real[i] + h * (r * S_new * infected_real[i] - (a + b) * infected_real[i])
    R_new = recovered_real[i] + h * a * infected_real[i]
    D_new = death_real[i] + h * b * infected_real[i]
    S_implicit_data.append(S_new)
    I_implicit_data.append(I_new)
    R_implicit_data.append(R_new)
    D_implicit_data.append(D_new)

S_rk_data = [susceptible_real[0]]
I_rk_data = [infected_real[0]]
R_rk_data = [recovered_real[0]]
D_rk_data = [death_real[0]]
for i in range(n-1):
    k1_S = -r * susceptible_real[i] * infected_real[i]
    k1_I = r * susceptible_real[i] * infected_real[i] - (a + b) * infected_real[i]
    k1_R = a * infected_real[i]
    k1_D = b * infected_real[i]
    S_mid = susceptible_real[i] + h/2 * k1_S
    I_mid = infected_real[i] + h/2 * k1_I
    k2_S = -r * S_mid * I_mid
    k2_I = r * S_mid * I_mid - (a + b) * I_mid
    k2_R = a * I_mid
    k2_D = b * I_mid
    S_mid = susceptible_real[i] + h/2 * k2_S
    I_mid = infected_real[i] + h/2 * k2_I
    k3_S = -r * S_mid * I_mid
    k3_I = r * S_mid * I_mid - (a + b) * I_mid
    k3_R = a * I_mid
    k3_D = b * I_mid
    S_end = susceptible_real[i] + h * k3_S
    I_end = infected_real[i] + h * k3_I
    k4_S = -r * S_end * I_end
    k4_I = r * S_end * I_end - (a + b) * I_end
    k4_R = a * I_end
    k4_D = b * I_end
    S_rk_data.append(susceptible_real[i] + h/6 * (k1_S + 2*k2_S + 2*k3_S + k4_S))
    I_rk_data.append(infected_real[i] + h/6 * (k1_I + 2*k2_I + 2*k3_I + k4_I))
    R_rk_data.append(recovered_real[i] + h/6 * (k1_R + 2*k2_R + 2*k3_R + k4_R))
    D_rk_data.append(death_real[i] + h/6 * (k1_D + 2*k2_D + 2*k3_D + k4_D))

class EDOApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulation SIRD - Méthodes Numériques")
        self.geometry("700x400")
        self.resizable(False, False)
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Simulation SIRD : Choisissez la méthode de prédiction", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        btn1 = ctk.CTkButton(frame, text="Prédiction à partir des conditions initiales", command=self.show_choix_approche1, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn1.pack(pady=10)
        btn2 = ctk.CTkButton(frame, text="Prédiction pas à pas avec données réelles", command=self.show_choix_approche2, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn2.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)
        self.btns_frame = None

    def show_choix_approche1(self):
        if self.btns_frame:
            self.btns_frame.destroy()
        self.btns_frame = ctk.CTkFrame(self)
        self.btns_frame.pack(pady=10)
        ctk.CTkButton(self.btns_frame, text="Susceptibles", command=self.plot_susceptibles_1, fg_color="#ffba08", text_color="#fff").pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="Infectés", command=self.plot_infectes_1, fg_color="#ffba08", text_color="#fff").pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="Rétablis", command=self.plot_retablis_1, fg_color="#ffba08", text_color="#fff").pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="Décès", command=self.plot_deces_1, fg_color="#ffba08", text_color="#fff").pack(side="left", padx=5)

    def show_choix_approche2(self):
        if self.btns_frame:
            self.btns_frame.destroy()
        self.btns_frame = ctk.CTkFrame(self)
        self.btns_frame.pack(pady=10)
        ctk.CTkButton(self.btns_frame, text="Susceptibles", command=self.plot_susceptibles_2, fg_color="#e85d04", text_color="#fff").pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="Infectés", command=self.plot_infectes_2, fg_color="#e85d04", text_color="#fff").pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="Rétablis", command=self.plot_retablis_2, fg_color="#e85d04", text_color="#fff").pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="Décès", command=self.plot_deces_2, fg_color="#e85d04", text_color="#fff").pack(side="left", padx=5)

 
    def plot_susceptibles_1(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, susceptible_real, 'ko-', label='Données réelles (S)')
        plt.plot(T, S_euler, 'b--', label='Euler explicite (S)')
        plt.plot(T, S_implicit, 'g-.', label='Euler implicite (S)')
        plt.plot(T, S_rk, 'r-', label='Runge-Kutta (S)')
        plt.title('Susceptibles - Prédiction à partir des conditions initiales')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_infectes_1(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, infected_real, 'ko-', label='Données réelles (I)')
        plt.plot(T, I_euler, 'b--', label='Euler explicite (I)')
        plt.plot(T, I_implicit, 'g-.', label='Euler implicite (I)')
        plt.plot(T, I_rk, 'r-', label='Runge-Kutta (I)')
        plt.title('Infectés - Prédiction à partir des conditions initiales')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_retablis_1(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, recovered_real, 'ko-', label='Données réelles (R)')
        plt.plot(T, R_euler, 'b--', label='Euler explicite (R)')
        plt.plot(T, R_implicit, 'g-.', label='Euler implicite (R)')
        plt.plot(T, R_rk, 'r-', label='Runge-Kutta (R)')
        plt.title('Rétablis - Prédiction à partir des conditions initiales')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_deces_1(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, death_real, 'ko-', label='Données réelles (D)')
        plt.plot(T, D_euler, 'b--', label='Euler explicite (D)')
        plt.plot(T, D_implicit, 'g-.', label='Euler implicite (D)')
        plt.plot(T, D_rk, 'r-', label='Runge-Kutta (D)')
        plt.title('Décès - Prédiction à partir des conditions initiales')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_susceptibles_2(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, susceptible_real, 'ko-', label='Données réelles (S)')
        plt.plot(T, S_euler_data, 'b--', label='Euler explicite (S)')
        plt.plot(T, S_implicit_data, 'g-.', label='Euler implicite (S)')
        plt.plot(T, S_rk_data, 'r-', label='Runge-Kutta (S)')
        plt.title('Susceptibles - Prédiction pas à pas avec données réelles')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_infectes_2(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, infected_real, 'ko-', label='Données réelles (I)')
        plt.plot(T, I_euler_data, 'b--', label='Euler explicite (I)')
        plt.plot(T, I_implicit_data, 'g-.', label='Euler implicite (I)')
        plt.plot(T, I_rk_data, 'r-', label='Runge-Kutta (I)')
        plt.title('Infectés - Prédiction pas à pas avec données réelles')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_retablis_2(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, recovered_real, 'ko-', label='Données réelles (R)')
        plt.plot(T, R_euler_data, 'b--', label='Euler explicite (R)')
        plt.plot(T, R_implicit_data, 'g-.', label='Euler implicite (R)')
        plt.plot(T, R_rk_data, 'r-', label='Runge-Kutta (R)')
        plt.title('Rétablis - Prédiction pas à pas avec données réelles')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_deces_2(self):
        plt.figure(figsize=(10, 5))
        plt.plot(T, death_real, 'ko-', label='Données réelles (D)')
        plt.plot(T, D_euler_data, 'b--', label='Euler explicite (D)')
        plt.plot(T, D_implicit_data, 'g-.', label='Euler implicite (D)')
        plt.plot(T, D_rk_data, 'r-', label='Runge-Kutta (D)')
        plt.title('Décès - Prédiction pas à pas avec données réelles')
        plt.xlabel('Temps (jours)')
        plt.ylabel('Proportion de la population')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = EDOApp()
    app.mainloop()