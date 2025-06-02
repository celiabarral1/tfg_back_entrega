import paho.mqtt.client as mqtt
import json

def config_mqtt():
    #Listado de topics [imagenes] - [alertas] - [series temporales] 
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.connect("mqtt.eclipseprojects.io", 1883, 60)
    return mqttc

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")


# Esto se puede enviar una vez analizado cada trabajador
# o bien al final de un período deerminado de tiempo (al final del día, cada semanas, ...etc) 
def mandar_alerta_emocion(client, datos_inferencia, timestamp):
    id = "alerta_emocion"
    
    # Este json tiene que contener la secuencia de emociones reconocidas para cada 
    # vez que un trabajador interacciona con el robot.
    json_data = {
        "id": id,
        "timestamp": timestamp,
        "value":
            {
                "workerid": datos_inferencia['worker_id'], 
                "emocategoric": datos_inferencia['emocategoric'], 
                "emodimensional": datos_inferencia['emodimensional']
            }
    }
    
    client.publish("inmerbot/emocion", json.dumps(json_data))
        