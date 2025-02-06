from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QHBoxLayout, QComboBox
)
from PySide6.QtGui import QFont, QIcon, QColor, QPalette
from PySide6.QtCore import QSize, Qt, QThread, Signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

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
            ("Funções Mais Populares", self.curriculo_model.get_top_cargos(self.filtro), "sorted_bar"),
            ("Primeiro Emprego vs Experientes", self.curriculo_model.get_pcd_distribuicao(self.filtro), "pie"),
            ("Idade vs Experiência", self.curriculo_model.get_experiencia_por_idade(self.filtro), "experience_age")
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
        title = QLabel("\U0001F4CA Painel de Controle")
        layout.addWidget(title)

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
            ("Primeiro Emprego vs Experientes", "pie"),
            ("Idade vs Experiência", "experience_age")
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
        fig, ax = plt.subplots(figsize=(12, 8))
        labels, values = zip(*data.items()) if data else ([], [])
        values = [int(v) for v in values]  # Garantindo que os valores sejam inteiros
        colors = plt.cm.tab10.colors[:len(labels)]

        bar_width = max(0.2, 0.6 - 0.02 * len(labels))  # Ajusta largura das barras

        if chart_type == "bar":
            ax.bar(labels, values, color=colors, width=bar_width)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        elif chart_type == "barh":
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Alterado de yaxis para xaxis
            ax.barh(labels, values, color=colors, height=bar_width)
            ax.invert_yaxis()
            ax.grid(axis='x', linestyle='--', alpha=0.7)
        elif chart_type == "sorted_bar":
            sorted_items = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
            sorted_labels, sorted_values = zip(*sorted_items)
            ax.bar(sorted_labels, sorted_values, color=colors, width=bar_width)
            ax.set_xticks(range(len(sorted_labels)))
            ax.set_xticklabels(sorted_labels, rotation=30, ha='right', fontsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        elif chart_type == "pie":
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
            for text in texts + autotexts:
                text.set_fontsize(10)
            ax.axis('equal')
        elif chart_type == "experience_age":
            ax.plot(labels, values, marker='o', linestyle='-', color='b')
            ax.set_xticks(labels)
            ax.set_xlabel("Idade")
            ax.set_ylabel("Anos de Experiência")
            ax.grid(True, linestyle='--', alpha=0.7)

        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.set_title(title)
        fig.tight_layout()
        return FigureCanvas(fig)

    def update_chart(self, title, chart_type):
        self.loading_bar.setVisible(True)

        chart_methods = {
            "bar": self.curriculo_model.get_curriculos_por_cidade,
            "barh": self.curriculo_model.get_escolaridade_distribuicao,
            "sorted_bar": self.curriculo_model.get_top_funcoes,
            "pie": self.curriculo_model.get_pcd_distribuicao,
            "experience_age": self.curriculo_model.get_experiencia_por_idade,
        }

        if chart_type not in chart_methods:
            print(f"Erro: Nenhum método encontrado para o tipo de gráfico '{chart_type}'")
            self.loading_bar.setVisible(False)
            return

        data = chart_methods[chart_type](self.current_filter)
        data = {k: int(v) for k, v in data.items()}

        if self.current_chart:
            self.chart_container.removeWidget(self.current_chart)
            self.current_chart.deleteLater()

        self.current_chart = self.create_chart(title, data, chart_type)
        self.chart_container.addWidget(self.current_chart)
        self.loading_bar.setVisible(False)
