import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


filepath = r"./BaseDedonnées/BD-Indonesie.xlsx"

df_I = pd.read_excel(filepath, sheet_name="Infected").iloc[1:].reset_index(drop=True)
df_R = pd.read_excel(filepath, sheet_name="Recovered").iloc[1:].reset_index(drop=True)
df_D = pd.read_excel(filepath, sheet_name="DeathC").iloc[1:].reset_index(drop=True)
df_S = pd.read_excel(filepath, sheet_name="Susceptible").iloc[1:].reset_index(drop=True)
N = 265185520
t = df_I.iloc[:, 0].values   
I_data = df_I.iloc[:, 1].values / N     
R_data = df_R.iloc[:, 1].values / N     
D_data = df_D.iloc[:, 1].values / N     
S_data = df_S.iloc[:, 1].values / N   

r = 0.6 
a = 0.4 
b = 0.005 

integrand_infectes = r * S_data * I_data 
integrand_guerisons = a * I_data          

def methode_rectangle_composite(t, integrand, t_cible, n=None):
    idx_cible = np.searchsorted(t, t_cible)
    if idx_cible >= len(t):
        idx_cible = len(t) - 1
    if n is not None:
        t_sub = np.linspace(0, t[idx_cible], n+1)
        integrand_sub = np.interp(t_sub, t[:idx_cible+1], integrand[:idx_cible+1])
        h = t_sub[1] - t_sub[0]
        somme = 0
        for i in range(n):
            somme += integrand_sub[i] * h
        return somme
    else:
        somme = 0
        for i in range(idx_cible):
            dt = t[i+1] - t[i]
            somme += integrand[i] * dt
        return somme

def methode_trapeze_composite(t, integrand, t_cible, n=None):
    idx_cible = np.searchsorted(t, t_cible)
    if idx_cible >= len(t):
        idx_cible = len(t) - 1
    if n is not None:
        t_sub = np.linspace(0, t[idx_cible], n+1)
        integrand_sub = np.interp(t_sub, t[:idx_cible+1], integrand[:idx_cible+1])
        h = t_sub[1] - t_sub[0]
        somme = 0
        for i in range(n):
            somme += (integrand_sub[i] + integrand_sub[i+1]) * h / 2
        return somme
    else:
        somme = 0
        for i in range(idx_cible):
            dt = t[i+1] - t[i]
            somme += (integrand[i] + integrand[i+1]) * dt / 2
        return somme

def methode_simpson_composite(t, integrand, t_cible, n=54):
    idx_cible = np.searchsorted(t, t_cible)
    if idx_cible >= len(t):
        idx_cible = len(t) - 1
    a = 1
    b = t[idx_cible]
    h = (b - a) / n
    f_a = np.interp(a, t[:idx_cible+1], integrand[:idx_cible+1])
    f_b = np.interp(b, t[:idx_cible+1], integrand[:idx_cible+1])
    sum_interior = 0
    for i in range(1, n):
        x_i = a + i * h
        f_x_i = np.interp(x_i, t[:idx_cible+1], integrand[:idx_cible+1])
        sum_interior += 2 * f_x_i
    sum_midpoints = 0
    for i in range(n):
        c_i = a + (i + 0.5) * h
        f_c_i = np.interp(c_i, t[:idx_cible+1], integrand[:idx_cible+1])
        sum_midpoints += 4 * f_c_i
    result = (h / 6) * (f_a + sum_interior + sum_midpoints + f_b)
    return result

def calculer_nombre_cumule_infectes(t_cible, n_subdivisions=[10, 20, 50, 100]):
    resultats = {
        "Méthode des rectangles": {},
        "Méthode des trapèzes": {},
        "Méthode de Simpson": {}
    }
    rectangle_normal = methode_rectangle_composite(t, integrand_infectes, t_cible) * N
    trapeze_normal = methode_trapeze_composite(t, integrand_infectes, t_cible) * N
    simpson_normal = methode_simpson_composite(t, integrand_infectes, t_cible) * N
    resultats["Méthode des rectangles"]["Points disponibles"] = rectangle_normal
    resultats["Méthode des trapèzes"]["Points disponibles"] = trapeze_normal
    resultats["Méthode de Simpson"]["Points disponibles"] = simpson_normal
    for n in n_subdivisions:
        rectangle = methode_rectangle_composite(t, integrand_infectes, t_cible, n) * N
        trapeze = methode_trapeze_composite(t, integrand_infectes, t_cible, n) * N
        simpson = methode_simpson_composite(t, integrand_infectes, t_cible, n) * N
        resultats["Méthode des rectangles"][f"{n} subdivisions"] = rectangle
        resultats["Méthode des trapèzes"][f"{n} subdivisions"] = trapeze
        resultats["Méthode de Simpson"][f"{n} subdivisions"] = simpson
    return resultats

