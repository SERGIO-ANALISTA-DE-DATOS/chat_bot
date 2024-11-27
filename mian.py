from conection.Database import conectar_bd,conectar_abako 
from clase.extract_process_data import isa_bot
import requests 

conexion=conectar_bd()
room=isa_bot(conexion=conexion)
#-----------------------------

# Base de datos
chat=room.get_message()
inactivos,activos=room.get_sin_interaccion(chat)

# en api
Conversation_api = "https://servimaxinternal.app/liveopsapp/getCurrentConversation"
chat = requests.get(Conversation_api).json()
activosapi=room.get_api(chat)
# Total
inactivosFinal=list(set(inactivos) - set(activos))


room.deliver_custom(inactivosFinal)


