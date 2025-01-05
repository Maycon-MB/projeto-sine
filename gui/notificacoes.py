from PySide6.QtWidgets import QToolButton, QMenu, QAction, QLabel, QVBoxLayout, QMessageBox, QWidget, QListWidget, QPushButton

class NotificacoesWidget(QWidget):
    def __init__(self, usuario_model):
        super().__init__()
        self.usuario_model = usuario_model
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Label para mostrar notificações pendentes
        self.label = QLabel("Notificações:")
        layout.addWidget(self.label)

        self.notification_list = QListWidget()
        layout.addWidget(self.notification_list)

        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.carregar_notificacoes)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.carregar_notificacoes()

    def carregar_notificacoes(self):
        try:
            notificacoes = self.usuario_model.listar_aprovacoes_pendentes()
            self.notification_list.clear()
            for notif in notificacoes:
                self.notification_list.addItem(f"{notif['usuario']} - {notif['email']} ({notif['criado_em']})")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar notificações: {e}")
