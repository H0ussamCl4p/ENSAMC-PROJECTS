import customtkinter as ctk
import pandas as pd
from scipy import integrate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def analyse_impact():
    df = pd.read_excel(r"./BaseDedonnées/BD-Indonesie.xlsx")
    df_riau = df[df["Province"] == "Riau"].sort_values("Date")
    df_riau["Date"] = pd.to_datetime(df_riau["Date"])
    date_range = pd.date_range(df_riau["Date"].min(), df_riau["Date"].max(), freq='D')
    df_riau = df_riau.set_index("Date").reindex(date_range).fillna(0).infer_objects(copy=False).reset_index()
    df_riau.rename(columns={"index": "Date"}, inplace=True)
    df_riau["Days"] = (df_riau["Date"] - df_riau["Date"].min()).dt.days
    df_riau["New Cases"] = df_riau["New Cases"].fillna(0).clip(lower=0)
    df_riau["I(t)"] = df_riau["New Cases"].rolling(window=7, center=True).mean().fillna(0)
    rupture_date = pd.to_datetime("2020-04-01")
    window_days = 60
    avant = df_riau[(df_riau["Date"] >= rupture_date) & 
                    (df_riau["Date"] < rupture_date + pd.Timedelta(days=window_days))]
    apres = df_riau[(df_riau["Date"] >= rupture_date - pd.Timedelta(days=window_days)) & 
                    (df_riau["Date"] < rupture_date)]

    result_txt = ""
    if len(avant) > 1 and len(apres) > 1:
        impact_sans = integrate.simpson(avant["I(t)"], x=avant["Days"])
        impact_avec = integrate.simpson(apres["I(t)"], x=apres["Days"])
        impact_total = abs(impact_sans - impact_avec)
        result_txt += f"Durée analysée : {window_days} jours avant/après le {rupture_date.date()}\n"
        result_txt += f"Cas cumulés sans mesures : {impact_sans:.0f} cas.jours\n"
        result_txt += f"Cas cumulés avec mesures : {impact_avec:.0f} cas.jours\n"
        result_txt += f"Impact estimé des mesures sanitaires : {impact_total:.0f} cas.jours"

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df_riau["Date"], df_riau["I(t)"], label="I(t) lissé (Riau)")
        ax.axvspan(rupture_date, rupture_date + pd.Timedelta(days=window_days), color="red", alpha=0.2, label="Sans mesures")
        ax.axvspan(rupture_date - pd.Timedelta(days=window_days), rupture_date, color="green", alpha=0.2, label="Avec mesures")
        ax.axvline(rupture_date, color="k", linestyle="--", label="Date rupture")
        ax.set_xlabel("Date")
        ax.set_ylabel("Nouveaux cas lissés")
        ax.set_title("Impact estimé des mesures sanitaires (Simpson)")
        ax.legend()
        fig.tight_layout()
        show_plot_window(fig, result_txt)
    else:
        result_txt = "Données insuffisantes pour effectuer l'analyse."
        show_result_only(result_txt)

def show_plot_window(fig, result_txt):
    win = ctk.CTkToplevel()
    win.title("Impact des mesures sanitaires - Simpson")
    win.geometry("1100x700")

    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = ctk.CTkCanvas(frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
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

    ctk.CTkLabel(scrollable_frame, text=result_txt, font=("Arial", 14)).pack(pady=10)

    def resize_canvas(event):
        canvas.itemconfig(scrollable_frame_id, width=event.width)
    canvas.bind("<Configure>", resize_canvas)

def show_result_only(result_txt):
    win = ctk.CTkToplevel()
    win.title("Impact des mesures sanitaires - Simpson")
    win.geometry("500x200")
    ctk.CTkLabel(win, text=result_txt, font=("Arial", 14)).pack(padx=20, pady=40)

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Impact des mesures sanitaires - Simpson")
    app.geometry("400x200")
    ctk.CTkLabel(app, text="Impact des mesures sanitaires\nMéthode de Simpson", font=("Arial", 16, "bold")).pack(pady=20)
    ctk.CTkButton(app, text="Analyser l'impact", command=analyse_impact).pack(pady=10)
    ctk.CTkButton(app, text="Quitter", command=app.destroy).pack(pady=10)
    app.mainloop()