from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class CadastrarFuncaoWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("CADASTRAR NOVA FUNÇÃO")

        # Layout principal
        layout = QVBoxLayout()
        
        # Rótulo e campo de entrada
        self.label = QLabel("NOME DA FUNÇÃO:")
        self.input_funcao = QLineEdit()
        self.input_funcao.setPlaceholderText("Digite a função...")
        self.input_funcao.textChanged.connect(self.converter_para_maiusculo)
        self.input_funcao.returnPressed.connect(self.salvar_funcao)  # Enter ativa o botão
        
        # Botão para salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_funcao)
        
        # Adicionando os widgets ao layout
        layout.addWidget(self.label)
        layout.addWidget(self.input_funcao)
        layout.addWidget(self.btn_salvar)
        layout.addStretch()
        
        self.setLayout(layout)

    def converter_para_maiusculo(self):
        texto = self.input_funcao.text().upper()
        self.input_funcao.blockSignals(True)  # Evita loop de sinais
        self.input_funcao.setText(texto)
        self.input_funcao.blockSignals(False)

    def salvar_funcao(self):
        nome_funcao = self.input_funcao.text().strip()  # Já está em UPPERCASE
        
        if not nome_funcao:
            QMessageBox.warning(self, "Aviso", "O nome da função não pode estar vazio!")
            return
        
        try:
            with self.db_connection.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO funcoes (nome) VALUES (%s)", (nome_funcao,))
                conn.commit()
                QMessageBox.information(self, "Sucesso", "Função cadastrada com sucesso!")
                self.input_funcao.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar função: {str(e)}")
