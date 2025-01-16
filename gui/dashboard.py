# gui/dashboard.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QSize, Qt

class DashboardWidget(QWidget):
    def __init__(self, usuario_model, aprovacao_model, navigate_callback):
        super().__init__()
        self.usuario_model = usuario_model
        self.aprovacao_model = aprovacao_model
        self.navigate_callback = navigate_callback

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("📊 Painel de Controle")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Indicadores rápidos
        indicators_layout = QHBoxLayout()

        total_curriculos = self._create_info_card("Total de Currículos", self.usuario_model.total_curriculos())
        pendentes = self._create_info_card("Aprovações Pendentes", self.aprovacao_model.total_pendentes())
        notificacoes = self._create_info_card("Notificações", self.aprovacao_model.total_notificacoes())

        indicators_layout.addWidget(total_curriculos)
        indicators_layout.addWidget(pendentes)
        indicators_layout.addWidget(notificacoes)

        layout.addLayout(indicators_layout)

        # Botões de Acesso Rápido
        botoes_layout = QHBoxLayout()

        btn_cadastrar = QPushButton("Cadastrar Currículo")
        btn_cadastrar.setIcon(QIcon("assets/icons/register-icon.svg"))
        btn_cadastrar.setIconSize(QSize(32, 32))
        btn_cadastrar.clicked.connect(lambda: self.navigate_callback("Cadastrar Currículo"))

        btn_consultar = QPushButton("Consultar Currículos")
        btn_consultar.setIcon(QIcon("assets/icons/search-icon.svg"))
        btn_consultar.setIconSize(QSize(32, 32))
        btn_consultar.clicked.connect(lambda: self.navigate_callback("Consultar Currículos"))

        botoes_layout.addWidget(btn_cadastrar)
        botoes_layout.addWidget(btn_consultar)

        layout.addLayout(botoes_layout)
        self.setLayout(layout)

    def _create_info_card(self, title, value):
        card = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))

        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setStyleSheet("color: #0056A1;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        return card
