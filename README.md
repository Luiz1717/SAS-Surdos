# SAS-Surdos
Segue o fluxo funcionando:

1) EDGE — ESP32 (Wokwi)
• Lê os valores do microfone
• Detecta sons acima do limiar
• Aciona os LEDs
• Publica o alerta em JSON via MQTT

2) FOG — Python (fog_service.py)
• Recebe as mensagens do ESP32 via MQTT
• Armazena localmente (SQLite)
• Envia os alertas para a nuvem
• Faz controle automático de reenvio
• Log mostrando todas as etapas

3) CLOUD — Firebase (RealTime Database)
• Recebe os alertas enviados pelo fog
• Armazena cada evento com ID único
• Dados chegando corretamente pela API
