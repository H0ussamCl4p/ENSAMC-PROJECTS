# SIRD Dashboard - Projet d'Analyse Numérique 2024-205
# Copyright (c) 2025 CHOUBIK Houssam. All rights reserved.

import customtkinter as ctk
import subprocess
import os
from PIL import Image
import webbrowser

# Le thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def run_script(script_name):
    if os.path.exists(script_name):
        subprocess.Popen(['python', script_name])
    else:
        ctk.CTkMessagebox(title="Error", message=f"{script_name} not found.")

def open_url(url):
    webbrowser.open_new(url)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SIRD APP")
        self.geometry("900x700")
        self.resizable(False, False)
        try:
            self.iconbitmap("your_logo.ico")
        except Exception:
            pass
        self.show_accueil()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_sidebar(self, selected="accueil"):
        sidebar = ctk.CTkFrame(self, width=400, height=400, corner_radius=0, fg_color="#1a1a1a")
        sidebar.pack(side="left", fill="y")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("your_logo.png"), size=(60, 60))
            logo_label = ctk.CTkLabel(sidebar, image=logo_img, text="")
            logo_label.pack(pady=(30, 10))
        except Exception:
            logo = ctk.CTkLabel(sidebar, text="SIRD \n App", font=("Arial", 18, "bold"), text_color="#00ff99")
            logo.pack(pady=(30, 20))
        acceuil_btn = ctk.CTkButton(
            sidebar, text="Accueil", command=self.show_accueil, width=120,
            fg_color="#054a29" if selected == "accueil" else "#222",
            hover_color="#067a3a", text_color="#fff"
        )
        acceuil_btn.pack(pady=10)

        doc_btn = ctk.CTkButton(
            sidebar, text="Documentation", command=self.show_documentation, width=120,
            fg_color="#3B8ED0" if selected == "doc" else "#222",
            hover_color="#2566a3", text_color="#fff"
        )
        doc_btn.pack(pady=10)
        apropos_btn = ctk.CTkButton(
            sidebar, text="À propos", command=self.show_apropos, width=120,
            fg_color="#3B8ED0" if selected == "apropos" else "#222",
            hover_color="#2566a3", text_color="#fff"
        )
        apropos_btn.pack(pady=10)
        copyright_label = ctk.CTkLabel(
            sidebar,
            text="© 2025 CHOUBIK Houssam",
            font=("Arial", 10),
            anchor="s",
            text_color="#888"
        )
        copyright_label.pack(side="bottom", pady=10)

    def show_accueil(self):
        self.clear_window()
        self.show_sidebar(selected="accueil")
        main_frame = ctk.CTkFrame(self, width=300, height=400, corner_radius=15, fg_color="#222")
        main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        title = ctk.CTkLabel(main_frame, text="Bienvenue dans l'outil SIRD", font=("Arial", 20, "bold"), text_color="#00ff99")
        title.pack(pady=(40, 10))
        desc = (
            "Cette application a été conçue dans le cadre du projet d'analyse numérique conformément au cahier des charges établi par notre Professeur A.KAMOUSS pour étudier la propagation du virus Covid-19.\n\n " 
            "Le but de l'application est de modéliser la dynamique de propagation du virus en utilisant des techniques d'analyse numérique à savoir l'interpolation, la résolution d'équations non linéaires, la dérivation numérique et la résolution d'équations différentielles.\n\n"
            "Elle permet également d'explorer l'impact de certaines prédictions et d'évaluer l'évolution de la pandémie en fonction des catégories de personnes (infectées, susceptibles, rétablies et décédées).\n\n"
            "Cliquez sur 'Démarrer' pour accéder aux options de lancement des scripts."
        )
        desc_label = ctk.CTkLabel(main_frame, text=desc, font=("Arial", 14), justify="center", wraplength=440, text_color="#fff")
        desc_label.pack(pady=10)
        start_btn = ctk.CTkButton(main_frame, text="Démarrer", command=self.show_dashboard, width=180, fg_color="#00ff99", hover_color="#067a3a", text_color="#222")
        start_btn.pack(pady=30)

    def show_dashboard(self):
        self.clear_window()
        self.show_sidebar(selected="dashboard")
        main_frame = ctk.CTkFrame(self, width=500, height=400, corner_radius=15, fg_color="#222")
        main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        title = ctk.CTkLabel(main_frame, text="Lancer un script", font=("Arial", 20, "bold"), text_color="#00ff99")
        title.pack(pady=(20, 10))

        # Section: Interpolation
        interp_label = ctk.CTkLabel(main_frame, text="Interpolation", font=("Arial", 16, "bold"), text_color="#00ff99")
        interp_label.pack(pady=(10, 0))
        interp_frame = ctk.CTkFrame(main_frame, fg_color="#222")
        interp_frame.pack(pady=2)
        ctk.CTkButton(interp_frame, text="Lagrange", command=lambda: run_script("./Interpolation/lagrange.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(interp_frame, text="Newton", command=lambda: run_script("./Interpolation/newton.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(interp_frame, text="Neville", command=lambda: run_script("./Interpolation/neville.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkButton(interp_frame, text="Splines Cubqiues", command=lambda: run_script("./Interpolation/SplineCubique.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(interp_frame, text="Comparaison des Méthodes", command=lambda: run_script("./Interpolation/Comparaison-Interpolation.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=1, column=1, padx=10, pady=5)

        # Section: Equations non linéaires
        eqn_label = ctk.CTkLabel(main_frame, text="Équations non linéaires", font=("Arial", 16, "bold"), text_color="#00ff99")
        eqn_label.pack(pady=(10, 0))
        eqn_frame = ctk.CTkFrame(main_frame, fg_color="#222")
        eqn_frame.pack(pady=2)
        ctk.CTkButton(eqn_frame, text="Pic épidémique", command=lambda: run_script("./Equations-non-lineaires/equation_a.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(eqn_frame, text="Seuil d'immunité collective", command=lambda: run_script("./Equations-non-lineaires/equation_b.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(eqn_frame, text="Temps critique pour une intervention sanitaire", command=lambda: run_script("./Equations-non-lineaires/equation_c.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=2, padx=10, pady=5)

        # Section: Dérivation
        deriv_label = ctk.CTkLabel(main_frame, text="Dérivation", font=("Arial", 16, "bold"), text_color="#00ff99")
        deriv_label.pack(pady=(10, 0))
        deriv_frame = ctk.CTkFrame(main_frame, fg_color="#222")
        deriv_frame.pack(pady=2)
        ctk.CTkButton(deriv_frame, text="Taux de transmission", command=lambda: run_script("./Derivation/derivation_a.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(deriv_frame, text="Taux de croissance intial", command=lambda: run_script("./Derivation/derivation_b.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(deriv_frame, text="Moment de décroissance", command=lambda: run_script("./Derivation/derivation_c.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkButton(deriv_frame, text="Vitesse de propagation", command=lambda: run_script("./Derivation/derivation_d.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(deriv_frame, text="Taux de variation", command=lambda: run_script("./Derivation/derivation_e.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=1, column=1, padx=10, pady=5)



        # Section: Intégration
        integ_label = ctk.CTkLabel(main_frame, text="Intégration", font=("Arial", 16, "bold"), text_color="#00ff99")
        integ_label.pack(pady=(10, 0))
        integ_frame = ctk.CTkFrame(main_frame, fg_color="#222")
        integ_frame.pack(pady=2)
        ctk.CTkButton(integ_frame, text="Taux de variation - Simpson composite", command=lambda: run_script("./Integration/int-a-simpson-composite.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(integ_frame, text="Taux de variation - Trapèze composite", command=lambda: run_script("./Integration/int-a-trapeze-composite.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(integ_frame, text="Nombre cummulé", command=lambda: run_script("./Integration/int-b.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(integ_frame, text="Durée totale", command=lambda: run_script("./Integration/int-c.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=1, column=1, padx=10, pady=5)      
        ctk.CTkButton(integ_frame, text="Impact - Simpson", command=lambda: run_script("./Integration/int-d-simpson.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=2, column=0, padx=10, pady=5)
        ctk.CTkButton(integ_frame, text="Impact - Trapèze", command=lambda: run_script("./Integration/int-d-trapeze.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=2, column=1, padx=10, pady=5)  
        
        
        # Section: Équations différentielles
        diff_label = ctk.CTkLabel(main_frame, text="Équations différentielles", font=("Arial", 16, "bold"), text_color="#00ff99")
        diff_label.pack(pady=(10, 0))
        diff_frame = ctk.CTkFrame(main_frame, fg_color="#222")
        diff_frame.pack(pady=2)
        ctk.CTkButton(diff_frame, text="Résolution EDO", command=lambda: run_script("./EDO/edo.py"), width=160, fg_color="#3B8ED0", hover_color="#2566a3").grid(row=0, column=0, padx=10, pady=5)
        

        # Boutton de retour
        return_btn = ctk.CTkButton(main_frame, text="Retour", command=self.show_accueil, width=120, fg_color="#054a29", hover_color="#067a3a")
        return_btn.pack(pady=15)

    def show_documentation(self):
        self.clear_window()
        self.show_sidebar(selected="doc")
        main_frame = ctk.CTkFrame(self, width=500, height=400, corner_radius=15, fg_color="#222")
        main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        title = ctk.CTkLabel(main_frame, text="Documentation", font=("Arial", 20, "bold"), text_color="#00ff99")
        title.pack(pady=(30, 10))
        doc_text = (
            "Utilisation du SIRD App :\n\n"
            "1. Cliquez sur 'Accueil' pour revenir à la page d'accueil.\n"
            "2. Cliquez sur 'Démarrer' pour accéder aux scripts à lancer.\n"
            "3. Utilisez le menu à gauche pour naviguer entre les sections.\n\n"
        )
        label = ctk.CTkLabel(main_frame, text=doc_text, font=("Arial", 14), justify="left", wraplength=440, text_color="#fff")
        label.pack(pady=20)


    def show_apropos(self):
        self.clear_window()
        self.show_sidebar(selected="apropos")
        scroll_frame = ctk.CTkScrollableFrame(self, width=500, height=400, fg_color="#222", corner_radius=15)
        scroll_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        title = ctk.CTkLabel(scroll_frame, text="À propos", font=("Arial", 20, "bold"), text_color="#00ff99")
        title.pack(pady=(20, 10))

        members_label = ctk.CTkLabel(scroll_frame, text="Membres du Groupe", font=("Arial", 16, "bold"), text_color="#00ff99")
        members_label.pack(pady=(10, 5))

        # Membres du Groupe
        members = [
            {
                "name": "CHOUBIK Houssam",
                "linkedin": "https://www.linkedin.com/in/houssam-choubik-5b4ba3316/",
                "github": "https://github.com/HoussamCbk",
                "mail": "mailto:",
                "role": "Chef de projet"
            },
            {"name": "KAZOURY Chaimae", 
             "linkedin": "https://www.linkedin.com/in/chaimae-kazoury-040715238/", 
             "github": "https://github.com/chaimae098", 
             "mail": "",
             "role": "Vice chef de projet"},
            {"name": "MOUZAKKI Othmane",
              "linkedin": "https://www.linkedin.com/in/othmane-mouzakki/",
              "github": "",
              "mail": ""},
            {"name": "ELHAMOUDI Wiam",
              "linkedin": "https://ma.linkedin.com/in/wiam-el-hamoudi-8821b5364", 
              "github": "", 
              "mail": ""},
            {"name": "EL MAAROUFI Soukaina", 
             "linkedin": "https://ma.linkedin.com/in/soukaina-el-ma%C3%A2roufi-9b4b29338", 
             "github": "", 
             "mail": ""},
            {"name": "EL MAATAOUI Ihssane", 
             "linkedin": "http://www.linkedin.com/in/ihssane-el-maataoui-694418363", 
             "github": "https://github.com/elmaataoui-ihssane",
              "mail": ""},
            {"name": "LABBAD Mariam", 
             "linkedin": "https://www.linkedin.com/in/mariam-labbad-45575b2b1/", 
             "github": "",
              "mail": ""}

        ]

        for member in members:
            box = ctk.CTkFrame(scroll_frame, fg_color="#1a1a1a", corner_radius=10)
            box.pack(fill="x", padx=10, pady=5)
            name_label = ctk.CTkLabel(box, text=member["name"], font=("Arial", 14, "bold"), text_color="#fff")
            name_label.pack(side="left", padx=10, pady=8)
            if member["linkedin"]:
                linkedin_btn = ctk.CTkButton(box, text="LinkedIn", width=70, fg_color="#0077b5", hover_color="#005983", command=lambda url=member["linkedin"]: open_url(url))
                linkedin_btn.pack(side="left", padx=5)
            if member["github"]:
                github_btn = ctk.CTkButton(box, text="Github", width=70, fg_color="#24292f", hover_color="#444", command=lambda url=member["github"]: open_url(url))
                github_btn.pack(side="left", padx=5)
            if member["mail"]:
                mail_btn = ctk.CTkButton(box, text=member["mail"].replace("mailto:", ""), width=180, fg_color="#c71610", hover_color="#a00", command=lambda url=member["mail"]: open_url(url))
                mail_btn.pack(side="left", padx=5)
            if member.get("role"):
                role_label = ctk.CTkLabel(box, text=member["role"], font=("Arial", 12), text_color="#00ff99")
                role_label.pack(side="right", padx=10, pady=8)

        # Encadrant
        encadrant_label = ctk.CTkLabel(
            scroll_frame,
            text="\nEncadrant",
            font=("Arial", 20, "bold"),
            text_color="#00ff99"
        )
        encadrant_label.pack(pady=(25, 0))

        encadrant_box = ctk.CTkFrame(
            scroll_frame,
            fg_color="#0e2d47",
            border_color="#00ff99",
            border_width=3,
            corner_radius=18
        )
        encadrant_box.pack(fill="x", padx=20, pady=10)

        # Encadrant name
        prof_name = ctk.CTkLabel(
            encadrant_box,
            text="Pr. Abdessamad KAMOUSS",
            font=("Arial", 16, "bold"),
            text_color="#00ff99"
        )
        prof_name.pack(pady=(12, 0), padx=10, anchor="w")

        prof_title = ctk.CTkLabel(
            encadrant_box,
            text="Département d'informatique\nÉcole Nationale Supérieure d'Arts et Métiers de Casablanca\nUniversité Hassan II Casablanca",
            font=("Arial", 13, "italic"),
            text_color="#fff",
            justify="left"
        )
        prof_title.pack(pady=(2, 12), padx=10, anchor="w")

        deco_line = ctk.CTkLabel(
            encadrant_box,
            text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            font=("Arial", 10),
            text_color="#00ff99"
        )
        deco_line.pack(pady=(0, 0), padx=10)

        thanks = ctk.CTkLabel(
            encadrant_box,
            text="Tout nos remerciements à notre Professeur pour nous avoir encadré pour la réalisation de ce projet.",
            font=("Arial", 12, "italic"),
            text_color="#00ff99",
            justify="left"
        )
        thanks.pack(pady=(6, 12), padx=10, anchor="w")


if __name__ == "__main__":
    app = App()
    app.mainloop()