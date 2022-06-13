import todoList
import json


def translate(event, context):
    # Se obtiene el item a traducir desde la funcion get_item
    item = todoList.get_item(event['pathParameters']['id'])
    #Se pasan el valor contenido en el tag text el cual sera el objetivo de la traducción
    translation = todoList.translate_texto(item['text'], event['pathParameters']['language'])
    if translation:
        # Si es posible realizar la traducción se crea la respuesta con el resultado 
        response = {
            "statusCode": 200,
            "body": json.dumps(translation)
        }
    else:
        response = {
            #En caso de error se retorna el respectivo mensaje al usuario
            "statusCode": 500,
            "body": "Se produjo un error en la ejecución de la función de traduccion"
        }
    return response