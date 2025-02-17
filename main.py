from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QMessageBox, QDialog
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from gui.configuracoes import ConfiguracoesWidget
from gui.cadastrar_curriculo import CadastroWidget
from gui.consultar_curriculo import ConsultaWidget
from gui.login_cadastro import LoginCadastroDialog  # Tela de login/cadastro
from gui.dashboard import DashboardWidget
from gui.cadastrar_funcao import CadastrarFuncaoWidget
from database.connection import DatabaseConnection
from models.usuario_model import UsuarioModel
from models.curriculo_model import CurriculoModel  # 🔥 Importando o CurriculoModel

class MainWindow(QMainWindow):
    def __init__(self, db_connection, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id  # Define o ID do usuário logado
        self.setWindowTitle("Aplicação com Sidebar")

        # Carregar configurações salvas
        config = ConfiguracoesWidget.load_configurations()
        self.current_theme = config.get("theme", "light")

        # Diretório base do projeto
        self.base_dir = Path(__file__).resolve().parent
        self.icons_dir = self.base_dir / "assets" / "icons"

        # Inicializar modelos
        self.db_connection = db_connection
        self.usuario_model = UsuarioModel(self.db_connection)
        self.curriculo_model = CurriculoModel(self.db_connection)

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
            "Cadastrar Função": "job-icon",  # ✅ Adicionando o botão para a nova tela
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

        # Inicializar a área de conteúdo principal
        self.content_area = QStackedWidget()

        # Adiciona a tela de Dashboard como "Home"
        self.dashboard_widget = DashboardWidget(
            self.usuario_model,
            self.curriculo_model,
            self._navigate,
            usuario_id  # Passa o ID do usuário logado
        )
        self.content_area.addWidget(self.dashboard_widget)

        # Adiciona os demais widgets
        self.cadastro_widget = CadastroWidget(self.db_connection)
        self.content_area.addWidget(self.cadastro_widget)

        self.consulta_widget = ConsultaWidget(self.db_connection)
        self.content_area.addWidget(self.consulta_widget)

        # Adicionando a nova tela de Cadastrar Função
        self.cadastrar_funcao_widget = CadastrarFuncaoWidget(self.db_connection)
        self.content_area.addWidget(self.cadastrar_funcao_widget)

        # Passa a referência de MainWindow ao ConfiguracoesWidget
        self.configuracoes_widget = ConfiguracoesWidget(self)
        self.configuracoes_widget.apply_theme(self.current_theme)  # Aplica o tema na inicialização
        self.content_area.addWidget(self.configuracoes_widget)

        # Adiciona a content_area ao layout
        body_layout.addWidget(self.content_area, stretch=1)

        main_layout.addLayout(body_layout)

        self._navigate("Home")

    def _confirm_exit(self):
        response = QMessageBox.question(
            self, "Confirmação", "Deseja realmente sair?",
            QMessageBox.Yes | QMessageBox.No
        )
        if response == QMessageBox.Yes:
            QApplication.quit()

    def _get_icon_path(self, icon_base):
        icon_path = self.icons_dir / f"{icon_base}.svg"
        if not icon_path.exists():
            print(f"Ícone não encontrado: {icon_path}")
        return str(icon_path)

    def _navigate(self, screen_name):
        for name, btn in self.buttons.items():
            btn.setChecked(name == screen_name)

        if screen_name == "Home":
            self.content_area.setCurrentWidget(self.dashboard_widget)
        elif screen_name == "Cadastrar Currículo":
            self.content_area.setCurrentWidget(self.cadastro_widget)
        elif screen_name == "Consultar Currículos":
            self.content_area.setCurrentWidget(self.consulta_widget)
        elif screen_name == "Cadastrar Função":  # ✅ Adicionada a navegação para a nova tela
            self.content_area.setCurrentWidget(self.cadastrar_funcao_widget)
        elif screen_name == "Configurações":
            self.content_area.setCurrentWidget(self.configuracoes_widget)

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
        password="teste",
        host="192.168.1.213"
    )
    usuario_model = UsuarioModel(db_connection)

    # Exibe a tela de login/cadastro antes da janela principal
    login_dialog = LoginCadastroDialog(usuario_model)
    if login_dialog.exec() == QDialog.Accepted:
        usuario_logado = login_dialog.usuario_logado  # Supondo que armazene o usuário logado
        window = MainWindow(db_connection, usuario_logado['id'])
        window.showMaximized()  # Isso abre a janela maximizada
        app.exec()

