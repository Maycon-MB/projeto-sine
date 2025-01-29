from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QSize, Qt
from models.curriculo_model import CurriculoModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

class DashboardWidget(QWidget):
    def __init__(self, usuario_model, curriculo_model, navigate_callback, tipo_usuario=None, usuario_id=None, cidade_admin=None):
        super().__init__()
        self.usuario_model = usuario_model
        self.curriculo_model = curriculo_model
        self.navigate_callback = navigate_callback
        self.tipo_usuario = tipo_usuario
        self.usuario_id = usuario_id
        self.cidade_admin = cidade_admin

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("📊 Painel de Controle")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Gráficos Estatísticos
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(self.create_bar_chart("Currículos por Cidade", self.curriculo_model.get_curriculos_por_cidade()))
        stats_layout.addWidget(self.create_pie_chart("Distribuição de Escolaridade", self.curriculo_model.get_escolaridade_distribuicao()))
        stats_layout.addWidget(self.create_bar_chart("Cargos Mais Populares", self.curriculo_model.get_top_cargos()))
        
        layout.addLayout(stats_layout)

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

    def create_bar_chart(self, title, data):
        fig, ax = plt.subplots()
        labels, values = zip(*data.items()) if data else ([], [])
        
        ax.bar(range(len(labels)), values, color='royalblue')
        ax.set_title(title)
        
        ax.set_xticks(range(len(labels)))  # Define os ticks antes dos labels
        ax.set_xticklabels(labels, rotation=45, ha='right')
        
        canvas = FigureCanvas(fig)
        return canvas

    def create_pie_chart(self, title, data):
        fig, ax = plt.subplots()
        labels, values = zip(*data.items()) if data else ([], [])
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        ax.set_title(title)
        
        canvas = FigureCanvas(fig)
        return canvas
