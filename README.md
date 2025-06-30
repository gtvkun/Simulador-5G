#  Simulador Interativo de Célula 5G

![Versão](https://img.shields.io/badge/versão-2.1-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.92.0-green?logo=fastapi)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)

Uma aplicação web interativa para simular o desempenho e a cobertura de uma *small cell* 5G. A ferramenta permite ao usuário posicionar uma torre de celular em um mapa interativo e visualizar em tempo real os principais indicadores de qualidade de serviço (QoS) para 500 usuários distribuídos na área, com base em um modelo de propagação de sinal realista.

### Pré-visualização

![image](https://github.com/user-attachments/assets/6ef9ed3d-98da-42ba-be0f-1cacd4bfd1f1)

---

## Funcionalidades Principais

### Interface Principal (`index.html`)
* **Mapa Interativo:** Utiliza a biblioteca Leaflet.js para exibir um mapa real da cidade de Uberlândia-MG.
* **Posicionamento da Torre:** Permite posicionar a antena 5G com um clique e reposicioná-la arrastando o ícone.
* **Ícones Personalizados:** Usa um ícone customizado para a torre e favicons para cada página.
* **Controles Dinâmicos:** Controles deslizantes para ajustar a **potência de transmissão** da torre (em dBm) e o **raio visual** da célula.
* **Visualização em Tempo Real:** Os dispositivos dos usuários são coloridos no mapa de acordo com o tipo de serviço (eMBB, mMTC, URLLC).
* **Feedback Instantâneo:** Ao clicar em um dispositivo, um pop-up exibe suas métricas individuais (RSSI, Downlink/Uplink, Tipo).
* **Painel de Resultados:** A barra lateral exibe a média de satisfação para cada fatia de serviço (slice).

### Simulação e Backend (`backend.py`)
* **Servidor Robusto:** Construído com o framework Python **FastAPI**.
* **Geração Dinâmica:** Gera 500 usuários dinamicamente em um raio de até 1km ao redor da torre a cada simulação.
* **Modelo de Propagação Realista:** Utiliza o modelo **Okumura-Hata** para calcular a perda de percurso, considerando frequência, altura da torre (20m) e altura do usuário (1.5m).
* **Cálculo de QoS:** Estima o throughput (Downlink/Uplink) com base na **Relação Sinal-Ruído (SNR)** e no **Teorema de Shannon-Hartley**.
* **Simulação de Slicing:** Modela os diferentes requisitos de QoS para os serviços **eMBB**, **mMTC** e **URLLC**.

### Página de Análise (`graficos.html`)
* **Relatório Visual:** Abre uma nova janela com 4 gráficos analíticos gerados com a biblioteca **Chart.js**.
* **Visualização da Informação:** Os gráficos incluem:
    1.  **Histograma** da distribuição de sinal (RSSI).
    2.  **Gráfico de Dispersão** da correlação entre Sinal e Distância.
    3.  **Gráfico de Barras** do throughput médio por serviço.
    4.  **Gráfico de Barras** da contagem de usuários satisfeitos.
* **Funcionalidade de Impressão:** Inclui um botão para imprimir o relatório ou salvá-lo como PDF, com formatação otimizada para impressão.

---

## Tecnologias Utilizadas
* **Backend:** Python 3, FastAPI, Uvicorn
* **Frontend:** HTML5, CSS3, JavaScript (ES6)
* **Bibliotecas:**
    * **Leaflet.js:** Para os mapas interativos.
    * **Chart.js:** Para a visualização de dados e gráficos.

---

## Como Executar o Projeto

**1. Pré-requisitos:**
* Ter o [Python 3.8](https://www.python.org/downloads/) ou superior instalado.

**2. Instalação das Dependências:**
Abra um terminal na pasta do projeto e instale as bibliotecas Python necessárias:
```bash
pip install fastapi uvicorn numpy
```
**3. Iniciar o Servidor Backend:**
No mesmo terminal, execute o seguinte comando:
```bash
uvicorn backend:app --reload
```
O terminal deve indicar que o servidor está rodando em http://127.0.0.1:8000. Mantenha este terminal aberto.

**4. Abrir o Simulador:**

Abra o arquivo index.html no seu navegador de internet.

**5. Usar a Aplicação:**

  Clique no mapa para posicionar a torre e iniciar a primeira simulação.
Use os controles na barra lateral para ajustar os parâmetros.
Após a simulação, clique no botão "Gerar Gráficos" para abrir a página de análise.

#Estrutura dos Arquivos
```bash
.
├── backend.py             # O servidor FastAPI com toda a lógica da simulação.
├── index.html             # A página principal do simulador (mapa e interface).
├── graficos.html          # A página dedicada a exibir os gráficos de análise.
├── antena.png             # Ícone customizado usado para a torre no mapa.
├── antena-de-radio.png    # Favicon da página de simulação.
└── grafico-de-barras.png  # Favicon da página de gráficos.
```