def calculer_nombre_cumule_guerisons(t_cible, n_subdivisions=[10, 20, 50, 100]):
    resultats = {
        "Méthode des rectangles": {},
        "Méthode des trapèzes": {},
        "Méthode de Simpson": {}
    }
    rectangle_normal = methode_rectangle_composite(t, integrand_guerisons, t_cible) * N
    trapeze_normal = methode_trapeze_composite(t, integrand_guerisons, t_cible) * N
    simpson_normal = methode_simpson_composite(t, integrand_guerisons, t_cible) * N
    resultats["Méthode des rectangles"]["Points disponibles"] = rectangle_normal
    resultats["Méthode des trapèzes"]["Points disponibles"] = trapeze_normal
    resultats["Méthode de Simpson"]["Points disponibles"] = simpson_normal
    for n in n_subdivisions:
        rectangle = methode_rectangle_composite(t, integrand_guerisons, t_cible, n) * N
        trapeze = methode_trapeze_composite(t, integrand_guerisons, t_cible, n) * N
        simpson = methode_simpson_composite(t, integrand_guerisons, t_cible, n) * N
        resultats["Méthode des rectangles"][f"{n} subdivisions"] = rectangle
        resultats["Méthode des trapèzes"][f"{n} subdivisions"] = trapeze
        resultats["Méthode de Simpson"][f"{n} subdivisions"] = simpson
    return resultats

class ScrollableWindow(ctk.CTkToplevel):
    def __init__(self, fig, title="Graphique"):
        super().__init__()
        self.title(title)
        self.geometry("1000x700")

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = ctk.CTkCanvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = ctk.CTkFrame(canvas)
        scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_configure)

        fig_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
        fig_canvas.draw()
        fig_canvas.get_tk_widget().pack(fill="both", expand=True)

        def resize_canvas(event):
            canvas.itemconfig(scrollable_frame_id, width=event.width)
        canvas.bind("<Configure>", resize_canvas)

class IntegrationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Comparaison des Méthodes d'Intégration - SIRD")
        self.geometry("900x800")
        self.resizable(True, True)
        self.fig = None
        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text="Comparaison des Méthodes d'Intégration Numérique (SIRD)", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))

        self.input_x = ctk.CTkEntry(frame, placeholder_text="Entrez le jour à approximer (ex: 10)")
        self.input_x.pack(pady=10)

        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)

        ctk.CTkButton(frame, text="Calculer et tracer (Infectés)", command=self.on_calculate_infectes, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222").pack(pady=5)
        ctk.CTkButton(frame, text="Calculer et tracer (Guérisons)", command=self.on_calculate_guerisons, fg_color="#457B9D", text_color="#FFFFFF", hover_color="#222").pack(pady=5)
        self.save_btn = ctk.CTkButton(frame, text="Télécharger le graphique", command=self.save_plot, fg_color="#2A9D8F", text_color="#fff", hover_color="#222")
        self.save_btn.pack(pady=5)
        self.save_btn.configure(state="disabled")

    def on_calculate_infectes(self):
        try:
            user_input = self.input_x.get().strip()
            if not user_input:
                messagebox.showerror("Erreur", "Veuillez entrer un jour.")
                return
            jour = float(user_input)
            if jour < 0 or jour > max(t):
                messagebox.showerror("Erreur", f"Le jour doit être compris entre 0 et {max(t):.1f}")
                return
            resultats = calculer_nombre_cumule_infectes(jour)
            txt = f"Nombre cumulé d'infectés au jour {jour:.1f} :\n"
            for methode, valeurs in resultats.items():
                txt += f"{methode} :\n"
                for subdivision, valeur in valeurs.items():
                    txt += f"   {subdivision:<18}: {valeur:.0f}\n"
            self.result_label.configure(text=txt, text_color="#00ff99")

            # Graphe comparaison méthodes infectés
            jours = t
            cumul_rectangle = np.zeros_like(jours)
            cumul_trapeze = np.zeros_like(jours)
            cumul_simpson = np.zeros_like(jours)
            cumul_rectangle_50 = np.zeros_like(jours)
            cumul_trapeze_50 = np.zeros_like(jours)
            cumul_simpson_50 = np.zeros_like(jours)
            for i, j in enumerate(jours):
                cumul_rectangle[i] = methode_rectangle_composite(t, integrand_infectes, j) * N
                cumul_trapeze[i] = methode_trapeze_composite(t, integrand_infectes, j) * N
                cumul_simpson[i] = methode_simpson_composite(t, integrand_infectes, j) * N
                cumul_rectangle_50[i] = methode_rectangle_composite(t, integrand_infectes, j, 50) * N
                cumul_trapeze_50[i] = methode_trapeze_composite(t, integrand_infectes, j, 50) * N
                cumul_simpson_50[i] = methode_simpson_composite(t, integrand_infectes, j, 50) * N

            self.fig, axs = plt.subplots(2, 1, figsize=(12, 8), facecolor="white")
            axs[0].plot(jours, cumul_rectangle, 'r-', label='Rectangles')
            axs[0].plot(jours, cumul_trapeze, 'g-', label='Trapèzes')
            axs[0].plot(jours, cumul_simpson, 'b-', label='Simpson')
            axs[0].set_xlabel('Jour', color="#222")
            axs[0].set_ylabel("Nombre cumulé d'infectés", color="#222")
            axs[0].set_title("Comparaison des méthodes d'intégration (points disponibles)", color="#222")
            axs[0].legend()
            axs[0].grid(True)
            axs[0].set_facecolor("white")
            axs[0].tick_params(colors="#222")

            axs[1].plot(jours, cumul_rectangle_50, 'r-', label='Rectangles (50 subdiv.)')
            axs[1].plot(jours, cumul_trapeze_50, 'g-', label='Trapèzes (50 subdiv.)')
            axs[1].plot(jours, cumul_simpson_50, 'b-', label='Simpson (50 subdiv.)')
            axs[1].set_xlabel('Jour', color="#222")
            axs[1].set_ylabel("Nombre cumulé d'infectés", color="#222")
            axs[1].set_title("Comparaison des méthodes d'intégration (50 subdivisions)", color="#222")
            axs[1].legend()
            axs[1].grid(True)
            axs[1].set_facecolor("white")
            axs[1].tick_params(colors="#222")

            self.fig.tight_layout()
            ScrollableWindow(self.fig, title="Comparaison méthodes - Infectés")
            self.save_btn.configure(state="normal")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.save_btn.configure(state="disabled")

    def on_calculate_guerisons(self):
        try:
            user_input = self.input_x.get().strip()
            if not user_input:
                messagebox.showerror("Erreur", "Veuillez entrer un jour.")
                return
            jour = float(user_input)
            if jour < 0 or jour > max(t):
                messagebox.showerror("Erreur", f"Le jour doit être compris entre 0 et {max(t):.1f}")
                return
            resultats = calculer_nombre_cumule_guerisons(jour)
            txt = f"Nombre cumulé de guérisons au jour {jour:.1f} :\n"
            for methode, valeurs in resultats.items():
                txt += f"{methode} :\n"
                for subdivision, valeur in valeurs.items():
                    txt += f"   {subdivision:<18}: {valeur:.0f}\n"
            self.result_label.configure(text=txt, text_color="#00ff99")

            # Graphe comparaison méthodes guérisons
            jours = t
            cumul_rectangle = np.zeros_like(jours)
            cumul_trapeze = np.zeros_like(jours)
            cumul_simpson = np.zeros_like(jours)
            cumul_rectangle_50 = np.zeros_like(jours)
            cumul_trapeze_50 = np.zeros_like(jours)
            cumul_simpson_50 = np.zeros_like(jours)
            for i, j in enumerate(jours):
                cumul_rectangle[i] = methode_rectangle_composite(t, integrand_guerisons, j) * N
                cumul_trapeze[i] = methode_trapeze_composite(t, integrand_guerisons, j) * N
                cumul_simpson[i] = methode_simpson_composite(t, integrand_guerisons, j) * N
                cumul_rectangle_50[i] = methode_rectangle_composite(t, integrand_guerisons, j, 50) * N
                cumul_trapeze_50[i] = methode_trapeze_composite(t, integrand_guerisons, j, 50) * N
                cumul_simpson_50[i] = methode_simpson_composite(t, integrand_guerisons, j, 50) * N

            self.fig, axs = plt.subplots(2, 1, figsize=(12, 8), facecolor="white")
            axs[0].plot(jours, cumul_rectangle, 'r-', label='Rectangles')
            axs[0].plot(jours, cumul_trapeze, 'g-', label='Trapèzes')
            axs[0].plot(jours, cumul_simpson, 'b-', label='Simpson')
            axs[0].set_xlabel('Jour', color="#222")
            axs[0].set_ylabel("Nombre cumulé de guérisons", color="#222")
            axs[0].set_title("Comparaison des méthodes d'intégration (points disponibles)", color="#222")
            axs[0].legend()
            axs[0].grid(True)
            axs[0].set_facecolor("white")
            axs[0].tick_params(colors="#222")

            axs[1].plot(jours, cumul_rectangle_50, 'r-', label='Rectangles (50 subdiv.)')
            axs[1].plot(jours, cumul_trapeze_50, 'g-', label='Trapèzes (50 subdiv.)')
            axs[1].plot(jours, cumul_simpson_50, 'b-', label='Simpson (50 subdiv.)')
            axs[1].set_xlabel('Jour', color="#222")
            axs[1].set_ylabel("Nombre cumulé de guérisons", color="#222")
            axs[1].set_title("Comparaison des méthodes d'intégration (50 subdivisions)", color="#222")
            axs[1].legend()
            axs[1].grid(True)
            axs[1].set_facecolor("white")
            axs[1].tick_params(colors="#222")

            self.fig.tight_layout()
            ScrollableWindow(self.fig, title="Comparaison méthodes - Guérisons")
            self.save_btn.configure(state="normal")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.save_btn.configure(state="disabled")

    def save_plot(self):
        if self.fig is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")])
            if file_path:
                self.fig.savefig(file_path)
                messagebox.showinfo("Succès", "Graphique enregistré avec succès !")

if __name__ == "__main__":
    app = IntegrationApp()
    app.mainloop()