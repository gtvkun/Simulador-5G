# ==============================================================================
# ARQUIVO: backend.py
# DESCRIÇÃO: Servidor backend para o Simulador 5G.
#            Responsável pelos cálculos de propagação de sinal, QoS e
#            geração dinâmica de dispositivos.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORTAÇÕES DE BIBLIOTECAS
# ------------------------------------------------------------------------------
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import math
import random

# ------------------------------------------------------------------------------
# 2. MODELO DE DADOS PARA ENTRADA DA API
# ------------------------------------------------------------------------------
class SimulationInput(BaseModel):
    """Define a estrutura de dados que o frontend envia para este backend."""
    lat: float
    lon: float
    potencia_dbm: float

# ------------------------------------------------------------------------------
# 3. CONSTANTES E PARÂMETROS GLOBAIS DA SIMULAÇÃO
# ------------------------------------------------------------------------------
# --- Configurações da Torre e Ambiente
FREQ_MHZ = 3500.0           # Frequência da portadora em MHz (Banda C do 5G)
ALTURA_TORRE_M = 20.0       # Altura da antena da torre (eNB/gNB) em metros
ALTURA_USER_M = 1.5         # Altura da antena do usuário (UE) em metros
LARGURA_BANDA_HZ = 20 * 1e6 # Largura de banda do canal em Hz (20 MHz)

# --- Configurações dos Dispositivos
TOTAL_DEVICES = 500         # Número total de dispositivos a serem gerados
DISTRIBUICAO = {            # Proporção de cada tipo de serviço
    'mMTC': 0.60,           # 60%
    'eMBB': 0.30,           # 30%
    'URLLC': 0.10           # 10%
}
RAIO_MIN_M = 50             # Distância mínima dos dispositivos à torre
RAIO_MAX_M = 1000           # Distância máxima (1 km)

# --- Constantes Físicas
THERMAL_NOISE_DBM_PER_HZ = -174 # Ruído térmico em dBm/Hz, um valor padrão em telecomunicações

