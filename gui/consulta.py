from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ConsultaWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Tela de Consulta")
        layout.addWidget(label)
        self.setLayout(layout)
