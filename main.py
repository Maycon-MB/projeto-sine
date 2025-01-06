import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from database.connection import DatabaseConnection
from gui.configuracoes import ConfiguracoesWidget
from gui.cadastro import CadastroWidget
from gui.consulta import ConsultaWidget
from gui.notificacoes import TelaNotificacoes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicação com Sidebar")
        self.resize(1200, 600)

        # Diretório base do projeto
        self.base_dir = Path(__file__).resolve().parent
        self.icons_dir = self.base_dir / "assets" / "icons"

        # Conexão com o banco de dados
        self.db_connection = DatabaseConnection(
            dbname="projeto_sine",
            user="postgres",
            password="admin",
            host="localhost"
        )

        # Carregar configurações salvas
        config = ConfiguracoesWidget.load_configurations()
        self.current_theme = config.get("theme", "light")  # Defina antes de usá-lo

        # Configuração do widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barra superior
        self.top_bar = QWidget()
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(10, 5, 10, 5)
        self.top_bar_layout.setSpacing(10)
        self.top_bar.setStyleSheet("background-color: #f0f0f0;")

        # Botão de notificações
        self.notification_button = QPushButton()
        self.notification_button.setIcon(QIcon("icone_notificacao.png"))  # Substitua pelo ícone desejado
        self.notification_button.setToolTip("Notificações")
        self.notification_button.clicked.connect(self.abrir_tela_notificacoes)
        self.top_bar_layout.addWidget(self.notification_button)
        main_layout.addWidget(self.top_bar)

        # Layout principal (barra lateral + conteúdo)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar.setStyleSheet("background-color: #191970;")
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(10)

        # Botões da Sidebar
        self.buttons = {}
        self.button_info = {
            "Home": "home-icon",
            "Cadastrar Currículo": "register-icon",
            "Consultar Currículos": "search-icon",
            "Configurações": "settings-icon",
            "Sair": "exit-icon"
        }

        for name, icon_base in self.button_info.items():
            btn = QPushButton(name)
            # Use QIcon para associar o ícone diretamente ao botão
            icon_path = self._get_icon_path(icon_base)
            icon = QIcon(icon_path)  # Cria um QIcon a partir do SVG
            btn.setIcon(icon)  # Define o ícone diretamente no botão
            btn.setIconSize(QSize(24, 24))  # Define o tamanho do ícone
            btn.setStyleSheet(self._button_stylesheet())
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, n=name: self._navigate(n))
            self.sidebar_layout.addWidget(btn)
            self.buttons[name] = btn  # Salva o botão para atualizações futuras

        self.sidebar_layout.addStretch()
        content_layout.addWidget(self.sidebar)

        # Área de conteúdo principal
        self.content_area = QStackedWidget()
        self.content_area.addWidget(QLabel("Bem-vindo ao sistema!"))

        self.cadastro_widget = CadastroWidget()
        self.content_area.addWidget(self.cadastro_widget)

        self.consulta_widget = ConsultaWidget(self.db_connection)
        self.content_area.addWidget(self.consulta_widget)

        self.configuracoes_widget = ConfiguracoesWidget(self.current_theme, self.apply_theme)
        self.content_area.addWidget(self.configuracoes_widget)

        content_layout.addWidget(self.content_area, stretch=1)
        main_layout.addLayout(content_layout)

        self._navigate("Home")

        # Aplica o tema salvo
        self.current_theme = "light"
        self.apply_theme(self.current_theme)

    def _get_icon_path(self, icon_base):
        """Constrói o caminho para o ícone SVG sem considerar o tema."""
        return str(self.icons_dir / f"{icon_base}.svg")

    def _navigate(self, screen_name):
        for name, btn in self.buttons.items():
            btn.setChecked(name == screen_name)

        if screen_name == "Home":
            self.content_area.setCurrentIndex(0)
        elif screen_name == "Cadastrar Currículo":
            self.content_area.setCurrentIndex(1)
        elif screen_name == "Consultar Currículos":
            self.content_area.setCurrentIndex(2)
        elif screen_name == "Configurações":
            self.content_area.setCurrentIndex(3)
        elif screen_name == "Sair":
            QApplication.quit()

    def apply_theme(self, theme):
        self.current_theme = theme
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; }
                QWidget { background-color: #1E1E1E; color: white; }
                QPushButton { background-color: #333; color: white; }
                QPushButton:hover { background-color: #555; }
                QPushButton:checked { background-color: #0073CF; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: white; }
                QWidget { background-color: #f0f0f0; color: black; }
                QPushButton { background-color: transparent; color: black; }
                QPushButton:hover { background-color: #dcdcdc; }
                QPushButton:checked { background-color: #0056A1; color: white; }
            """)

    def _button_stylesheet(self):
        return """
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #367dba;
            }
            QPushButton:checked {
                background-color: #0056A1;
                color: white;
            }
        """

    def abrir_tela_notificacoes(self):
        notificacoes_tela = TelaNotificacoes(self.db_connection)
        notificacoes_tela.show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
