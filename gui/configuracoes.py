import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QComboBox, QSpinBox
)


class ConfiguracoesWidget(QWidget):
    CONFIG_FILE = "config.json"  # Arquivo de configuração

    def __init__(self, current_theme, apply_theme_callback, main_window):
        super().__init__()
        self.main_window = main_window  # Recebe a referência para o QMainWindow

        # Carrega as configurações salvas
        saved_config = self.load_configurations()

        # Define os valores iniciais a partir das configurações salvas
        self.current_theme = saved_config.get("theme", "light")
        self.apply_theme_callback = apply_theme_callback
        self.font_family = saved_config.get("font_family", "Arial")
        self.font_size = saved_config.get("font_size", 12)
        self.resolution = saved_config.get("resolution", "1200x600")

        layout = QVBoxLayout(self)

        # Tema
        self.theme_label = QLabel("Tema Atual: Claro" if self.current_theme == "light" else "Tema Atual: Escuro")
        layout.addWidget(self.theme_label)

        self.theme_toggle = QPushButton("Alternar para Tema Escuro" if self.current_theme == "light" else "Alternar para Tema Claro")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setChecked(self.current_theme == "dark")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle)

        # Configuração de Fonte
        font_label = QLabel(f"Fonte Atual: {self.font_family}")
        layout.addWidget(font_label)

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Verdana", "Tahoma", "Courier New", "Times New Roman"])
        self.font_combo.setCurrentText(self.font_family)
        self.font_combo.currentTextChanged.connect(self.update_font_family)
        layout.addWidget(self.font_combo)

        # Tamanho da Fonte
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 48)
        self.font_size_spinbox.setValue(self.font_size)
        self.font_size_spinbox.valueChanged.connect(self.update_font_size)
        layout.addWidget(QLabel("Tamanho da Fonte:"))
        layout.addWidget(self.font_size_spinbox)

        # Resolução Padrão da Tela
        self.resolution_label = QLabel(f"Resolução Atual: {self.resolution}")
        layout.addWidget(self.resolution_label)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "800x600",
            "1024x768",
            "1280x720",
            "1366x768",
            "1600x900",
            "1920x1080"
        ])
        self.resolution_combo.setCurrentText(self.resolution)
        self.resolution_combo.currentTextChanged.connect(self.apply_resolution)
        layout.addWidget(self.resolution_combo)

        # Restaurar Configurações
        reset_button = QPushButton("Restaurar Configurações Padrão")
        reset_button.clicked.connect(self.reset_to_defaults)
        layout.addWidget(reset_button)

        # Salvar Configurações
        save_button = QPushButton("Salvar Configurações")
        save_button.clicked.connect(self.save_configurations)
        layout.addWidget(save_button)

        layout.addStretch()

        # Aplica as configurações ao inicializar
        self.apply_font_settings()
        self.apply_resolution(self.resolution)
        self.apply_theme_callback(self.current_theme)

    def toggle_theme(self):
        # Alterna entre os temas claro e escuro
        self.current_theme = "dark" if self.theme_toggle.isChecked() else "light"
        self.theme_label.setText("Tema Atual: Escuro" if self.current_theme == "dark" else "Tema Atual: Claro")
        self.theme_toggle.setText("Alternar para Tema Claro" if self.current_theme == "dark" else "Alternar para Tema Escuro")
        self.apply_theme_callback(self.current_theme)

    def update_font_family(self, font):
        # Atualiza a família da fonte
        self.font_family = font
        self.apply_font_settings()

    def update_font_size(self, value):
        # Atualiza o tamanho da fonte
        self.font_size = value
        self.apply_font_settings()

    def apply_font_settings(self):
        # Aplica as configurações de fonte na interface
        self.setStyleSheet(f"* {{ font-family: {self.font_family}; font-size: {self.font_size}px; }}")

    def apply_resolution(self, resolution):
        """
        Redimensiona a janela principal com base na resolução selecionada.
        """
        self.resolution = resolution
        if self.main_window:  # Usa a referência direta ao MainWindow
            try:
                width, height = map(int, resolution.split("x"))
                self.main_window.resize(width, height)
                self.resolution_label.setText(f"Resolução Atual: {resolution}")
            except ValueError:
                QMessageBox.critical(self, "Erro", f"Resolução inválida: {resolution}")

    def reset_to_defaults(self):
        # Restaura as configurações para os valores padrão
        self.current_theme = "light"
        self.theme_label.setText("Tema Atual: Claro")
        self.theme_toggle.setChecked(False)
        self.theme_toggle.setText("Alternar para Tema Escuro")
        self.font_family = "Arial"
        self.font_combo.setCurrentText("Arial")
        self.font_size = 12
        self.font_size_spinbox.setValue(12)
        self.resolution_combo.setCurrentText("1200x600")
        self.apply_resolution("1200x600")
        self.apply_font_settings()
        self.apply_theme_callback(self.current_theme)
        QMessageBox.information(self, "Configurações", "Configurações restauradas para os valores padrão!")

    def save_configurations(self):
        # Salva a configuração atual no arquivo JSON
        config = {
            "theme": self.current_theme,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "resolution": self.resolution
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
            return {
                "theme": "light",
                "font_family": "Arial",
                "font_size": 12,
                "resolution": "1200x600"
            }  # Valores padrão
