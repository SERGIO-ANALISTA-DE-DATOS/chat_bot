import json
import csv
from collections import defaultdict

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
    
    def deliver_custom(self,numeros):
        query="""
                        SELECT ic.valor as Numero,ic.confirmado  as verificacion, 
                        p.noDocumento as documento,p.nombres as cliente,
                        c.nit,c.nombre as Comercio , s.nombre  as barrio ,c.direccion ,
                        ven.asesor
                        from INFO_CONTACTO ic
                        JOIN COMERCIO c  ON c.idComercio  = ic.idComerce
                        JOIN PERSONA p  ON p.noDocumento = ic.fk_noDocumento 
                        join RELACION_SECTORIZACION rs  on rs.id_comercio = ic.idComerce 
                        join SECTORIZACION s on s.idSector=rs.id_sector
                        join PERTENENCIA_COMERCIO_A_ZONA pcaz  on pcaz.fk_idComercio  = c.idComercio
                        join (
                            SELECT  noDocumento ,rn.idResponsableNegocio as idasesor ,nombres as asesor ,ar.area
                            from  PERSONA p 
                            join RESPONSABLE_NEGOCIO rn on rn.fk_noDocumento=p.noDocumento
                            join AREA_RESPONSABLE ar on ar.idarea = rn.area
                            where rn.idrol=1 
                        ) ven on pcaz.codAsesorTemp = ven.idasesor
                        where s.tipo ='BRR'  and c.estado ='ACT'
        """
        # and ic.valor in ([wtsp])
         
        # numeros_como_string = ",".join(f"'{number}'" for number in numeros)
        # query=query.replace('[wtsp]', numeros_como_string)  
        with self.conxion.cursor() as cursor:
            cursor.execute(query)
            resultado=cursor.fetchall()
            cursor.close()
            
        clientes_asesoras = defaultdict(list)
        for row in resultado:
            numero = row[2]  
            asesora = row[8]  
            if asesora not in clientes_asesoras[numero]:
                clientes_asesoras[numero].append(asesora)

        contador_asignaciones = defaultdict(int)

        tabla_final = []  
        for cliente, asesoras in clientes_asesoras.items():
            asesora_asignada = min(asesoras, key=lambda x: contador_asignaciones[x])
            contador_asignaciones[asesora_asignada] += 1

            for row in resultado:
                if row[2] == cliente:
                    fila = list(row[:8]) 
                    fila.append(asesora_asignada) 
                    tabla_final.append(fila)
                    break
                
        # Agregar_grupo
        grupos_y_visitas = {}

        nits = "','".join([fila[4] for fila in tabla_final]) 
        asesores = "','".join([fila[8] for fila in tabla_final])    

        query_grupos_visitas = f"""
            SELECT c.nit, ven.asesor, ven.area AS grupo, MAX(pcaz.diaVisita) AS dia_visita
            FROM COMERCIO c
            JOIN PERTENENCIA_COMERCIO_A_ZONA pcaz ON pcaz.fk_idComercio = c.idComercio
            JOIN (
                SELECT noDocumento, rn.idResponsableNegocio AS idasesor, nombres AS asesor, ar.area
                FROM PERSONA p
                JOIN RESPONSABLE_NEGOCIO rn ON rn.fk_noDocumento = p.noDocumento
                JOIN AREA_RESPONSABLE ar ON ar.idarea = rn.area
                WHERE rn.idrol = 1
            ) ven ON pcaz.codAsesorTemp = ven.idasesor
            WHERE c.nit IN ('{nits}') AND ven.asesor IN ('{asesores}')
            GROUP BY c.nit, ven.asesor, ven.area
        """     

        with self.conxion.cursor() as cursor:
            cursor.execute(query_grupos_visitas)
            resultados = cursor.fetchall()      

        for nit, asesor, grupo, dia_visita in resultados:
            grupos_y_visitas[(nit, asesor)] = (grupo, dia_visita)       

        pivot_final = []
        for fila in tabla_final:
            nit = fila[4]
            asesor = fila[8]
            grupo, dia_visita = grupos_y_visitas.get((nit, asesor), ("Sin Grupo", "Sin Visita"))
            fila.append(grupo)
            fila.append(dia_visita)
            pivot_final.append(fila)        

        tabla_final = pivot_final       


        csv_headers = [
            "Numero", "Verificacion", "Documento", "Cliente", "NIT", "Comercio", "Barrio", "direccion","Asesor Designado", "Grupo", "Visita"
        ]
        output_file = "Boyaca_clientes_designados.csv"
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(csv_headers)
            writer.writerows(tabla_final)       

        print(f"Archivo CSV generado: {output_file}")