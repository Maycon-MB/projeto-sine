from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from gui.configuracoes import ConfiguracoesWidget  # Certifique-se de que o arquivo `configuracoes.py` está no mesmo diretório
from gui.cadastro import CadastroWidget  # Certifique-se de que o arquivo `cadastro.py` está no mesmo diretório


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicação com Sidebar")
        self.resize(1200, 600)

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
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(10)

        # Botões da Sidebar
        self.buttons = {}
        button_info = {
            "Home": "home-icon.png",
            "Cadastrar Pessoa": "register-icon.png",
            "Consultar Pessoas": "search-icon.png",
            "Configurações": "settings-icon.png",
            "Sair": "exit-icon.png"
        }

        for name, icon_path in button_info.items():
            btn = QPushButton(name)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setStyleSheet(self._button_stylesheet())
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, n=name: self._navigate(n))
            self.sidebar_layout.addWidget(btn)
            self.buttons[name] = btn

        self.sidebar_layout.addStretch()  # Adiciona um espaçamento flexível ao final
        main_layout.addWidget(self.sidebar)

        # Área de conteúdo principal
        self.content_area = QStackedWidget()
        self.content_area.addWidget(QLabel("Bem-vindo ao sistema!"))  # Tela inicial padrão

        # Adiciona a tela de cadastro
        self.cadastro_widget = CadastroWidget()  # Aqui cria a tela de cadastro
        self.content_area.addWidget(self.cadastro_widget)

        # Adiciona a tela de configurações
        self.configuracoes_widget = ConfiguracoesWidget(self.current_theme, self.apply_theme)
        self.content_area.addWidget(self.configuracoes_widget)

        main_layout.addWidget(self.content_area, stretch=1)

        # Inicializa a navegação
        self._navigate("Home")

        # Aplica o tema salvo
        self.apply_theme(self.current_theme)

    def _navigate(self, screen_name):
        # Lógica para alternar a tela
        for name, btn in self.buttons.items():
            btn.setChecked(name == screen_name)

        if screen_name == "Home":
            self.content_area.setCurrentIndex(0)
        elif screen_name == "Cadastrar Pessoa":
            self.content_area.setCurrentIndex(1)  # Alterado para o índice correto da tela de cadastro
        elif screen_name == "Consultar Pessoas":
            self.content_area.addWidget(QLabel("Tela de Consulta de Pessoas"))
            self.content_area.setCurrentIndex(2)
        elif screen_name == "Configurações":
            # Exibe o widget de configurações
            self.content_area.setCurrentWidget(self.configuracoes_widget)
        elif screen_name == "Sair":
            QApplication.quit()

    def apply_theme(self, theme):
        # Aplica o tema
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
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #dcdcdc;
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
