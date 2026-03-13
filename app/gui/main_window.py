import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from app.config.app_config import APP_NAME, APP_AUTHOR, APP_CONTACT_EMAIL
from app.services.certificate_service import generate_certificates
from app.services.file_identification_service import identify_pdf_files
from app.utils.path_utils import open_folder
from app.validators.pairing_validator import validate_selected_pdf_pair


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)

        self.selected_files = []
        self.output_folder = ""
        self.validation_result = None

        self._configure_style()
        self._build_ui()

    def _configure_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.root.configure(bg="#eef2f7")

        style.configure("App.TFrame", background="#eef2f7")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("CardTitle.TLabel", background="#ffffff", font=("Segoe UI", 10, "bold"))
        style.configure("CardText.TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#eef2f7", font=("Segoe UI", 20, "bold"))
        style.configure("SubHeader.TLabel", background="#eef2f7", font=("Segoe UI", 10))
        style.configure("Footer.TLabel", background="#eef2f7", font=("Segoe UI", 9))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=20, style="App.TFrame")
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame, style="App.TFrame")
        header_frame.pack(fill="x", pady=(0, 16))

        ttk.Label(
            header_frame,
            text=APP_NAME,
            style="Header.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="Selecione os PDFs do colaborador e gere os certificados separados automaticamente.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        content_frame = ttk.Frame(main_frame, style="App.TFrame")
        content_frame.pack(fill="both", expand=True)

        top_row = ttk.Frame(content_frame, style="App.TFrame")
        top_row.pack(fill="x", pady=(0, 12))

        top_left = ttk.Frame(top_row, style="Card.TFrame", padding=14)
        top_left.pack(side="left", fill="both", expand=True)

        top_right = ttk.Frame(top_row, style="Card.TFrame", padding=14)
        top_right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        ttk.Label(top_left, text="Arquivos PDF", style="CardTitle.TLabel").pack(anchor="w")

        ttk.Button(
            top_left,
            text="Selecionar os 2 PDFs",
            command=self.select_pdf_files,
            style="Primary.TButton",
        ).pack(anchor="w", pady=(10, 10))

        self.selected_files_box = tk.Listbox(
            top_left,
            height=5,
            font=("Segoe UI", 9),
            activestyle="none",
            relief="solid",
            bd=1,
            highlightthickness=0,
        )
        self.selected_files_box.pack(fill="x")

        ttk.Label(top_right, text="Identificação automática", style="CardTitle.TLabel").pack(anchor="w")

        info_grid = ttk.Frame(top_right, style="Card.TFrame")
        info_grid.pack(fill="x", pady=(10, 0))

        ttk.Label(info_grid, text="Colaborador", style="CardText.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        self.person_label = ttk.Label(info_grid, text="-", style="CardText.TLabel")
        self.person_label.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=4)

        ttk.Label(info_grid, text="Arquivo NRS", style="CardText.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.nrs_label = ttk.Label(info_grid, text="-", style="CardText.TLabel")
        self.nrs_label.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=4)

        ttk.Label(info_grid, text="Arquivo NR-37", style="CardText.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.nr37_label = ttk.Label(info_grid, text="-", style="CardText.TLabel")
        self.nr37_label.grid(row=2, column=1, sticky="w", padx=(12, 0), pady=4)

        middle_row = ttk.Frame(content_frame, style="App.TFrame")
        middle_row.pack(fill="x", pady=(0, 12))

        middle_card = ttk.Frame(middle_row, style="Card.TFrame", padding=14)
        middle_card.pack(fill="x")

        ttk.Label(middle_card, text="Pasta de saída", style="CardTitle.TLabel").pack(anchor="w")

        buttons_row = ttk.Frame(middle_card, style="Card.TFrame")
        buttons_row.pack(anchor="w", pady=(10, 8))

        ttk.Button(
            buttons_row,
            text="Selecionar pasta",
            command=self.select_output_folder,
        ).pack(side="left")

        self.open_output_button = ttk.Button(
            buttons_row,
            text="Abrir pasta",
            command=self.open_output_folder,
            state="disabled",
        )
        self.open_output_button.pack(side="left", padx=(8, 0))

        self.output_label = ttk.Label(
            middle_card,
            text="Nenhuma pasta selecionada.",
            style="CardText.TLabel",
        )
        self.output_label.pack(anchor="w")

        action_row = ttk.Frame(content_frame, style="App.TFrame")
        action_row.pack(fill="x", pady=(0, 12))

        action_card = ttk.Frame(action_row, style="Card.TFrame", padding=14)
        action_card.pack(fill="x")

        ttk.Label(action_card, text="Ação principal", style="CardTitle.TLabel").pack(anchor="w")

        self.process_button = ttk.Button(
            action_card,
            text="Gerar certificados",
            state="disabled",
            command=self.process_pdfs,
            style="Primary.TButton",
        )
        self.process_button.pack(anchor="w", pady=(10, 8))

        self.status_line = ttk.Label(
            action_card,
            text="Aguardando seleção dos arquivos.",
            style="CardText.TLabel",
        )
        self.status_line.pack(anchor="w")

        status_row = ttk.Frame(content_frame, style="App.TFrame")
        status_row.pack(fill="both", expand=True)

        status_card = ttk.Frame(status_row, style="Card.TFrame", padding=14)
        status_card.pack(fill="both", expand=True)

        ttk.Label(status_card, text="Andamento", style="CardTitle.TLabel").pack(anchor="w")

        self.log_text = tk.Text(
            status_card,
            height=10,
            wrap="word",
            font=("Segoe UI", 10),
            state="disabled",
            relief="solid",
            bd=1,
            highlightthickness=0,
            bg="#fafbfc",
        )
        self.log_text.pack(fill="both", expand=True, pady=(10, 0))

        footer_label = ttk.Label(
            main_frame,
            text=f"Desenvolvido por {APP_AUTHOR} | {APP_CONTACT_EMAIL}",
            style="Footer.TLabel",
        )
        footer_label.pack(anchor="center", pady=(14, 0))

    def _set_status(self, message: str):
        self.status_line.config(text=message)

    def _update_process_button_state(self):
        if self.validation_result and self.validation_result.is_valid and self.output_folder:
            self.process_button.config(state="normal")
        else:
            self.process_button.config(state="disabled")

    def _update_output_button_state(self):
        if self.output_folder:
            self.open_output_button.config(state="normal")
        else:
            self.open_output_button.config(state="disabled")

    def _reset_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def log(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"• {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def reset_identification_labels(self):
        self.person_label.config(text="-")
        self.nrs_label.config(text="-")
        self.nr37_label.config(text="-")

    def auto_validate_selection(self):
        if not self.selected_files:
            self.validation_result = None
            self.reset_identification_labels()
            self._update_process_button_state()
            self._set_status("Aguardando seleção dos arquivos.")
            return

        identified_files = identify_pdf_files(self.selected_files)
        result = validate_selected_pdf_pair(identified_files)
        self.validation_result = result

        if not result.is_valid:
            self.reset_identification_labels()
            self._update_process_button_state()
            self._set_status("Não foi possível confirmar os arquivos.")
            self.log(result.message)
            return

        self.person_label.config(text=result.person_name_base)
        self.nrs_label.config(text=Path(result.nrs_file.original_path).name)
        self.nr37_label.config(text=Path(result.nr37_file.original_path).name)

        self._update_process_button_state()
        self._set_status("Arquivos confirmados com sucesso.")
        self.log(f"Colaborador identificado: {result.person_name_base}")

        if not self.output_folder:
            self.log("Agora selecione a pasta onde os certificados serão salvos.")

    def select_pdf_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Selecione os 2 PDFs do colaborador",
            filetypes=[("Arquivos PDF", "*.pdf")],
        )

        if not file_paths:
            return

        self._reset_log()
        self.selected_files = list(file_paths)
        self.selected_files_box.delete(0, "end")

        for file_path in self.selected_files:
            self.selected_files_box.insert("end", Path(file_path).name)

        self.validation_result = None
        self.reset_identification_labels()
        self._update_process_button_state()

        self._set_status("Analisando os arquivos selecionados...")
        self.log("Arquivos selecionados com sucesso.")
        self.auto_validate_selection()

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Selecione a pasta de saída")

        if not folder_path:
            return

        self.output_folder = folder_path
        self.output_label.config(text=self.output_folder)
        self._update_output_button_state()
        self._update_process_button_state()

        self.log("Pasta de saída selecionada com sucesso.")

        if self.validation_result and self.validation_result.is_valid:
            self._set_status("Tudo pronto para gerar os certificados.")
        else:
            self._set_status("Pasta selecionada. Falta confirmar os arquivos.")

    def open_output_folder(self):
        if not self.output_folder:
            messagebox.showwarning("Aviso", "Selecione uma pasta de saída primeiro.")
            return

        open_folder(self.output_folder)

    def process_pdfs(self):
        if not self.validation_result or not self.validation_result.is_valid:
            messagebox.showwarning("Aviso", "Selecione arquivos válidos antes de processar.")
            return

        if not self.output_folder:
            messagebox.showwarning("Aviso", "Selecione a pasta de saída antes de processar.")
            return

        try:
            self._reset_log()
            self.process_button.config(state="disabled")
            self._set_status("Gerando certificados...")

            self.log(f"Iniciando geração para {self.validation_result.person_name_base}.")
            result = generate_certificates(
                nrs_pdf_path=self.validation_result.nrs_file.original_path,
                nr37_pdf_path=self.validation_result.nr37_file.original_path,
                person_name_output=self.validation_result.person_name_output,
                output_folder=self.output_folder,
                log_callback=self.log,
            )

            self.log("Os certificados foram gerados com sucesso.")
            self.log(f"Foram criados {len(result.generated_files)} arquivos.")
            self._set_status("Processamento concluído com sucesso.")
            messagebox.showinfo("Concluído", result.message)
            self._update_process_button_state()

        except Exception as error:
            self.log(str(error))
            self._set_status("Ocorreu um problema no processamento.")
            messagebox.showerror("Erro", str(error))
            self._update_process_button_state()