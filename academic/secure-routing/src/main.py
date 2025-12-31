import customtkinter as ctk
import sys
import io
import os

# ---------------------------------------------------------
# Path configuration
# ---------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms.dijkstra import main as dijkstra_main
from algorithms.astar import main as astar_main
from algorithms.astar_initial import main as astar_initial_main
from analysis.comparaison import main as comparaison_main
from analysis.scalabilite import main as scalabilite_main
from analysis.calcul_poids import main as calcul_poids_main


# ---------------------------------------------------------
# Output redirection
# ---------------------------------------------------------
class OutputRedirector(io.StringIO):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def write(self, s):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", s)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def flush(self):
        pass


def run_and_capture(func, textbox, status_label, notify_figures=False):
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")
    textbox.configure(state="disabled")

    status_label.configure(text="Running...", text_color="#FFA000")

    old_stdout = sys.stdout
    sys.stdout = OutputRedirector(textbox)

    try:
        func()
        status_label.configure(text="Completed successfully", text_color="#4CAF50")
        if notify_figures:
            textbox.configure(state="normal")
            textbox.insert("end", "\n[INFO] Figures generated in 'figures' folder\n")
            textbox.configure(state="disabled")
    except Exception as e:
        status_label.configure(text="Error occurred", text_color="#F44336")
        textbox.configure(state="normal")
        textbox.insert("end", f"\n[ERROR] {e}\n")
        textbox.configure(state="disabled")
    finally:
        sys.stdout = old_stdout


# ---------------------------------------------------------
# Main Application
# ---------------------------------------------------------
def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Secure Routing Algorithms")
    app.geometry("1024x680")
    app.minsize(900, 580)

    # =======================
    # GRID CONFIG
    # =======================
    app.grid_columnconfigure(0, weight=0)
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(1, weight=1)

    # =======================
    # HEADER
    # =======================
    header = ctk.CTkFrame(app, corner_radius=12)
    header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=10)

    ctk.CTkLabel(
        header,
        text="Secure Routing with Graph Algorithms",
        font=("Segoe UI", 22, "bold"),
        text_color="#00d4ff"
    ).pack(pady=(10, 2))

    ctk.CTkLabel(
        header,
        text="Operations Research Mini-Project • Network Optimization",
        font=("Segoe UI", 12),
        text_color="#b0b0b0"
    ).pack(pady=(0, 10))

    # =======================
    # LEFT PANEL (SCROLLABLE)
    # =======================
    controls = ctk.CTkScrollableFrame(app, width=260, corner_radius=12)
    controls.grid(row=1, column=0, sticky="ns", padx=(16, 8), pady=8)

    ctk.CTkLabel(
        controls,
        text="Controls",
        font=("Segoe UI", 15, "bold")
    ).pack(pady=(10, 6))

    # Compact button configuration
    button_cfg = {
        "height": 32,
        "corner_radius": 8,
        "font": ("Segoe UI", 11)
    }

    def section(title):
        ctk.CTkLabel(
            controls,
            text=title,
            font=("Segoe UI", 11, "bold"),
            text_color="#00d4ff"
        ).pack(anchor="w", pady=(10, 4), padx=10)

    # -----------------------
    # Core algorithms
    # -----------------------
    section("Core Algorithms")

    ctk.CTkButton(
        controls, text="Run Dijkstra",
        command=lambda: run_and_capture(dijkstra_main, textbox, status_label, True),
        **button_cfg
    ).pack(fill="x", padx=10, pady=3)

    ctk.CTkButton(
        controls, text="Run A* (Initial)",
        command=lambda: run_and_capture(astar_initial_main, textbox, status_label, True),
        **button_cfg
    ).pack(fill="x", padx=10, pady=3)

    ctk.CTkButton(
        controls, text="Run A* (Corrected)",
        command=lambda: run_and_capture(astar_main, textbox, status_label, True),
        **button_cfg
    ).pack(fill="x", padx=10, pady=3)

    # -----------------------
    # Analysis tools
    # -----------------------
    section("Analysis Tools")

    ctk.CTkButton(
        controls, text="Compare Dijkstra vs A*",
        command=lambda: run_and_capture(comparaison_main, textbox, status_label),
        **button_cfg
    ).pack(fill="x", padx=10, pady=3)

    ctk.CTkButton(
        controls, text="Scalability Analysis",
        command=lambda: run_and_capture(scalabilite_main, textbox, status_label),
        **button_cfg
    ).pack(fill="x", padx=10, pady=3)

    ctk.CTkButton(
        controls, text="Weight Calculation",
        command=lambda: run_and_capture(calcul_poids_main, textbox, status_label),
        **button_cfg
    ).pack(fill="x", padx=10, pady=3)

    # -----------------------
    # Exit
    # -----------------------
    section("Application")

    ctk.CTkButton(
        controls,
        text="Exit Application",
        fg_color="#d32f2f",
        hover_color="#b71c1c",
        command=app.destroy,
        **button_cfg
    ).pack(fill="x", padx=10, pady=(6, 12))

    # =======================
    # RIGHT PANEL (OUTPUT)
    # =======================
    output = ctk.CTkFrame(app, corner_radius=12)
    output.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=8)

    output.grid_columnconfigure(0, weight=1)
    output.grid_rowconfigure(2, weight=1)

    ctk.CTkLabel(
        output,
        text="Output Console",
        font=("Segoe UI", 16, "bold")
    ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

    status_label = ctk.CTkLabel(
        output,
        text="Ready",
        font=("Segoe UI", 11),
        text_color="#808080"
    )
    status_label.grid(row=1, column=0, padx=16, sticky="w")

    textbox = ctk.CTkTextbox(
        output,
        font=("Consolas", 11),
        state="disabled",
        corner_radius=8
    )
    textbox.grid(row=2, column=0, sticky="nsew", padx=16, pady=(8, 16))

    app.eval("tk::PlaceWindow . center")
    app.mainloop()


if __name__ == "__main__":
    main()
