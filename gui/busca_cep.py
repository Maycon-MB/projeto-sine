import requests
from PySide6.QtWidgets import QMessageBox

def consultar_cep(cep_input, cidade_input):
    cep = cep_input.text().strip()

    # Remove tudo que não for número
    cep_numerico = ''.join(filter(str.isdigit, cep))

    # Validação do CEP
    if not cep_numerico.isdigit():  # Verifica se há caracteres inválidos
        QMessageBox.critical(None, "Erro", "CEP inválido! Apenas números são permitidos.")
        return

    if len(cep_numerico) != 8:  # Verifica se tem exatamente 8 dígitos
        QMessageBox.critical(None, "Erro", "CEP inválido! Deve conter exatamente 8 dígitos numéricos.")
        return

    try:
        url = f'https://viacep.com.br/ws/{cep_numerico}/json/'
        response = requests.get(url, timeout=5)  # Adiciona timeout para evitar travamentos

        if response.status_code == 200:
            data = response.json()

            if "erro" in data:  # Se o CEP não existir na base do ViaCEP
                QMessageBox.critical(None, "Erro", "CEP não encontrado. Verifique e tente novamente.")
                return

            cidade = data.get('localidade', '')

            if cidade:
                # Verifica se a cidade já está na lista do ComboBox
                index = cidade_input.findText(cidade)
                if index == -1:
                    cidade_input.addItem(cidade)  # Adiciona caso não exista
                    cidade_input.setCurrentText(cidade)
                else:
                    cidade_input.setCurrentIndex(index)
        else:
            QMessageBox.critical(None, "Erro", "Erro ao buscar o CEP. Tente novamente mais tarde.")
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(None, "Erro", f"Erro de conexão: {str(e)}")
