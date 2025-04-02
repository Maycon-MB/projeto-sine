from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QHBoxLayout, QComboBox
)
from PySide6.QtGui import QFont, QIcon, QColor, QPalette
from PySide6.QtCore import QSize, Qt, QThread, Signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

class ChartLoaderThread(QThread):
    charts_ready = Signal(list)

    def __init__(self, curriculo_model, filtro):
        super().__init__()
        self.curriculo_model = curriculo_model
        self.filtro = filtro

    def run(self):
        charts_data = [
            ("Currículos por Cidade", self.curriculo_model.get_curriculos_por_cidade(self.filtro), "bar"),
            ("Distribuição de Escolaridade", self.curriculo_model.get_escolaridade_distribuicao(self.filtro), "barh"),
            ("Funções Mais Populares", self.curriculo_model.get_top_funcoes(self.filtro), "sorted_bar"),
            ("Proporção de CTPS", self.curriculo_model.get_ctps_distribuicao(self.filtro), "pie"),
            ("Idade vs Experiência", self.curriculo_model.get_experiencia_media_por_idade(self.filtro), "experience_age"),
            ("Distribuição por Faixa Etária", self.curriculo_model.get_faixa_etaria_distribuicao(self.filtro), "bar")
        ]
        self.charts_ready.emit(charts_data)

class DashboardWidget(QWidget):
    def __init__(self, usuario_model, curriculo_model, navigate_callback, tipo_usuario=None, usuario_id=None, cidade_admin=None):
        super().__init__()
        self.usuario_model = usuario_model
        self.curriculo_model = curriculo_model
        self.navigate_callback = navigate_callback
        self.tipo_usuario = tipo_usuario
        self.usuario_id = usuario_id
        self.cidade_admin = cidade_admin
        self.current_chart = None
        self.current_filter = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.filter_selector = QComboBox()
        self.filter_selector.addItems(["Todos", "Últimos 30 dias", "Últimos 6 meses", "Último ano"])
        self.filter_selector.currentTextChanged.connect(self.update_filter)
        layout.addWidget(self.filter_selector)

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        layout.addWidget(self.loading_bar)

        self.buttons_layout = QHBoxLayout()
        self.chart_container = QVBoxLayout()
        self.chart_container.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(self.buttons_layout)
        layout.addLayout(self.chart_container)
        self.setLayout(layout)

        self.charts_data = [
            ("Currículos por Cidade", "bar"),
            ("Distribuição de Escolaridade", "barh"),
            ("Funções Mais Populares", "sorted_bar"),
            ("Proporção de CTPS", "pie"),
            ("Idade vs Experiência", "experience_age"),
            ("Distribuição por Faixa Etária", "bar")
        ]

        for title, chart_type in self.charts_data:
            button = QPushButton(title)
            button.clicked.connect(lambda checked=False, t=title, c=chart_type: self.update_chart(t, c))
            self.buttons_layout.addWidget(button)

        self.update_chart(self.charts_data[0][0], self.charts_data[0][1])

    def update_filter(self, filter_text):
        self.current_filter = None if filter_text == "Todos" else filter_text
        self.update_chart(self.charts_data[0][0], self.charts_data[0][1])

    def create_chart(self, title, data, chart_type):
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.set_theme(style="whitegrid")  # Estilo moderno do Seaborn
        
        if not data:
            ax.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center')
            return FigureCanvas(fig)
        
        # Ordenar dados para alguns tipos de gráfico
        if chart_type in ["bar", "barh", "sorted_bar"]:
            items = sorted(data.items(), key=lambda x: x[1], reverse=True)
            labels, values = zip(*items)
        else:
            labels, values = zip(*data.items())

        colors = plt.cm.tab20.colors  # Paleta mais profissional
        edgecolor = '#333333'
        
        # Configurações comuns
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.set_facecolor('#f5f5f5')
        fig.patch.set_facecolor('#ffffff')
        
        if chart_type == "bar":
            bars = ax.bar(labels, values, color=colors, edgecolor=edgecolor)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.bar_label(bars, padding=3, fmt='%d')  # Mostrar valores nas barras
            
        elif chart_type == "barh":
            ax.barh(labels, values, color=colors, edgecolor=edgecolor)
            ax.invert_yaxis()  # Maior valor no topo
            ax.set_xlabel('Quantidade de Candidatos')
            
        elif chart_type == "sorted_bar":
            bars = ax.bar(labels, values, color=colors, edgecolor=edgecolor)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.bar_label(bars, padding=3, fmt='%d')
            
        elif chart_type == "pie":
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                wedgeprops={'edgecolor': edgecolor}
            )
            plt.setp(autotexts, size=10, weight="bold")  # % em negrito
            
        elif chart_type == "experience_age":
            ax.scatter(labels, values, color='dodgerblue', s=100, edgecolor=edgecolor)
            ax.plot(labels, values, color='dodgerblue', linestyle='--', alpha=0.5)
            ax.set_xlabel('Idade')
            ax.set_ylabel('Experiência Média (anos)')
            ax.set_xticks(range(min(labels), max(labels)+1))  # Todos os inteiros

        ax.set_title(title, pad=20, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return FigureCanvas(fig)

    def update_chart(self, title, chart_type):
        self.loading_bar.setVisible(True)

        chart_methods = {
            "bar": self.curriculo_model.get_curriculos_por_cidade,
            "barh": self.curriculo_model.get_escolaridade_distribuicao,
            "sorted_bar": self.curriculo_model.get_top_funcoes,
            "pie": self.curriculo_model.get_ctps_distribuicao,
            "experience_age": self.curriculo_model.get_experiencia_media_por_idade,
            "faixa_etaria": self.curriculo_model.get_faixa_etaria_distribuicao
        }

        data = chart_methods[chart_type](self.current_filter)
        # Garantir que todos os valores sejam inteiros
        data = {k: int(v) for k, v in data.items()}

        if self.current_chart:
            self.chart_container.removeWidget(self.current_chart)
            self.current_chart.deleteLater()

        self.current_chart = self.create_chart(title, data, chart_type)
        self.chart_container.addWidget(self.current_chart)
        self.loading_bar.setVisible(False)
