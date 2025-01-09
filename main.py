import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon
from gui.configuracoes import ConfiguracoesWidget
from gui.cadastrar_curriculo import CadastroWidget
from gui.consultar_curriculo import ConsultaWidget
from gui.notificacoes import TelaNotificacoes
from gui.login_cadastro import LoginCadastroDialog  # Tela de login/cadastro
from database.connection import DatabaseConnection
from database.models import UsuarioModel


class MainWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.setWindowTitle("Aplicação com Sidebar")

        # Carregar configurações salvas
        config = ConfiguracoesWidget.load_configurations()
        self.current_theme = config.get("theme", "light")
        self.resolution = config.get("resolution", "1200x600")

        # Aplicar resolução salva
        width, height = map(int, self.resolution.split("x"))
        self.resize(width, height)

        # Diretório base do projeto
        self.base_dir = Path(__file__).resolve().parent
        self.icons_dir = self.base_dir / "assets" / "icons"

        # Inicializar modelo de usuários
        self.db_connection = db_connection
        self.usuario_model = UsuarioModel(self.db_connection)

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
        self.notification_button.setStyleSheet("background-color: transparent; border: none; position: relative;")
        self.notification_button.clicked.connect(self._show_notifications)

        # Label para o contador de notificações
        self.notification_count_label = QLabel("0", self.notification_button)  # Associada ao botão
        self.notification_count_label.setFixedSize(20, 20)
        self.notification_count_label.setAlignment(Qt.AlignCenter)
        self.notification_count_label.setStyleSheet("""
            background-color: red;
            color: white;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
            position: absolute;
        """)
        self.notification_count_label.move(self.notification_button.width() - 15, 0)  # Posição fixa relativa ao botão
        self.notification_count_label.setVisible(False)  # Ocultar inicialmente

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

        # Passa a referência de MainWindow ao ConfiguracoesWidget
        self.configuracoes_widget = ConfiguracoesWidget(self.current_theme, self.apply_theme, self)
        self.content_area.addWidget(self.configuracoes_widget)

        body_layout.addWidget(self.content_area, stretch=1)

        main_layout.addLayout(body_layout)

        self._navigate("Home")
        self.apply_theme(self.current_theme)

        # Atualiza o contador de notificações periodicamente
        self._update_notification_count()
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self._update_notification_count)
        self.notification_timer.start(5000)

    def _show_notifications(self):
        try:
            notificacoes = TelaNotificacoes(self.usuario_model)
            notificacoes.exec()
            self._update_notification_count()
        except Exception as e:
            print(f"Erro ao mostrar notificações: {e}")

    def _update_notification_count(self):
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
                QPushButton {
                    background-color: #333; 
                    color: white; 
                    border-radius: 5px; 
                    padding: 10px;
                }
                QPushButton:hover { background-color: #555; }
                QPushButton:checked { background-color: #0073CF; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: white; }
                QWidget { background-color: #f0f0f0; color: black; }
                QPushButton {
                    background-color: #e0e0e0; 
                    color: black; 
                    border-radius: 5px; 
                    padding: 10px;
                }
                QPushButton:hover { background-color: #dcdcdc; }
                QPushButton:checked { background-color: #0073CF; color: white; }
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

    # Inicializa a conexão com o banco
    db_connection = DatabaseConnection(
        dbname="projeto_sine",
        user="postgres",
        password="admin",
        host="localhost"
    )
    usuario_model = UsuarioModel(db_connection)

    # Exibe a tela de login/cadastro antes da janela principal
    login_dialog = LoginCadastroDialog(usuario_model)
    if login_dialog.exec() == QDialog.Accepted:
        # Usuário autenticado, inicia a janela principal
        window = MainWindow(db_connection)
        window.show()
        app.exec()
