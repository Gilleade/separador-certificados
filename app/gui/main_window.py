import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from app.config.app_config import APP_NAME, APP_AUTHOR, APP_CONTACT_EMAIL
from app.services.batch_grouping_service import group_pdf_files_for_batch
from app.services.batch_processing_service import process_batch_files
from app.services.file_identification_service import identify_pdf_files
from app.services.individual_processing_service import process_individual_files
from app.services.report_service import get_runtime_report_path
from app.utils.path_utils import open_folder, open_path


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)

        self.selected_files = []
        self.output_folder = ""
        self.last_report_path = ""

        self.mode_var = tk.StringVar(value="individual")

        self.individual_ready = False
        self.batch_ready = False

        self._configure_style()
        self._build_ui()
        self._update_buttons()

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
            text="Escolha o modo de uso, selecione os PDFs e gere os certificados automaticamente.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        content_frame = ttk.Frame(main_frame, style="App.TFrame")
        content_frame.pack(fill="both", expand=True)

        top_row = ttk.Frame(content_frame, style="App.TFrame")
        top_row.pack(fill="x", pady=(0, 12))

        mode_card = ttk.Frame(top_row, style="Card.TFrame", padding=14)
        mode_card.pack(side="left", fill="both", expand=True)

        files_card = ttk.Frame(top_row, style="Card.TFrame", padding=14)
        files_card.pack(side="left", fill="both", expand=True, padx=(12, 0))

        ttk.Label(mode_card, text="Modo de uso", style="CardTitle.TLabel").pack(anchor="w")

        ttk.Radiobutton(
            mode_card,
            text="Processamento individual",
            value="individual",
            variable=self.mode_var,
            command=self.on_mode_change,
        ).pack(anchor="w", pady=(10, 2))

        ttk.Radiobutton(
            mode_card,
            text="Processamento em lote",
            value="batch",
            variable=self.mode_var,
            command=self.on_mode_change,
        ).pack(anchor="w", pady=(0, 2))

        self.mode_help_label = ttk.Label(
            mode_card,
            text="No individual, você pode processar 1 ou 2 PDFs de um único colaborador.",
            style="CardText.TLabel",
        )
        self.mode_help_label.pack(anchor="w", pady=(10, 0))

        ttk.Label(files_card, text="Arquivos PDF", style="CardTitle.TLabel").pack(anchor="w")

        self.select_files_button = ttk.Button(
            files_card,
            text="Selecionar PDFs",
            command=self.select_pdf_files,
            style="Primary.TButton",
        )
        self.select_files_button.pack(anchor="w", pady=(10, 10))

        self.selected_files_box = tk.Listbox(
            files_card,
            height=6,
            font=("Segoe UI", 9),
            activestyle="none",
            relief="solid",
            bd=1,
            highlightthickness=0,
        )
        self.selected_files_box.pack(fill="x")

        middle_row = ttk.Frame(content_frame, style="App.TFrame")
        middle_row.pack(fill="x", pady=(0, 12))

        summary_card = ttk.Frame(middle_row, style="Card.TFrame", padding=14)
        summary_card.pack(side="left", fill="both", expand=True)

        output_card = ttk.Frame(middle_row, style="Card.TFrame", padding=14)
        output_card.pack(side="left", fill="both", expand=True, padx=(12, 0))

        ttk.Label(summary_card, text="Resumo da seleção", style="CardTitle.TLabel").pack(anchor="w")

        self.summary_line_1 = ttk.Label(
            summary_card,
            text="Nenhum arquivo selecionado.",
            style="CardText.TLabel",
        )
        self.summary_line_1.pack(anchor="w", pady=(10, 4))

        self.summary_line_2 = ttk.Label(
            summary_card,
            text="",
            style="CardText.TLabel",
        )
        self.summary_line_2.pack(anchor="w", pady=4)

        self.summary_line_3 = ttk.Label(
            summary_card,
            text="",
            style="CardText.TLabel",
        )
        self.summary_line_3.pack(anchor="w", pady=4)

        ttk.Label(output_card, text="Pasta de saída", style="CardTitle.TLabel").pack(anchor="w")

        output_buttons_row = ttk.Frame(output_card, style="Card.TFrame")
        output_buttons_row.pack(anchor="w", pady=(10, 8))

        ttk.Button(
            output_buttons_row,
            text="Selecionar pasta",
            command=self.select_output_folder,
        ).pack(side="left")

        self.open_output_button = ttk.Button(
            output_buttons_row,
            text="Abrir pasta",
            command=self.open_output_folder,
            state="disabled",
        )
        self.open_output_button.pack(side="left", padx=(8, 0))

        self.output_label = ttk.Label(
            output_card,
            text="Nenhuma pasta selecionada.",
            style="CardText.TLabel",
        )
        self.output_label.pack(anchor="w")

        action_row = ttk.Frame(content_frame, style="App.TFrame")
        action_row.pack(fill="x", pady=(0, 12))

        action_card = ttk.Frame(action_row, style="Card.TFrame", padding=14)
        action_card.pack(fill="x")

        ttk.Label(action_card, text="Ações", style="CardTitle.TLabel").pack(anchor="w")

        buttons_row = ttk.Frame(action_card, style="Card.TFrame")
        buttons_row.pack(anchor="w", pady=(10, 8))

        self.process_button = ttk.Button(
            buttons_row,
            text="Processar",
            state="disabled",
            command=self.process_files,
            style="Primary.TButton",
        )
        self.process_button.pack(side="left")

        self.open_report_button = ttk.Button(
            buttons_row,
            text="Abrir relatório",
            state="disabled",
            command=self.open_report,
        )
        self.open_report_button.pack(side="left", padx=(8, 0))

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

    def _reset_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def log(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"• {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _update_buttons(self):
        self.open_output_button.config(state="normal" if self.output_folder else "disabled")

        report_exists = False
        if self.last_report_path:
            report_exists = Path(self.last_report_path).exists()
        else:
            report_exists = get_runtime_report_path().exists()

        self.open_report_button.config(state="normal" if report_exists else "disabled")

        if not self.output_folder or not self.selected_files:
            self.process_button.config(state="disabled")
            return

        current_mode = self.mode_var.get()

        if current_mode == "individual":
            self.process_button.config(state="normal" if self.individual_ready else "disabled")
        else:
            self.process_button.config(state="normal" if self.batch_ready else "disabled")

    def _reset_summary(self):
        self.summary_line_1.config(text="Nenhum arquivo selecionado.")
        self.summary_line_2.config(text="")
        self.summary_line_3.config(text="")

    def on_mode_change(self):
        self.selected_files = []
        self.individual_ready = False
        self.batch_ready = False

        self.selected_files_box.delete(0, "end")
        self._reset_summary()
        self._reset_log()

        if self.mode_var.get() == "individual":
            self.mode_help_label.config(
                text="No individual, você pode processar 1 ou 2 PDFs de um único colaborador."
            )
            self._set_status("Modo individual selecionado.")
        else:
            self.mode_help_label.config(
                text="No lote, apenas colaboradores com NRS e NR-37 completos serão processados."
            )
            self._set_status("Modo lote selecionado.")

        self._update_buttons()

    def select_pdf_files(self):
        current_mode = self.mode_var.get()

        if current_mode == "individual":
            title = "Selecione 1 ou 2 PDFs de um colaborador"
        else:
            title = "Selecione varios PDFs para processamento em lote"

        file_paths = filedialog.askopenfilenames(
            title=title,
            filetypes=[("Arquivos PDF", "*.pdf")],
        )

        if not file_paths:
            return

        self._reset_log()
        self.selected_files = list(file_paths)
        self.selected_files_box.delete(0, "end")

        for file_path in self.selected_files:
            self.selected_files_box.insert("end", Path(file_path).name)

        if current_mode == "individual":
            self._analyze_individual_selection()
        else:
            self._analyze_batch_selection()

        self._update_buttons()

    def _analyze_individual_selection(self):
        self.individual_ready = False

        if not self.selected_files:
            self._reset_summary()
            self._set_status("Aguardando seleção dos arquivos.")
            return

        if len(self.selected_files) > 2:
            self.summary_line_1.config(text="Seleção inválida para o modo individual.")
            self.summary_line_2.config(text="No modo individual, selecione no máximo 2 PDFs.")
            self.summary_line_3.config(text="")
            self._set_status("Ajuste a seleção dos arquivos.")
            self.log("No modo individual, selecione no máximo 2 PDFs.")
            return

        identified_files = identify_pdf_files(self.selected_files)

        unidentified_files = [item for item in identified_files if item.certificate_type is None]
        nrs_files = [item for item in identified_files if item.certificate_type == "NRS"]
        nr37_files = [item for item in identified_files if item.certificate_type == "NR37"]

        detected_names = {
            item.person_name_base
            for item in identified_files
            if item.person_name_base.strip()
        }

        collaborator_name = next(iter(detected_names)) if len(detected_names) == 1 else "-"

        self.summary_line_1.config(text=f"Colaborador: {collaborator_name}")
        self.summary_line_2.config(
            text=f"Arquivos detectados: NRS={len(nrs_files)} | NR-37={len(nr37_files)}"
        )

        if unidentified_files:
            self.summary_line_3.config(text="Ha arquivo(s) que nao puderam ser identificados.")
            self._set_status("Ajuste a seleção dos arquivos.")
            self.log("Existe arquivo que nao foi identificado como NRS ou NR-37.")
            return

        if len(detected_names) > 1:
            self.summary_line_3.config(text="Os arquivos parecem ser de colaboradores diferentes.")
            self._set_status("Ajuste a seleção dos arquivos.")
            self.log("Os arquivos selecionados parecem pertencer a pessoas diferentes.")
            return

        if len(nrs_files) > 1:
            self.summary_line_3.config(text="Existe mais de um arquivo NRS selecionado.")
            self._set_status("Ajuste a seleção dos arquivos.")
            self.log("Existe mais de um arquivo NRS selecionado.")
            return

        if len(nr37_files) > 1:
            self.summary_line_3.config(text="Existe mais de um arquivo NR-37 selecionado.")
            self._set_status("Ajuste a seleção dos arquivos.")
            self.log("Existe mais de um arquivo NR-37 selecionado.")
            return

        if len(nrs_files) == 0 and len(nr37_files) == 0:
            self.summary_line_3.config(text="Nenhum arquivo valido foi encontrado.")
            self._set_status("Ajuste a seleção dos arquivos.")
            self.log("Nenhum arquivo valido foi encontrado.")
            return

        if len(nrs_files) == 1 and len(nr37_files) == 1:
            self.summary_line_3.config(text="Seleção completa. Os dois PDFs podem ser processados.")
        elif len(nrs_files) == 1:
            self.summary_line_3.config(text="Seleção parcial. Apenas o NRS sera processado.")
        else:
            self.summary_line_3.config(text="Seleção parcial. Apenas o NR-37 sera processado.")

        self.individual_ready = True
        self._set_status("Tudo pronto para processar no modo individual.")
        self.log("Arquivos validados para o modo individual.")

    def _analyze_batch_selection(self):
        self.batch_ready = False

        if not self.selected_files:
            self._reset_summary()
            self._set_status("Aguardando seleção dos arquivos.")
            return

        grouping_result = group_pdf_files_for_batch(self.selected_files)

        processable_groups = 0
        skipped_groups = 0

        for group in grouping_result.groups.values():
            if len(group.nrs_files) == 1 and len(group.nr37_files) == 1:
                processable_groups += 1
            else:
                skipped_groups += 1

        self.summary_line_1.config(
            text=f"Grupos identificados: {len(grouping_result.groups)}"
        )
        self.summary_line_2.config(
            text=(
                f"Prontos para processar: {processable_groups} | "
                f"Nao processados na analise: {skipped_groups}"
            )
        )
        self.summary_line_3.config(
            text=f"Arquivos nao identificados: {len(grouping_result.unidentified_files)}"
        )

        self.batch_ready = len(self.selected_files) > 0
        if processable_groups > 0:
            self._set_status("Lote analisado. Ha colaboradores prontos para processar.")
        else:
            self._set_status("Lote analisado. Nenhum colaborador completo foi encontrado.")

        self.log("Analise do lote concluida.")
        self.log(f"Grupos encontrados: {len(grouping_result.groups)}")
        self.log(f"Grupos prontos: {processable_groups}")

        if skipped_groups > 0:
            self.log(f"Grupos nao processaveis nesta analise: {skipped_groups}")

        if len(grouping_result.unidentified_files) > 0:
            self.log(f"Arquivos nao identificados: {len(grouping_result.unidentified_files)}")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Selecione a pasta de saída")

        if not folder_path:
            return

        self.output_folder = folder_path
        self.output_label.config(text=self.output_folder)
        self.log("Pasta de saída selecionada com sucesso.")
        self._update_buttons()

    def open_output_folder(self):
        if not self.output_folder:
            messagebox.showwarning("Aviso", "Selecione uma pasta de saída primeiro.")
            return

        open_folder(self.output_folder)

    def open_report(self):
        report_path = self.last_report_path or str(get_runtime_report_path())

        if not Path(report_path).exists():
            messagebox.showwarning("Aviso", "Nenhum relatório foi encontrado ainda.")
            return

        open_path(report_path)

    def process_files(self):
        if not self.output_folder:
            messagebox.showwarning("Aviso", "Selecione a pasta de saída antes de processar.")
            return

        if not self.selected_files:
            messagebox.showwarning("Aviso", "Selecione os arquivos antes de processar.")
            return

        current_mode = self.mode_var.get()

        try:
            self._reset_log()
            self.process_button.config(state="disabled")

            if current_mode == "individual":
                if not self.individual_ready:
                    messagebox.showwarning("Aviso", "A seleção atual nao esta pronta para processamento.")
                    self._update_buttons()
                    return

                self._set_status("Processando no modo individual...")
                self.log("Iniciando processamento individual...")

                result = process_individual_files(
                    file_paths=self.selected_files,
                    output_folder=self.output_folder,
                    log_callback=self.log,
                )

            else:
                if not self.batch_ready:
                    messagebox.showwarning("Aviso", "Selecione arquivos para o lote.")
                    self._update_buttons()
                    return

                self._set_status("Processando no modo lote...")
                self.log("Iniciando processamento em lote...")

                result = process_batch_files(
                    file_paths=self.selected_files,
                    output_root_folder=self.output_folder,
                    log_callback=self.log,
                )

            self.last_report_path = result.report_path
            self._update_buttons()

            if result.success:
                self._set_status("Processamento concluído com sucesso.")
                self.log(result.message)
                messagebox.showinfo("Concluído", result.message)
            else:
                self._set_status("Processamento concluído com observações.")
                self.log(result.message)
                messagebox.showwarning("Atenção", result.message)

        except Exception as error:
            self.log(str(error))
            self._set_status("Ocorreu um problema no processamento.")
            messagebox.showerror("Erro", str(error))
            self._update_buttons()