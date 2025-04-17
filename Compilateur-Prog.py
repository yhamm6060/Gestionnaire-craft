import os
import sys
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

class PythonToExeConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.title("Python vers EXE - Convertisseur (Python 3.13 Compatible)")
        self.geometry("700x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables
        self.script_path = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.console_output = ctk.StringVar(value="True")
        self.onefile_output = ctk.StringVar(value="True")
        self.icon_path = ctk.StringVar()
        self.additional_data = ctk.StringVar()
        self.additional_imports = ctk.StringVar()

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        
        # Titre
        title_label = ctk.CTkLabel(main_frame, text="Convertisseur Python en Exécutable", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Sélection du fichier Python
        file_label = ctk.CTkLabel(main_frame, text="Fichier Python:")
        file_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        file_frame.grid_columnconfigure(0, weight=1)
        
        file_entry = ctk.CTkEntry(file_frame, textvariable=self.script_path)
        file_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        file_button = ctk.CTkButton(file_frame, text="Parcourir", command=self.browse_script)
        file_button.grid(row=0, column=1)

        # Sélection du dossier de sortie
        output_label = ctk.CTkLabel(main_frame, text="Dossier de sortie:")
        output_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        output_frame.grid_columnconfigure(0, weight=1)
        
        output_entry = ctk.CTkEntry(output_frame, textvariable=self.output_dir)
        output_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        output_button = ctk.CTkButton(output_frame, text="Parcourir", command=self.browse_output)
        output_button.grid(row=0, column=1)

        # Sélection de l'icône
        icon_label = ctk.CTkLabel(main_frame, text="Icône (optionnel):")
        icon_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        icon_frame = ctk.CTkFrame(main_frame)
        icon_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        icon_frame.grid_columnconfigure(0, weight=1)
        
        icon_entry = ctk.CTkEntry(icon_frame, textvariable=self.icon_path)
        icon_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        icon_button = ctk.CTkButton(icon_frame, text="Parcourir", command=self.browse_icon)
        icon_button.grid(row=0, column=1)

        # Options
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        
        console_label = ctk.CTkLabel(options_frame, text="Afficher console:")
        console_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        console_switch = ctk.CTkSwitch(options_frame, text="", variable=self.console_output, 
                                       onvalue="True", offvalue="False")
        console_switch.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        console_switch.select()
        
        onefile_label = ctk.CTkLabel(options_frame, text="Fichier unique:")
        onefile_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        onefile_switch = ctk.CTkSwitch(options_frame, text="", variable=self.onefile_output, 
                                       onvalue="True", offvalue="False")
        onefile_switch.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        onefile_switch.select()

        # Données additionnelles
        additionals_frame = ctk.CTkFrame(main_frame)
        additionals_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        additionals_frame.grid_columnconfigure(0, weight=1)
        additionals_frame.grid_columnconfigure(1, weight=3)
        
        data_label = ctk.CTkLabel(additionals_frame, text="Fichiers additionnels\n(séparés par des virgules):")
        data_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        data_entry = ctk.CTkEntry(additionals_frame, textvariable=self.additional_data)
        data_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        imports_label = ctk.CTkLabel(additionals_frame, text="Modules à inclure\n(séparés par des virgules):")
        imports_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        imports_entry = ctk.CTkEntry(additionals_frame, textvariable=self.additional_imports)
        imports_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Zone de log
        log_label = ctk.CTkLabel(main_frame, text="Journal de compilation:")
        log_label.grid(row=6, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        
        self.log_text = ctk.CTkTextbox(main_frame, height=150)
        self.log_text.grid(row=7, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")

        # Bouton de compilation
        compile_button = ctk.CTkButton(main_frame, text="Compiler", 
                                     command=self.compile_script,
                                     fg_color="#28a745", 
                                     hover_color="#218838")
        compile_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        # Définir des valeurs par défaut
        self.output_dir.set(os.path.expanduser("~/Desktop"))

    def browse_script(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier Python",
            filetypes=[("Fichiers Python", "*.py"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.script_path.set(file_path)

    def browse_output(self):
        dir_path = filedialog.askdirectory(
            title="Sélectionner le dossier de sortie"
        )
        if dir_path:
            self.output_dir.set(dir_path)

    def browse_icon(self):
        icon_path = filedialog.askopenfilename(
            title="Sélectionner une icône",
            filetypes=[("Fichiers icône", "*.ico"), ("Tous les fichiers", "*.*")]
        )
        if icon_path:
            self.icon_path.set(icon_path)

    def update_log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def patch_pkg_resources(self):
        """Patch pkg_resources pour Python 3.13"""
        try:
            pkg_resources_path = os.path.join(sys.prefix, "Lib", "site-packages", "pkg_resources", "__init__.py")
            if not os.path.exists(pkg_resources_path):
                self.update_log("Impossible de trouver pkg_resources pour le patch")
                return False
                
            # Créer une sauvegarde si elle n'existe pas déjà
            backup_path = pkg_resources_path + ".bak"
            if not os.path.exists(backup_path):
                with open(pkg_resources_path, 'r') as f:
                    content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(content)
                self.update_log(f"Sauvegarde créée: {backup_path}")
            
            # Lire le contenu
            with open(pkg_resources_path, 'r') as f:
                content = f.read()
            
            # Remplacer la ligne problématique
            if 'register_finder(pkgutil.ImpImporter, find_on_path)' in content:
                patched_content = content.replace(
                    'register_finder(pkgutil.ImpImporter, find_on_path)',
                    '# Ligne patched pour Python 3.13\ntry:\n    register_finder(pkgutil.ImpImporter, find_on_path)\nexcept AttributeError:\n    pass'
                )
                
                with open(pkg_resources_path, 'w') as f:
                    f.write(patched_content)
                    
                self.update_log("pkg_resources patché avec succès pour Python 3.13")
                return True
            else:
                self.update_log("La ligne problématique n'a pas été trouvée dans pkg_resources")
                return False
                
        except Exception as e:
            self.update_log(f"Erreur lors du patch de pkg_resources: {str(e)}")
            return False

    def compile_script(self):
        # Vérifier si le fichier Python est spécifié
        script_path = self.script_path.get()
        if not script_path or not os.path.isfile(script_path):
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Python valide.")
            return

        # Vérifier si le dossier de sortie est spécifié
        output_dir = self.output_dir.get()
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de sortie valide.")
            return

        # Construire la commande PyInstaller
        command = ["pyinstaller"]
        
        # Options de base
        if self.onefile_output.get() == "True":
            command.append("--onefile")
        else:
            command.append("--onedir")
            
        if self.console_output.get() == "False":
            command.append("--noconsole")
            
        # Icon
        if self.icon_path.get():
            command.extend(["--icon", self.icon_path.get()])
            
        # Output directory
        command.extend(["--distpath", output_dir])
        
        # Additional data files
        if self.additional_data.get():
            data_files = self.additional_data.get().split(",")
            for data in data_files:
                data = data.strip()
                if data:
                    command.extend(["--add-data", f"{data}{os.pathsep}."])
                    
        # Additional imports
        if self.additional_imports.get():
            imports = self.additional_imports.get().split(",")
            for imp in imports:
                imp = imp.strip()
                if imp:
                    command.extend(["--hidden-import", imp])

        # Add script path
        command.append(script_path)
        
        # Afficher la commande
        cmd_str = " ".join(command)
        self.update_log(f"Exécution de la commande:\n{cmd_str}\n")
        
        # Patcher pkg_resources pour Python 3.13
        if sys.version_info >= (3, 13):
            self.update_log("Détection de Python 3.13, application du patch...")
            if not self.patch_pkg_resources():
                self.update_log("Échec du patch, la compilation pourrait échouer")
        
        self.update_log("Compilation en cours, veuillez patienter...\n")
        # Lancer la compilation dans un thread séparé
        threading.Thread(target=self._run_compilation, args=(command,)).start()

    def _run_compilation(self, command):
        try:
            # Vérifier si PyInstaller est installé
            try:
                import PyInstaller
            except ImportError:
                self.update_log("PyInstaller n'est pas installé. Installation en cours...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
                self.update_log("PyInstaller installé avec succès.")
            
            # Ajouter le patch pour Python 3.13 si nécessaire
            if sys.version_info >= (3, 13):
                # Essayons d'installer auto-py-to-exe comme alternative
                try:
                    import auto_py_to_exe
                except ImportError:
                    try:
                        self.update_log("Tentative d'installation d'une solution alternative (auto-py-to-exe)...")
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "auto-py-to-exe"])
                        self.update_log("auto-py-to-exe installé avec succès. Vous pouvez l'utiliser comme alternative.")
                    except Exception as e:
                        self.update_log(f"Erreur lors de l'installation d'auto-py-to-exe: {str(e)}")
            
            # Exécuter la commande
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Capture de la sortie
            for line in process.stdout:
                self.update_log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.update_log("\nCompilation terminée avec succès!")
                messagebox.showinfo("Succès", "Le fichier exécutable a été créé avec succès.")
            else:
                self.update_log("\nLa compilation a échoué.")
                
                # Solutions alternatives pour Python 3.13
                if sys.version_info >= (3, 13):
                    self.update_log("\nComme vous utilisez Python 3.13, voici des solutions alternatives:")
                    self.update_log("1. Essayez d'installer la version de développement de PyInstaller:")
                    self.update_log("   pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip")
                    self.update_log("\n2. Lancez auto-py-to-exe (installé précédemment) avec la commande:")
                    self.update_log("   auto-py-to-exe")
                    self.update_log("\n3. Essayez une version plus ancienne de Python (3.11 ou 3.12)")
                
                messagebox.showerror("Erreur", "La compilation a échoué. Consultez le journal pour plus de détails et solutions alternatives.")
                
        except Exception as e:
            self.update_log(f"\nErreur: {str(e)}")
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")

class DirectPyInstaller:
    """Classe pour une compilation directe sans interface graphique"""
    
    @staticmethod
    def patch_pkg_resources():
        """Patch pkg_resources pour Python 3.13"""
        try:
            # Cherche tous les chemins possibles pour pkg_resources
            potential_paths = [
                os.path.join(sys.prefix, "Lib", "site-packages", "pkg_resources", "__init__.py"),
                os.path.join(os.path.dirname(os.__file__), "..", "site-packages", "pkg_resources", "__init__.py")
            ]
            
            pkg_resources_path = None
            for path in potential_paths:
                if os.path.exists(path):
                    pkg_resources_path = path
                    break
                    
            if not pkg_resources_path:
                print("Impossible de trouver pkg_resources pour le patch")
                return False
                
            # Créer une sauvegarde si elle n'existe pas déjà
            backup_path = pkg_resources_path + ".bak"
            if not os.path.exists(backup_path):
                with open(pkg_resources_path, 'r') as f:
                    content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(content)
                print(f"Sauvegarde créée: {backup_path}")
            
            # Lire le contenu
            with open(pkg_resources_path, 'r') as f:
                content = f.read()
            
            # Remplacer la ligne problématique
            if 'register_finder(pkgutil.ImpImporter, find_on_path)' in content:
                patched_content = content.replace(
                    'register_finder(pkgutil.ImpImporter, find_on_path)',
                    '# Ligne patched pour Python 3.13\ntry:\n    register_finder(pkgutil.ImpImporter, find_on_path)\nexcept AttributeError:\n    pass'
                )
                
                with open(pkg_resources_path, 'w') as f:
                    f.write(patched_content)
                    
                print("pkg_resources patché avec succès pour Python 3.13")
                return True
            else:
                print("La ligne problématique n'a pas été trouvée dans pkg_resources")
                return False
                
        except Exception as e:
            print(f"Erreur lors du patch de pkg_resources: {str(e)}")
            return False
            
    @staticmethod
    def compile_direct(script_path, output_dir=None, onefile=True, console=True, icon=None):
        """Compile directement un script Python en exécutable"""
        if not output_dir:
            output_dir = os.path.expanduser("~/Desktop")
            
        # Patcher pkg_resources si Python 3.13
        if sys.version_info >= (3, 13):
            print("Détection de Python 3.13, application du patch...")
            if not DirectPyInstaller.patch_pkg_resources():
                print("Échec du patch, la compilation pourrait échouer")
            
        # Construire la commande
        command = ["pyinstaller"]
        
        if onefile:
            command.append("--onefile")
        if not console:
            command.append("--noconsole")
        if icon:
            command.extend(["--icon", icon])
            
        command.extend(["--distpath", output_dir, script_path])
        
        print(f"Exécution de la commande: {' '.join(command)}")
        print("Compilation en cours...")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Affichage de la sortie en temps réel
            for line in process.stdout:
                print(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                print("\nCompilation terminée avec succès!")
                return True
            else:
                print("\nLa compilation a échoué.")
                
                # Solutions alternatives pour Python 3.13
                if sys.version_info >= (3, 13):
                    print("\nComme vous utilisez Python 3.13, voici des solutions alternatives:")
                    print("1. Essayez d'installer la version de développement de PyInstaller:")
                    print("   pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip")
                    print("\n2. Utilisez auto-py-to-exe avec la commande:")
                    print("   pip install auto-py-to-exe")
                    print("   auto-py-to-exe")
                    print("\n3. Essayez une version plus ancienne de Python (3.11 ou 3.12)")
                
                return False
                
        except Exception as e:
            print(f"\nErreur: {str(e)}")
            return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Mode ligne de commande avec arguments
        script_path = sys.argv[1]
        output_dir = os.path.expanduser("~/Desktop") if len(sys.argv) <= 2 else sys.argv[2]
        DirectPyInstaller.compile_direct(script_path, output_dir)
    else:
        # Mode interface graphique
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"
        
        app = PythonToExeConverter()
        app.mainloop()
