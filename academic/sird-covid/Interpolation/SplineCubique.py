import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def spline_naturelle(x, y):
    """ Calcule les coefficients des splines cubiques naturelles """
    n = len(x) - 1
    h = np.diff(x)
    A = np.zeros((n - 1, n - 1))
    b = np.zeros(n - 1)
    for i in range(1, n):
        A[i - 1, i - 1] = 2 * (h[i - 1] + h[i])
        if i < n - 1:
            A[i - 1, i] = h[i]
            A[i, i - 1] = h[i]
        b[i - 1] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])
    M = np.zeros(n + 1)
    M[1:n] = np.linalg.solve(A, b)
    a = y[:-1]
    c = M[:-1] / 2
    d = (M[1:] - M[:-1]) / (6 * h)
    b = (y[1:] - y[:-1]) / h - h * (2 * M[:-1] + M[1:]) / 6
    return a, b, c, d, x

def eval_spline(a, b, c, d, x, x_eval):
    """ Évalue la spline cubique pour une valeur donnée """
    i = np.searchsorted(x, x_eval) - 1
    i = np.clip(i, 0, len(a) - 1)
    dx = x_eval - x[i]
    return a[i] + b[i] * dx + c[i] * dx**2 + d[i] * dx**3

def plot_spline(x, y, a, b, c, d, x_points, x_eval=None, y_eval=None):
    """Affiche la courbe de la spline cubique et les points donnés."""
    x_fine = np.linspace(min(x), max(x), 200)
    y_fine = np.array([eval_spline(a, b, c, d, x_points, xi) for xi in x_fine])
    plt.figure(figsize=(8, 5))
    plt.scatter(x, y, color='red', label="Points de données", marker='o')
    plt.plot(x_fine, y_fine, label="Spline cubique", color='blue')
    if x_eval is not None and y_eval is not None:
        plt.scatter(x_eval, y_eval, color='green', label=f"f({x_eval}) = {y_eval:.2f}", marker='x', s=100)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.title("Interpolation par Splines Cubiques Naturelles")
    plt.legend()
    plt.grid(True)
    plt.show()

class SplineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Spline Cubique Naturelle")
        self.geometry("600x400")
        self.resizable(False, False)
        # Chargement des données
        file_path = r"./BaseDedonnées/BD-Indonesie.xlsx"
        df = pd.read_excel(file_path, sheet_name="Infected")
        df.columns = df.columns.str.strip()
        self.x = df["Date"].values
        self.y = df["I"].values
        self.a, self.b, self.c, self.d, self.x_points = spline_naturelle(self.x, self.y)
        
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Approximation par Spline Cubique Naturelle", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        self.input_x = ctk.CTkEntry(frame, placeholder_text="Entrez la valeur de x")
        self.input_x.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)
        btn = ctk.CTkButton(frame, text="Calculer et tracer", command=self.on_calculate, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)

    def on_calculate(self):
        try:
            x_eval = float(self.input_x.get())
            y_eval = eval_spline(self.a, self.b, self.c, self.d, self.x_points, x_eval)
            self.result_label.configure(text=f"f({x_eval}) ≈ {y_eval:.4f}", text_color="#00ff99")
            plot_spline(self.x, self.y, self.a, self.b, self.c, self.d, self.x_points, x_eval, y_eval)
        except ValueError:
            self.result_label.configure(text="Entrée non valide pour x.", text_color="#ff3333")

if __name__ == "__main__":
    app = SplineApp()
    app.mainloop()