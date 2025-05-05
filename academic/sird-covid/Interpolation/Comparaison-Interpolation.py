import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def divided_diff(x, y):
    n = len(y)
    coef = np.zeros([n, n])
    coef[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            coef[i][j] = (coef[i + 1][j - 1] - coef[i][j - 1]) / (x[i + j] - x[i])
    return coef

def newton_poly(coef, x_data, x):
    n = len(x_data) - 1
    p = coef[0]
    for i in range(1, n + 1):
        prod = 1
        for j in range(i):
            prod *= (x - x_data[j])
        p += coef[i] * prod
    return p

def neville_interpolation(x, xi, yi):
    n = len(xi)
    Q = np.zeros((n, n))
    Q[:, 0] = yi
    for j in range(1, n):
        for i in range(n - j):
            denominator = (xi[i] - xi[i + j])
            if denominator == 0:
                return np.nan
            Q[i, j] = ((x - xi[i + j]) * Q[i, j - 1] - (x - xi[i]) * Q[i + 1, j - 1]) / denominator
    return Q[0, -1]

def lagrange_interpolation(x_values, y_values, x):
    n = len(x_values)
    P_x = 0
    for i in range(n):
        L_i = 1
        for j in range(n):
            if i != j:
                L_i *= (x - x_values[j]) / (x_values[i] - x_values[j])
        P_x += y_values[i] * L_i
    return P_x

class InterpolationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Comparaison des Méthodes d'Interpolation")
        self.geometry("600x500")
        self.resizable(False, False)
        # Chargement des données
        file_path = r"./BaseDedonnées/BD-Indonesie.xlsx"
        try:
            df = pd.read_excel(file_path, sheet_name='Infected')
            df.columns = df.columns.str.strip()
        except Exception as e:
            ctk.CTkMessagebox(title="Erreur", message=f"Erreur lors du chargement des données : {e}")
            self.destroy()
            return

        try:
            self.xi = df["Date"].values.astype(float)
            self.yi = df["I"].values.astype(float)
            sort_idx = np.argsort(self.xi)
            self.xi = self.xi[sort_idx]
            self.yi = self.yi[sort_idx]
        except Exception as e:
            ctk.CTkMessagebox(title="Erreur", message=f"Erreur lors du traitement des données : {e}")
            self.destroy()
            return

        self.x_fine = np.linspace(min(self.xi), max(self.xi), 200)
        self.cs = CubicSpline(self.xi, self.yi, bc_type='natural')
        self.y_spline = self.cs(self.x_fine)
        self.coefs = divided_diff(self.xi, self.yi)[0, :]
        self.y_newton = np.array([newton_poly(self.coefs, self.xi, x) for x in self.x_fine])
        self.y_neville = np.array([neville_interpolation(x, self.xi, self.yi) for x in self.x_fine])
        self.y_neville = np.clip(self.y_neville, np.min(self.yi), np.max(self.yi) * 1.2)

        self.colors = {
            'cubic_spline': '#E63946',
            'newton': '#457B9D',
            'neville': '#2A9D8F',
            'lagrange': '#9B5DE5',
            'data_points': '#F94144'
        }

        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Comparaison des Méthodes d'Interpolation", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        self.input_x = ctk.CTkEntry(frame, placeholder_text="Entrez la valeur de x à approximer")
        self.input_x.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)
        btn = ctk.CTkButton(frame, text="Calculer et tracer", command=self.on_calculate, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)

    def on_calculate(self):
        try:
            user_input = self.input_x.get().strip()
            if user_input.lower() == 'fin':
                self.destroy()
                return
            x_approx = float(user_input)
            lagrange_result = lagrange_interpolation(self.xi, self.yi, x_approx)
            newton_result = newton_poly(self.coefs, self.xi, x_approx)
            neville_result = neville_interpolation(x_approx, self.xi, self.yi)
            spline_result = self.cs(x_approx)

            self.result_label.configure(
                text=(
                    f"Lagrange: {lagrange_result:.4f}   |   "
                    f"Newton: {newton_result:.4f}   |   "
                    f"Neville: {neville_result:.4f}   |   "
                    f"Splines: {spline_result:.4f}"
                ),
                text_color="#00ff99"
            )

            plt.figure(figsize=(8, 6))
            plt.plot(self.x_fine, self.y_spline, color=self.colors['cubic_spline'], linewidth=2.5, label="Cubic Spline", alpha=0.9)
            plt.plot(self.x_fine, self.y_newton, color=self.colors['newton'], linewidth=2.5, label="Newton Interpolation", alpha=0.9)
            plt.plot(self.x_fine, self.y_neville, color=self.colors['neville'], linestyle='--', linewidth=2, label="Neville Interpolation", alpha=0.8)
            x_range = np.linspace(min(self.xi), max(self.xi), 100)
            y_range = [lagrange_interpolation(self.xi, self.yi, x) for x in x_range]
            plt.plot(x_range, y_range, color=self.colors['lagrange'], linestyle='-.', linewidth=2, label="Lagrange Polynomial", alpha=0.8)
            plt.scatter(self.xi, self.yi, color=self.colors['data_points'], s=60, zorder=5, edgecolor='black', linewidth=1, label="Original Data")
            plt.scatter([x_approx], [spline_result], color='gold', s=100, zorder=10, edgecolor='black', label=f"Approximation (x={x_approx:.2f}, y={spline_result:.2f})")
            plt.ylim(min(self.yi) * 0.95, max(self.yi) * 1.05 + 2000)
            plt.xlabel("T_data (Days)", fontsize=8, fontweight='bold')
            plt.ylabel("I_data (Infected)", fontsize=8, fontweight='bold')
            plt.yticks(np.arange(0, 101, 20) if np.max(self.yi) <= 100 else np.linspace(2000, 9000, 5))
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.title("Comparaison des méthodes d'interpolation", fontsize=10, fontweight='bold', pad=15)
            plt.legend(loc='upper left', fontsize=6, framealpha=0.9, edgecolor='gray')
            plt.grid(True, linestyle='--', alpha=0.4)
            plt.tight_layout()
            plt.show()
        except ValueError:
            self.result_label.configure(text="Erreur : Veuillez entrer un nombre valide ou 'fin'.", text_color="#ff3333")

if __name__ == "__main__":
    app = InterpolationApp()
    app.mainloop()