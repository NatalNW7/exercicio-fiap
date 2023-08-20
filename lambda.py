import boto3
import json
import re

from dynamo import BaseDAO
from decimal import Decimal

client = boto3.client('s3')
dy = BaseDAO('votos')

def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = re.sub('\D{0,100}\/', '', event['Records'][0]['s3']['object']['key'])
    file_content = client.get_object(Bucket=bucket, Key=object_key)["Body"].read()

    votos = json.loads(file_content)
    items_dy = dy.scan_table_allpages()
    
    items = []
    totaldevotos = 0
    
    for candidato in votos['votos']:
            totaldevotos += votos['votos'][candidato]
    
    if items_dy:
        delete_items(items_dy)
        
        for item in items_dy:
            if item['candidato'] == 'totaldevotos':
               item['total'] += totaldevotos
               
            if item['candidato'] in votos['votos']:
                item['total'] += votos['votos'][item['candidato']]
                votos['votos'].pop(item['candidato'])
        
        merge_value(items_dy, votos)
        create_items(items_dy)
    else:
        merge_value(items, votos)
        
        items.append({
            'candidato': 'totaldevotos',
            'total': totaldevotos
        })
        
        create_items(items)
    

def merge_value(obj, votos):
    for candidato in votos['votos']:
        obj.append({
            'candidato': candidato,
            'total': votos['votos'][candidato]
        })
    
def delete_items(items):
    for item in items:
        dy.delete_item(item)   

def create_items(items):
    for item in items:
        dy.put_item(item)


if __name__ == '__main__':
    # TESTE 1
    votos = {
        "votos":{
            "candidato1": 3,
            "candidato2": 4
        }
    }
        
    totaldevotos = 0
    items = []
    
    for candidato in votos['votos']:
        totaldevotos += votos['votos'][candidato]
        
    merge_value(items, votos)
        #items.append({
        #    'candidato': candidato,
        #    'total': votos['votos'][candidato]
        #})
    
    items.append({
        'candidato': 'totaldevotos',
        'total': totaldevotos
    })
    
    print('### TESTE 1 ###')
    print(json.dumps(items, indent=4))
    
    # TESTE 2
    items_dy = [
        {
            'total': Decimal('7'), 
            'candidato': 'totaldevotos'
        }, 
        {
            'total': Decimal('3'), 
            'candidato': 'candidato1'
        }, 
        {
            'total': Decimal('4'), 
            'candidato': 'candidato2'
        }
    ]
    
    votos = {
        "votos":{
            "candidato1": 3,
            "candidato2": 4,
            "candidato3": 5
        }
    }
    
    #items = []
    totaldevotos = 0
    for candidato in votos['votos']:
        totaldevotos += votos['votos'][candidato]
    
    for item in items_dy:
        if item['candidato'] == 'totaldevotos':
           item['total'] += totaldevotos
           
        if item['candidato'] in votos['votos']:
            item['total'] += votos['votos'][item['candidato']]
            votos['votos'].pop(item['candidato'])
    
    
    merge_value(items_dy, votos)        
    #for candidato in votos['votos']:
    #    items_dy.append({
    #        'candidato': candidato,
    #        'total': votos['votos'][candidato]
    #    })
    #        
    
    print('### TESTE 2 ###')
    print(json.dumps(items_dy, indent=4, default=str))
    #print(json.dumps(votos, indent=4))
        #for k, v in item.items():
        #    if k == 'candidato':
        #        if v in votos['votos']:
        #            print(v)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    