# ------------------------------------------------------------------------------
# 4. FUNÇÕES AUXILIARES DE GEOLOCALIZAÇÃO
# ------------------------------------------------------------------------------
def haversine_destination(lat, lon, distance_m, bearing_deg):
    """
    Calcula uma nova coordenada geográfica a partir de um ponto inicial,
    uma distância em metros e uma direção em graus.
    
    Args:
        lat (float): Latitude do ponto de partida.
        lon (float): Longitude do ponto de partida.
        distance_m (float): Distância em metros.
        bearing_deg (float): Direção (azimute) em graus (0-360).

    Returns:
        list[float, float]: Uma lista contendo a nova [latitude, longitude].
    """
    R = 6371000  # Raio médio da Terra em metros
    d = distance_m
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_deg)
    
    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(d / R) +
                            math.cos(lat_rad) * math.sin(d / R) * math.cos(bearing_rad))
    new_lon_rad = lon_rad + math.atan2(math.sin(bearing_rad) * math.sin(d / R) * math.cos(lat_rad),
                                     math.cos(d / R) - math.sin(lat_rad) * math.sin(new_lat_rad))
    return [math.degrees(new_lat_rad), math.degrees(new_lon_rad)]

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em metros entre duas coordenadas geográficas
    usando a fórmula de Haversine.

    Args:
        lat1, lon1 (float): Coordenadas do primeiro ponto.
        lat2, lon2 (float): Coordenadas do segundo ponto.

    Returns:
        float: Distância em metros.
    """
    R = 6371000  # Raio médio da Terra em metros
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ------------------------------------------------------------------------------
# 5. LÓGICA PRINCIPAL DA SIMULAÇÃO
# ------------------------------------------------------------------------------
def generate_devices(center_lat, center_lon):
    """
    Gera uma lista de dispositivos (usuários) aleatoriamente posicionados
    em um anel em volta de um ponto central (a torre).
    
    Args:
        center_lat (float): Latitude do centro (torre).
        center_lon (float): Longitude do centro (torre).

    Returns:
        list: Uma lista de dispositivos, onde cada um é [latitude, longitude, tipo_serviço].
    """
    devices = []
    counts = {dev_type: int(TOTAL_DEVICES * perc) for dev_type, perc in DISTRIBUICAO.items()}
    while sum(counts.values()) < TOTAL_DEVICES: # Garante a contagem exata
        counts[random.choice(list(counts.keys()))] += 1
        
    for dev_type, count in counts.items():
        for _ in range(count):
            distancia = random.uniform(RAIO_MIN_M, RAIO_MAX_M)
            angulo = random.uniform(0, 360)
            lat_dev, lon_dev = haversine_destination(center_lat, center_lon, distancia, angulo)
            devices.append([lat_dev, lon_dev, dev_type])
            
    return devices

def path_loss_hata(dist_km):
    """
    Calcula a perda de percurso (Path Loss) em dB usando o modelo
    Okumura-Hata para ambientes urbanos.

    Args:
        dist_km (float): Distância entre a torre e o usuário em quilômetros.

    Returns:
        float: A perda de sinal (Path Loss) em dB.
    """
    if dist_km <= 0: dist_km = 0.001 # Evita log de zero ou número negativo

    # Fator de correção para a altura da antena do usuário para cidades grandes
    a_hm = (1.1 * math.log10(FREQ_MHZ) - 0.7) * ALTURA_USER_M - (1.56 * math.log10(FREQ_MHZ) - 0.8)
    
    # Fórmula principal do Okumura-Hata
    loss = (69.55 + 26.16 * math.log10(FREQ_MHZ) - 13.82 * math.log10(ALTURA_TORRE_M) - a_hm +
            (44.9 - 6.55 * math.log10(ALTURA_TORRE_M)) * math.log10(dist_km))
    
    return loss

def calculate_qos(rssi, dev_type):
    """
    Calcula a Qualidade de Serviço (QoS) para um dispositivo com base na
    potência do sinal recebido (RSSI) e no seu tipo de serviço.

    Args:
        rssi (float): Potência do sinal recebido em dBm.
        dev_type (str): O tipo de serviço ('eMBB', 'mMTC' ou 'URLLC').

    Returns:
        tuple: Uma tupla contendo (downlink_mbps, uplink_mbps, satisfacao).
    """
    # 1. Calcular o Ruído Térmico Total no canal
    total_noise_dbm = THERMAL_NOISE_DBM_PER_HZ + 10 * math.log10(LARGURA_BANDA_HZ)

    # 2. Calcular a Relação Sinal-Ruído (Signal-to-Noise Ratio - SNR)
    snr_db = rssi - total_noise_dbm
    if snr_db < 0: return 0, 0, 0.0 # Conexão inviável se o sinal for mais fraco que o ruído
        
    # 3. Estimar a capacidade máxima do canal (Teorema de Shannon-Hartley)
    snr_linear = 10**(snr_db / 10)
    capacidade_mbps = (LARGURA_BANDA_HZ * math.log2(1 + snr_linear)) / 1e6
    
    downlink, satisfacao = 0, 0

    # 4. Ajustar os resultados por tipo de serviço, modelando seus requisitos
    if dev_type == 'eMBB':
        downlink = capacidade_mbps * 0.7 # Fator de eficiência espectral
        satisfacao = min(downlink / 100, 1.0)
    elif dev_type == 'mMTC':
        downlink = min(capacidade_mbps, 0.1) # Baixo throughput é esperado
        satisfacao = 1.0 if rssi > -120 else 0.5 if rssi > -130 else 0.0
    elif dev_type == 'URLLC':
        downlink = min(capacidade_mbps * 0.5, 50) # Throughput moderado, alta confiabilidade
        satisfacao = 1.0 if snr_db > 20 else 0.7 if snr_db > 10 else 0.3 if snr_db > 5 else 0.0
    
    uplink = downlink / 4 # Uplink é tipicamente uma fração do downlink
    return downlink, uplink, satisfacao

# ------------------------------------------------------------------------------
# 6. INICIALIZAÇÃO E ENDPOINT DA API (FASTAPI)
# ------------------------------------------------------------------------------
app = FastAPI(title="Simulador 5G API")

# Configuração do CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate", summary="Executa uma simulação 5G")
def simulate(sim_input: SimulationInput):
    """
    Endpoint principal da API. Recebe as coordenadas da torre, gera os
    dispositivos ao redor dela e calcula o desempenho para cada um.
    """
    devices_para_simular = generate_devices(sim_input.lat, sim_input.lon)
    resultados = []
    
    for lat_dev, lon_dev, dev_type in devices_para_simular:
        # Para cada dispositivo, calcula distância, perda de percurso, RSSI e QoS
        dist_m = haversine(sim_input.lat, sim_input.lon, lat_dev, lon_dev)
        loss = path_loss_hata(dist_m / 1000.0)
        rssi = sim_input.potencia_dbm - loss
        downlink, uplink, satisfacao = calculate_qos(rssi, dev_type)
        
        resultados.append({
            "pos": [lat_dev, lon_dev],
            "type": dev_type,
            "rssi": rssi,
            "downlink": downlink,
            "uplink": uplink,
            "satisfacao": satisfacao,
            "distancia": dist_m
        })
        
    return {"devices": resultados}