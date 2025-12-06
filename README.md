# Sensibility_Analysis

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue)

## Introdução

Sensibility_Analysis é uma ferramenta que busca modelar o comportamento tensão x deformação de uma pilha de rejeitos por meio do modelo Hardening Soil, além de avaliar a sensibilidade dos parâmetros. Desenvolvido como um projeto open source, o objetivo é quantificar como as incertezas nos parâmetros do solo afetam as tensões e deformações do sistema.

## Funcionalidades

- Quantificar incertezas nos parâmetros
- Avaliar a confiabilidade do sistema
- Fornecer curva tensão-deformação

## Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

- [Python] versão 3.12
- [Numpy] versão 2.3.5
- [matplotlib] versão 3.10.7

## Instalação

Siga as etapas abaixo para configurar o projeto em sua máquina local:

1. Clone o repositório:
    ```bash
    git clone https://github.com/IMNascimento/Sensitivity_Analysis.git
    ```
2. Navegue até o diretório do projeto:
    ```bash
    cd Sensitivity_Analysis
    ```

3. Crie e ative o ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Para Linux/MacOS
    .\venv\Scripts\activate  # Para Windows
    ```
4. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

5. Instalação de modulo do projeto:
    ```python
    #instalação do modulo 
    pip install -e .
    ```
    
## Uso

Após a instalação, você pode iniciar a aplicação com o seguinte comando:

```bash
streamlit run src/sensitivity_analysis/web/app.py
```

Acesse o projeto em http://localhost:8501.

## Exemplos de Uso
```python
# Exemplo de código mostrando como usar a funcionalidade principal do projeto
```

## Contribuindo

Contribuições são bem-vindas! Por favor, siga as diretrizes em CONTRIBUTING.md para fazer um pull request.

## Licença

Distribuído sob a licença MIT. Veja LICENSE para mais informações.

## Autores

Igor Nascimento - Desenvolvedor Principal - [github.com/IMNascimento](https://github.com/IMNascimento/)
Bruna Martins - Desenvolvedora - [github.com/brunamartinseesc](https://github.com/brunamartinseesc)

## Agradecimentos
Agradeço a contribuição fundamental do professor Igor Nascimento para o sucesso deste projeto.
