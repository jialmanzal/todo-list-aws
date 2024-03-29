import os
import boto3
import time
import uuid
import json
import functools
from botocore.exceptions import ClientError


def get_table(dynamodb=None):
    if not dynamodb:
        URL = os.environ['ENDPOINT_OVERRIDE']
        if URL:
            print('URL dynamoDB:'+URL)
            boto3.client = functools.partial(boto3.client, endpoint_url=URL)
            boto3.resource = functools.partial(boto3.resource,
                                               endpoint_url=URL)
        dynamodb = boto3.resource("dynamodb")
    # fetch todo from the database
    try:
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        return table
    except (UnboundLocalError, AttributeError):
        print("Error al obtener la tabla")


def get_item(key, dynamodb=None):
    table = get_table(dynamodb)
    try:
        result = table.get_item(
            Key={
                'id': key
            }
        )

    except (UnboundLocalError, AttributeError, ClientError):
        print("Error al obtener el item")
    else:
        print('Result getItem:'+str(result))
        if 'Item' in result:
            return result['Item']


def get_items(dynamodb=None):
    table = get_table(dynamodb)
    # fetch todo from the database
    result = table.scan()
    return result['Items']


def put_item(text, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = str(time.time())
    print('Table name:' + table.name)
    item = {
        'id': str(uuid.uuid1()),
        'text': text,
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }
    try:
        # write the todo to the database
        table.put_item(Item=item)
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }

    except (UnboundLocalError, AttributeError, ClientError):
        print("Error al ejecutar el recurso put_item")
    else:
        return response


def update_item(key, text, checked, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = int(time.time() * 1000)
    # update the todo in the database
    try:
        result = table.update_item(
            Key={
                'id': key
            },
            ExpressionAttributeNames={
              '#todo_text': 'text',
            },
            ExpressionAttributeValues={
              ':text': text,
              ':checked': checked,
              ':updatedAt': timestamp,
            },
            UpdateExpression='SET #todo_text = :text, '
                             'checked = :checked, '
                             'updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )

    except (UnboundLocalError, AttributeError, ClientError):
        print("Error al actualizar el item")
    else:
        return result['Attributes']


def delete_item(key, dynamodb=None):
    table = get_table(dynamodb)
    # delete the todo from the database
    try:
        table.delete_item(
            Key={
                'id': key
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return


def create_todo_table(dynamodb):
    # For unit testing
    tableName = os.environ['DYNAMODB_TABLE']
    print('Creating Table with name:' + tableName)
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
    if (table.table_status != 'ACTIVE'):
        raise AssertionError()

    return table

#Definición de la función para traducción en donde se recibe el texto a traducir y el lenguaje deseado
def translate_texto(text, language):
    #Se define el servicio de traducción suministrado por AWS
    print("*** texto a traducir *** " + text)
    print("*** lenguaje a traducir *** " + language)
    #traductor = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
    translate = boto3.client(service_name='translate')
    try:
        #Se hace uso de la funcion de traducción
        result = translate.translate_text(Text=text, SourceLanguageCode="auto", TargetLanguageCode=language)
        print('TranslatedText: ' + result.get('TranslatedText'))
        print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
        print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))
    except ClientError as e:
        #En caso de error se imprime el respectivo mensaje
        print(e.response['Error']['Message'])
    else:
        # Se retorna el texto traducido 
        translation = result.get('TranslatedText')
        print('Result translate:'+str(translation))
        return translation