from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QStackedWidget
from gui.cadastro import CadastroWidget
from gui.consulta import ConsultaWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gerenciamento de Pessoas")
        self.setMinimumSize(800, 600)

        # Layout principal
        main_layout = QHBoxLayout()

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)

        self.button_cadastro = QPushButton("Cadastro")
        self.button_cadastro.clicked.connect(lambda: self.switch_screen(0))
        self.sidebar_layout.addWidget(self.button_cadastro)

        self.button_consulta = QPushButton("Consulta")
        self.button_consulta.clicked.connect(lambda: self.switch_screen(1))
        self.sidebar_layout.addWidget(self.button_consulta)

        self.sidebar_layout.addStretch()

        # Área principal
        self.main_area = QStackedWidget()
        self.main_area.addWidget(CadastroWidget())  # Tela de Cadastro
        self.main_area.addWidget(ConsultaWidget())  # Tela de Consulta

        # Adicionando ao layout principal
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_area, 1)

        # Configuração do layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def switch_screen(self, index):
        self.main_area.setCurrentIndex(index)
