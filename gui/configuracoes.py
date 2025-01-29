import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QComboBox, QSpinBox, QApplication
)


class ConfiguracoesWidget(QWidget):
    CONFIG_FILE = "config.json"  # Arquivo de configuração

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Recebe a referência para o QMainWindow

        # Carrega as configurações salvas
        saved_config = self.load_configurations()

        # Define os valores iniciais a partir das configurações salvas
        self.current_theme = saved_config.get("theme", "light")
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
            "800x600", "1024x768", "1280x720", "1366x768", "1600x900", "1920x1080", "2560x1440", "3840x2160"
        ])
        self.resolution_combo.setCurrentText(self.resolution)
        self.resolution_combo.currentTextChanged.connect(self.apply_resolution)
        layout.addWidget(self.resolution_combo)

        # Layout horizontal para os botões
        button_layout = QHBoxLayout()

        # Salvar Configurações (Agora está antes do Resetar)
        save_button = QPushButton("Salvar")
        save_button.setFixedSize(100, 30)  # Define tamanho menor
        save_button.clicked.connect(self.save_configurations)
        button_layout.addWidget(save_button)

        # Restaurar Configurações
        reset_button = QPushButton("Resetar Configurações")
        reset_button.setFixedSize(150, 30)  # Define tamanho menor
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)

        # Adiciona o layout horizontal ao layout principal
        layout.addLayout(button_layout)

        layout.addStretch()

        # Aplica as configurações ao inicializar
        self.apply_font_settings()
        self.apply_resolution(self.resolution)
        self.apply_theme(self.current_theme)

    def toggle_theme(self):
        self.current_theme = "dark" if self.theme_toggle.isChecked() else "light"
        self.theme_label.setText("Tema Atual: Escuro" if self.current_theme == "dark" else "Tema Atual: Claro")
        self.theme_toggle.setText("Alternar para Tema Claro" if self.current_theme == "dark" else "Alternar para Tema Escuro")
        self.apply_theme(self.current_theme)  # Chama diretamente a função

    def update_font_family(self, font):
        self.font_family = font
        self.apply_font_settings()

    def update_font_size(self, value):
        self.font_size = value
        self.apply_font_settings()
        self.apply_theme(self.current_theme)  # Garante que o tema atual seja mantido

    def apply_font_settings(self):
        QApplication.instance().setStyleSheet(f"* {{ font-family: {self.font_family}; font-size: {self.font_size}px; }}")

    def apply_resolution(self, resolution):
        self.resolution = resolution
        if self.main_window:
            try:
                width, height = map(int, resolution.split("x"))
                self.main_window.resize(width, height)
                self.resolution_label.setText(f"Resolução Atual: {resolution}")
            except ValueError:
                QMessageBox.critical(self, "Erro", f"Resolução inválida: {resolution}")

    def reset_to_defaults(self):
        self.current_theme = "light"
        self.theme_label.setText("Tema Atual: Claro")
        self.theme_toggle.setChecked(False)
        self.theme_toggle.setText("Alternar para Tema Escuro")
        self.font_family = "Arial"
        self.font_combo.setCurrentText("Arial")
        self.font_size = 14
        self.font_size_spinbox.setValue(14)
        self.resolution_combo.setCurrentText("1200x600")
        self.apply_resolution("1200x600")
        self.apply_font_settings()
        self.apply_theme(self.current_theme)
        QMessageBox.information(self, "Configurações", "Configurações restauradas para os valores padrão!")

    def save_configurations(self):
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
        try:
            with open(ConfiguracoesWidget.CONFIG_FILE, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"theme": "light", "font_family": "Arial", "font_size": 14, "resolution": "1200x600"}

    def apply_theme(self, theme):
        self.current_theme = theme
        QApplication.instance().setStyleSheet("")  # Limpa estilos antigos

        qss = """
            QDialog, QMainWindow { background-color: #c2dafc; }
            QLabel { font-size: 14px; color: #333333; }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #b0c4de;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                color: #000000;
            }

            QCheckBox {
                font-size: 14px;
                color: #333333; 
            }

            QSpinBox { 
                background-color: #ffffff; 
                color: #000000;
                font-size: 14px;
            }
                
            QLineEdit:focus, QComboBox:focus { 
                border: 2px solid #0078d7; 
            }

            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #b0c4de;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
                font-size: 14px;
            }
            
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover { background-color: #005499; }
            QPushButton:disabled {
                background-color: #c0c0c0;
                color: #808080;
            }
            
            QTableWidget, QTableView {
                background-color: #ffffff;
                border: 1px solid #b0c4de;
                gridline-color: #b0c4de;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
                color: #000000;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #0078d7;
                color: white;
                padding: 5px;
                border: 1px solid #b0c4de;
                font-size: 14px;
            }
        """ if theme == "light" else """
            QMainWindow { background-color: #121212; }
            QWidget { background-color: #1E1E1E; color: white; font-size: 14px; }

            QLabel { font-size: 14px; color: white; }
            
            QLineEdit, QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }

            QCheckBox {
                font-size: 14px;
                color: white; 
            }

            QSpinBox { 
                background-color: #333333; 
                color: white;
                font-size: 14px;
            }

            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #005499; }
            QPushButton:checked { background-color: #0078d7; }

            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #0078d7;
                selection-color: white;
                font-size: 14px;
            }
            
            QTableWidget, QTableView {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                gridline-color: #555555;
                selection-background-color: #0078d7;
                selection-color: white;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #044a82;
                color: white;
                padding: 5px;
                border: 1px solid #555555;
                font-size: 14px;
            }
        """

        QApplication.instance().setStyleSheet(qss)
