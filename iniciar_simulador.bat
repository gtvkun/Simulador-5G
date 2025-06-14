@echo off
ECHO ===================================================
ECHO  INICIANDO O SERVIDOR DA API DO SIMULADOR 5G
ECHO  Nao feche esta janela de terminal!
ECHO ===================================================

:: Inicia o servidor uvicorn em uma nova janela de terminal.
:: O 'start' permite que o script continue para o próximo passo.
:: O 'cmd /k' mantém a janela do servidor aberta para vermos os logs.
start "Simulador 5G - Backend" cmd /k uvicorn backend:app

:: Pausa de 5 segundos para dar tempo ao servidor de iniciar completamente.
ECHO Aguardando o servidor iniciar...
timeout /t 5 /nobreak > nul

:: Abre a interface do simulador no navegador padrão.
ECHO Abrindo a interface do simulador no navegador...
start index.html

exit