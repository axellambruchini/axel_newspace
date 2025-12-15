import requests

def get_holiday_info(date_obj):
    """
    Simulación: Conecta a una API de feriados.
    Retorna información si la fecha elegida es festivo (puede afectar precios).
    """
    # Aquí iría la lógica real con requests.get('https://api.feriados...')
    # Por ahora retornamos un diccionario base
    return {"is_holiday": False, "reason": ""}

def get_weather_forecast(lat, lon, date_obj):
    """
    Obtiene el clima actual.
    Maneja el error si no hay API Key para que la web no se caiga.
    """
    # --- CONFIGURACIÓN ---
    # Si tienes tu clave, pégala dentro de las comillas.
    # Si no la tienes, déjalo así, el código funcionará en modo "Demo".
    API_KEY = 'TU_API_KEY_DE_OPENWEATHERMAP' 
    # ---------------------

    # 1. Modo de seguridad: Si no has puesto la clave, retornamos datos falsos sin dar error.
    if API_KEY == 'TU_API_KEY_DE_OPENWEATHERMAP':
        return {
            "temp": "--", 
            "condition": "Sin API Key (Modo Demo)",
            "icon_url": "" 
        }

    # 2. Intento de conexión real
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=es"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            condition = data['weather'][0]['description']
            icon = data['weather'][0]['icon']
            
            return {
                "temp": round(temp, 1),
                "condition": condition.capitalize(),
                "icon_url": f"http://openweathermap.org/img/wn/{icon}.png"
            }
        else:
            # Si la API responde error (ej: clave inválida)
            print(f"Error API Clima: {response.status_code}")
            return {"temp": "N/A", "condition": "Error servicio clima"}
            
    except Exception as e:
        # Si falla la conexión (internet, timeout)
        print(f"Excepción conectando a API Clima: {e}")
        return {"temp": "N/A", "condition": "Servicio no disponible"}