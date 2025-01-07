# main.py

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIcon
from gui.configuracoes import ConfiguracoesWidget
from gui.cadastro import CadastroWidget
from gui.consulta import ConsultaWidget
from gui.notificacoes import TelaNotificacoes
from database.connection import DatabaseConnection
from database.models import UsuarioModel

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

        # Inicializar modelos
        self.usuario_model = UsuarioModel(self.db_connection)

        # Carregar configurações salvas
        config = ConfiguracoesWidget.load_configurations()
        self.current_theme = config.get("theme", "light")

        # Configuração do widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar.setStyleSheet("background-color: #191970;")
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)

        # Botões da Sidebar
        self.buttons = {}
        self.button_info = {
            "Home": "home-icon",
            "Cadastrar Currículo": "register-icon",
            "Consultar Currículos": "search-icon",
            "Configurações": "settings-icon",
        }

        for name, icon_base in self.button_info.items():
            btn = QPushButton(name)
            btn.setIcon(QIcon(self._get_icon_path(icon_base)))
            btn.setIconSize(QSize(24, 24))
            btn.setStyleSheet(self._button_stylesheet())
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda _, n=name: self._navigate(n))
            self.sidebar_layout.addWidget(btn)
            self.buttons[name] = btn

        # Adiciona espaço vazio antes do botão "Sair"
        self.sidebar_layout.addStretch()

        # Botão "Sair"
        self.exit_button = QPushButton("Sair")
        self.exit_button.setIcon(QIcon(self._get_icon_path("exit-icon")))
        self.exit_button.setIconSize(QSize(24, 24))
        self.exit_button.setStyleSheet(self._button_stylesheet())
        self.exit_button.clicked.connect(self._confirm_exit)
        self.sidebar_layout.addWidget(self.exit_button)

        main_layout.addWidget(self.sidebar)

        # Corpo principal
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Top Bar
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(50)
        self.top_bar.setStyleSheet("background-color: #191970;")
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.top_bar_layout.setSpacing(10)

        # Botão de notificações na top bar
        self.notification_button = QPushButton()
        self.notification_button.setIcon(QIcon(self._get_icon_path("notification-icon")))
        self.notification_button.setIconSize(QSize(24, 24))
        self.notification_button.setFixedSize(40, 40)
        self.notification_button.setStyleSheet("background-color: transparent; border: none;")
        self.notification_button.clicked.connect(self._show_notifications)

        # Label para o contador de notificações
        self.notification_count_label = QLabel("0")
        self.notification_count_label.setFixedSize(20, 20)
        self.notification_count_label.setAlignment(Qt.AlignCenter)
        self.notification_count_label.setStyleSheet("""
            background-color: red;
            color: white;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
        """)
        self.notification_count_label.move(30, -5)  # Posição no canto superior direito

        # Layout do botão de notificações
        notification_layout = QWidget(self.notification_button)
        notification_layout.setGeometry(0, 0, 40, 40)  # Posicionamento interno
        notification_layout_layout = QVBoxLayout(notification_layout)
        notification_layout_layout.setContentsMargins(20, 5, 0, 0)
        notification_layout_layout.addWidget(self.notification_count_label)

        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.notification_button)

        body_layout.addWidget(self.top_bar)

        # Área de conteúdo principal
        self.content_area = QStackedWidget()
        self.content_area.addWidget(QLabel("Bem-vindo ao sistema!"))

        self.cadastro_widget = CadastroWidget()
        self.content_area.addWidget(self.cadastro_widget)

        self.consulta_widget = ConsultaWidget(self.db_connection)
        self.content_area.addWidget(self.consulta_widget)

        self.configuracoes_widget = ConfiguracoesWidget(self.current_theme, self.apply_theme)
        self.content_area.addWidget(self.configuracoes_widget)

        body_layout.addWidget(self.content_area, stretch=1)

        main_layout.addLayout(body_layout)

        self._navigate("Home")
        self.apply_theme(self.current_theme)

        # Atualiza o contador de notificações periodicamente
        self._update_notification_count()
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self._update_notification_count)
        self.notification_timer.start(5000)  # Atualiza a cada 5 segundos

    def _show_notifications(self):
        """
        Abre a tela de notificações como um diálogo modal.
        """
        try:
            notificacoes = TelaNotificacoes(self.usuario_model)  # Passa o UsuarioModel
            notificacoes.exec()  # Usa exec() corretamente com QDialog
            self._update_notification_count()  # Atualiza o contador após interações
        except Exception as e:
            print(f"Erro ao mostrar notificações: {e}")

    def _update_notification_count(self):
        """
        Atualiza o contador de notificações pendentes.
        """
        try:
            count = len(self.usuario_model.listar_aprovacoes_pendentes())
            self.notification_count_label.setText(str(count))
            self.notification_count_label.setVisible(count > 0)
        except Exception as e:
            print(f"Erro ao atualizar contador de notificações: {e}")

    def _confirm_exit(self):
        response = QMessageBox.question(
            self, "Confirmação", "Deseja realmente sair?",
            QMessageBox.Yes | QMessageBox.No
        )
        if response == QMessageBox.Yes:
            QApplication.quit()

    def _get_icon_path(self, icon_base):
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
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                border: none;
                background-color: transparent;
                outline: none;
            }
            QPushButton:hover {
                background-color: #367dba;
            }
            QPushButton:checked {
                background-color: #0056A1;
                color: white;
            }
        """


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
