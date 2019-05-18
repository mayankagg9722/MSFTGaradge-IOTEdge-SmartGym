
import requests

def GetIntent(query):
    headers = {
        'Ocp-Apim-Subscription-Key': 'b9523925e0784f64bf36fa3cc1f5801e',
    }
    params ={
        'q': query,
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }
    try:
        r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/b6562490-dde2-4693-ac26-66128a5ca9df',headers=headers, params=params)
        print(r.json())
        return r.json()
    except:
        return None 

def CheckIntent(res):
    if(res["topScoringIntent"]["intent"]):
        return res["topScoringIntent"]["intent"]
    else:
        return None    

def getNameEntity(resJson):
    entArr = resJson["entities"]
    for ent in entArr:
        if(ent["type"]=="builtin.personName"):
            personname =  ent["entity"]
            return personname
    return None

def CheckExerciseSentimentRole(resJson):
    entArr = resJson["entities"]
    for ent in entArr:
        if(ent["role"] and ent["role"]=="positive"):
            return True
        else:
            return False    
    return False
