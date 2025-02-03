import os, logging
from pathlib import Path
from PySide6.QtSvgWidgets import QSvgWidget
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
from gui.dashboard import DashboardWidget
from database.connection import DatabaseConnection
from models.usuario_model import UsuarioModel
from models.notificacao_model import NotificacaoModel
from models.curriculo_model import CurriculoModel  # 🔥 Importando o CurriculoModel



class MainWindow(QMainWindow):
    def __init__(self, db_connection, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id  # Define o ID do usuário logado
        self.setWindowTitle("Aplicação com Sidebar")

        # Carregar configurações salvas
        config = ConfiguracoesWidget.load_configurations()
        self.current_theme = config.get("theme", "light")

        # Definir uma resolução padrão ou ajustar a janela de acordo com a tela disponível
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        width, height = screen_geometry.width(), screen_geometry.height()

        # Aplica a resolução ajustada à área disponível
        self.resize(width, height)

        # Define um tamanho mínimo de janela
        self.setMinimumSize(800, 600)

        # Garantir que a janela sempre será maximizada ao iniciar
        self.showMaximized()


        # Diretório base do projeto
        self.base_dir = Path(__file__).resolve().parent
        self.icons_dir = self.base_dir / "assets" / "icons"

        # Inicializar modelo de usuários
        self.db_connection = db_connection
        self.usuario_model = UsuarioModel(self.db_connection)

        # Inicializar modelo de aprovações
        self.db_connection = db_connection
        self.notificacao_model = NotificacaoModel(self.db_connection)

        self.curriculo_model = CurriculoModel(self.db_connection)  # ✅ Criando instância correta


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
        self.notification_count_label.move(self.notification_button.width() - 20, 0)  # Posição fixa relativa ao botão
        self.notification_count_label.setVisible(False)  # Ocultar inicialmente

        self.top_bar_layout.addStretch()
        self.top_bar_layout.addSpacing(10)  # Espaçamento extra antes do botão
        self.top_bar_layout.addWidget(self.notification_button)

        body_layout.addWidget(self.top_bar)

        # ✅ Inicializar a área de conteúdo principal
        self.content_area = QStackedWidget()

        # Adiciona a tela de Dashboard como "Home"
        self.dashboard_widget = DashboardWidget(
            self.usuario_model,
            self.curriculo_model,
            self._navigate,
            usuario_logado['tipo_usuario'],  # Tipo do usuário
            usuario_logado['id'],  # Passa o ID do usuário logado
            usuario_logado.get('cidade_admin')  # Cidade do admin (se aplicável)
        )
        self.content_area.addWidget(self.dashboard_widget)

        # Adiciona os demais widgets
        self.cadastro_widget = CadastroWidget(self.db_connection)
        self.content_area.addWidget(self.cadastro_widget)

        self.consulta_widget = ConsultaWidget(self.db_connection)
        self.content_area.addWidget(self.consulta_widget)

        # Passa a referência de MainWindow ao ConfiguracoesWidget
        self.configuracoes_widget = ConfiguracoesWidget(self)
        self.configuracoes_widget.apply_theme(self.current_theme)  # Aplica o tema na inicialização
        self.content_area.addWidget(self.configuracoes_widget)

        # ✅ Adiciona a content_area ao layout
        body_layout.addWidget(self.content_area, stretch=1)


        main_layout.addLayout(body_layout)

        self._navigate("Página Inicial")

        # Atualiza o contador de notificações periodicamente
        self._update_notification_count()
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self._update_notification_count)
        self.notification_timer.start(5000)

    def _show_notifications(self):
        try:
            notificacoes = TelaNotificacoes(self.notificacao_model, self.usuario_id, usuario_logado['tipo_usuario'])
            notificacoes.exec()
            self._update_notification_count()
        except Exception as e:
            logging.error(f"Erro ao mostrar notificações: {e}")

    def _update_notification_count(self):
        try:
            notificacoes = self.notificacao_model.listar_aprovacoes_pendentes(tipo_usuario=usuario_logado['tipo_usuario'], usuario_id=self.usuario_id)
            count = len(notificacoes)
            self.notification_count_label.setText(str(count))
            self.notification_count_label.setVisible(count > 0)
        except Exception as e:
            logging.error(f"Erro ao atualizar contador de notificações: {e}")

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
            self.content_area.setCurrentWidget(self.dashboard_widget)  # ✅ Dashboard
        elif screen_name == "Cadastrar Currículo":
            self.content_area.setCurrentWidget(self.cadastro_widget)
        elif screen_name == "Consultar Currículos":
            self.content_area.setCurrentWidget(self.consulta_widget)
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
        window.show()
        app.exec()
