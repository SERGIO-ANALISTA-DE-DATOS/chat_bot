import json

class  isa_bot:
    def __init__(self,conexion):
        self.conxion=conexion
        
    
    
    def get_message(self):
        query="""
        SELECT idNumber,messagesJSON from BOTWP_CONVERSATIONS_NEW
        """
        with self.conxion.cursor() as cursor:
            cursor.execute(query)
            resultado=cursor.fetchall()
            cursor.close()
            return resultado
        
    
    def get_sin_interaccion(self,chat):
        activos=[]
        allnumber=[]
        pediddos=[]
    
        for row in chat:
            allnumber.append(row[0])
            data=json.loads(row[1])
            conversation_array = data.get('conversationArray', {})
            messages = conversation_array.get('messages', [])
            for mensaje in messages:
                if mensaje['typeMessage']==1:
                    activos.append(row[0])
                if mensaje.get('message')=='*Tu pedido ha sido realizado correctamente.*':
                    pediddos.append([row[0]])

        inactivos = list(set(allnumber) - set(activos))
        print('Inactivos db',len(inactivos))
        return inactivos, activos

    def get_api(self,chat):
        activos=[]
        for item in chat.get('response', []):
            conversation_array = item.get('conversationArray', {})
            number=item['numberId']
            messages = conversation_array.get('messages', [])
            for mensaje in messages:
                if mensaje['typeMessage']==1:
                    activos.append(number)
        return activos   
               