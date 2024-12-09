import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox


class ConfiguracoesWidget(QWidget):
    CONFIG_FILE = "config.json"  # Arquivo de configuração

    def __init__(self, current_theme, apply_theme_callback):
        super().__init__()
        self.current_theme = current_theme
        self.apply_theme_callback = apply_theme_callback

        layout = QVBoxLayout(self)

        # Label que indica o tema atual
        self.theme_label = QLabel("Tema Atual: Claro" if self.current_theme == "light" else "Tema Atual: Escuro")
        layout.addWidget(self.theme_label)

        # Botão para alternar o tema
        self.theme_toggle = QPushButton("Alternar para Tema Escuro" if self.current_theme == "light" else "Alternar para Tema Claro")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setChecked(self.current_theme == "dark")
        self.theme_toggle.clicked.connect(self.toggle_theme)

        layout.addWidget(self.theme_toggle)

        # Botão para salvar configurações
        save_button = QPushButton("Salvar Configurações")
        save_button.clicked.connect(self.save_configurations)
        layout.addWidget(save_button)

        layout.addStretch()

    def toggle_theme(self):
        # Alterna entre os temas claro e escuro
        self.current_theme = "dark" if self.theme_toggle.isChecked() else "light"
        self.theme_label.setText("Tema Atual: Escuro" if self.current_theme == "dark" else "Tema Atual: Claro")
        self.theme_toggle.setText("Alternar para Tema Claro" if self.current_theme == "dark" else "Alternar para Tema Escuro")
        self.apply_theme_callback(self.current_theme)

    def save_configurations(self):
        # Salva a configuração atual no arquivo JSON
        config = {
            "theme": self.current_theme
        }
        try:
            with open(self.CONFIG_FILE, "w") as file:
                json.dump(config, file)
            QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {e}")

    @staticmethod
    def load_configurations():
        # Carrega as configurações do arquivo JSON, se existir
        try:
            with open(ConfiguracoesWidget.CONFIG_FILE, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"theme": "light"}  # Valor padrão
