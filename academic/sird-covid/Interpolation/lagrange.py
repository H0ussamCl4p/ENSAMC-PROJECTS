import customtkinter as ctk
import pandas as pd

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def lagrange(t, ti, Ii):
    n = len(ti)
    P = 0
    for i in range(n):
        P_temp = 1
        for j in range(n):
            if i != j:
                P_temp *= (t - ti[j]) / (ti[i] - ti[j])
        P += P_temp * Ii[i]
    return P

class LagrangeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Interpolation de Lagrange")
        self.geometry("600x400")
        self.resizable(False, False)

        file_path = r"./BaseDedonnées/BD-Indonesie.xlsx"
        df1 = pd.read_excel(file_path, sheet_name='Infected').rename(columns={'Date ': 'Day'})
        df2 = pd.read_excel(file_path, sheet_name='DeathC').rename(columns={'Date ': 'Day'})
        df3 = pd.read_excel(file_path, sheet_name='RecoveredC').rename(columns={'Date ': 'Day'})

        self.ti = df1["Day"].values.astype(float)
        self.Ii = df1["I"].values.astype(float)
        self.Di = df2["DC"].values.astype(float)
        self.Ri = df3["RC"].values.astype(float)

        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)
        label = ctk.CTkLabel(frame, text="Approximation par la méthode de Lagrange", font=("Arial", 18, "bold"), text_color="#fff")
        label.pack(pady=(10, 20))
        self.input_t = ctk.CTkEntry(frame, placeholder_text="Entrez la valeur du jour t")
        self.input_t.pack(pady=10)
        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14), text_color="#fff")
        self.result_label.pack(pady=10)
        btn = ctk.CTkButton(frame, text="Calculer", command=self.on_calculate, fg_color="#4CBB17", text_color="#FFFFFF", hover_color="#222")
        btn.pack(pady=10)

    def on_calculate(self):
        try:
            t = float(self.input_t.get())
            res_infectes = lagrange(t, self.ti, self.Ii)
            res_decedes = lagrange(t, self.ti, self.Di)
            res_retablis = lagrange(t, self.ti, self.Ri)
            self.result_label.configure(
                text=(
                    f"Infectés : {res_infectes:.2f}\n"
                    f"Décédés : {res_decedes:.2f}\n"
                    f"Rétablis : {res_retablis:.2f}"
                ),
                text_color="#00ff99"
            )
        except ValueError:
            self.result_label.configure(text="Entrée non valide pour t.", text_color="#ff3333")

if __name__ == "__main__":
    app = LagrangeApp()
    app.mainloop()