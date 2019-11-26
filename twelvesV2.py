from flask import Flask, session, request, jsonify
from flask_session import Session
from flask_cors import CORS
import requests
import os
import json
import flask_cors

app = Flask(__name__)
#Cria uma chave aletoria para cada sessao
app.secret_key = os.urandom(12).hex()
CORS(app,allow_headers=['Cookie', 'Content-Type', 'Access-Control-Allow-Credentials', 'Set-Cookie'], resources=r'/*',  supports_credentials=True)

def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True

#funcao que traz todas as perguntas
def get_todas_perguntas(tag):
    if is_number(tag) == False:
        tag = ''
    url = "https://r9tdk8a7j3gfkze-siriusatpdb.adb.us-phoenix-1.oraclecloudapps.com/ords/sirius/madhacks/questions"
    querystring = {"KEYWORD":tag}
    response = requests.request("GET", url, params=querystring)
    lista = json.loads(response.text)['items']
    return lista

#funcao que traz recomendacao
def get_recomendacao(respostas):

    recomendacao = []
    valorTotal = 0
    url = "https://r9tdk8a7j3gfkze-siriusatpdb.adb.us-phoenix-1.oraclecloudapps.com/ords/sirius/madhacks/recomendacoes"
    for f in respostas:
        querystring = {"id":f[0], "resposta":f[1]}
        req = json.loads(requests.request("GET", url, params=querystring).text)['items']
        for i in req:
            recomendacao.append(i)
            valorTotal+= i['price']
    insert_recomendation(recomendacao)
    return recomendacao, valorTotal

#Insert resposta no ADB
def insert_questions(dados):
    url = "https://r9tdk8a7j3gfkze-siriusatpdb.adb.us-phoenix-1.oraclecloudapps.com/ords/sirius/madhacks/questions"
    headers = {'Content-Type': "application/json"}
    for data in dados:
        payload = '{"session_id":"'+session['sessionID']+'", "question_id": '+ str(data[0]) + ', "resposta": "'+ data[1] +'"}'
        requests.request("POST", url, data=payload, headers=headers)

#Insert recomendacoes no ADB
def insert_recomendation(recomendacoes):
    url = "https://r9tdk8a7j3gfkze-siriusatpdb.adb.us-phoenix-1.oraclecloudapps.com/ords/sirius/madhacks/recomendacoes"
    headers = {'Content-Type': "application/json"}
    for data in recomendacoes:
        payload = '{"session_id":"'+session['sessionID']+'", "subject": '+ str(session['tag']) + ', "topic_id": '+ str(data["topic_id"]) +', "course_id": '+ str(data["course_id"]) +'}'
        requests.request("POST", url, data=payload, headers=headers)

#fucao que traz as perguntas na ordem, verifica se a resposta foi sim ou nao 
#adiciona os topicos com resposta negativa na trilha e remove os filhos desse topico
def get_perguntas(param, lista, sort, ordem):
    perguntas = [t for t in lista if t['sort'] == sort]
    tempResp = []
    if ordem <= len(perguntas) - 1:
        if perguntas[ordem]['father'] == 0:
            if param == 'No':
                session['trilha'].append([perguntas[ordem]['id'], param])
                tempResp.append([perguntas[ordem]['id'], param])
                result = [p for p in perguntas if p['father'] != 0]
                if len(result) > 0: 
                    for j in result:
                        session['trilha'].append([j['id'],j['respostas'].split(',')[-1]])
                        tempResp.append([j['id'],j['respostas'].split(',')[-1]])
                sort += 1
                ordem = 0        
            else:
                session['trilha'].append([perguntas[ordem]['id'], param])
                tempResp.append([perguntas[ordem]['id'], param])
                result = [p for p in perguntas if p['father'] != 0]
                if len(result) > 0:
                    ordem += 1
                else:
                    ordem = 0
                    sort += 1
        else:
            if ordem < len(perguntas) -1:
                session['trilha'].append([perguntas[ordem]['id'], param])
                tempResp.append([perguntas[ordem]['id'], param])
                ordem += 1
            else:
                session['trilha'].append([perguntas[ordem]['id'], param])
                tempResp.append([perguntas[ordem]['id'], param])
                ordem = 0
                sort += 1
    if sort <= max(t['sort'] for t in lista):
        pergunta = [t['question'] for t in lista if t['sort'] == sort][ordem]
        respostas = [t['respostas'] for t in lista if t['sort'] == sort][ordem]
        retorno = {"Pergunta" : pergunta, "Respostas": respostas.split(','), "offset": 0}
        insert_questions(tempResp)
        return retorno, ordem, sort
    else:
        recomendacao, valor = get_recomendacao(session['trilha'])
        return {"Recomendacao": recomendacao, "Valor Total": valor, "offset": 1}, 0 ,1 

#Cria o path relativo do endpoint
@app.route('/tag', methods=['GET', 'POST'])
def tag():
    #verifica se a chamada e um GET ou um POST
    if request.method == 'GET':
        session['tag'] = request.args.get('tag')
        session['lista'] = get_todas_perguntas(session['tag'])
        if len(session['lista']) > 0:
            session['sessionID'] = os.urandom(20).hex()
            session['sort'] = 1
            session['trilha'] = []
            session['ordem'] = 0
            pergunta = [t['question'] for t in session['lista'] if t['sort'] == session['sort'] and t['father'] == 0][0]
            respostas = [t['respostas'] for t in session['lista'] if t['sort'] == session['sort'] and t['father'] == 0][0]
            responses = {"Pergunta": pergunta, "Resposta": respostas.split(','), "offset": 0, "sessionid": 'session='+str(request.cookies.get('session'))}
            responses = jsonify(responses)
            responses.headers.add("Access-Control-Allow-Credentials", "true")
            responses.headers.add("Access-Control-Allow-Origin", "http://www.twelves.site")
            return responses
        else: 
            responses = jsonify({"Pergunta": "Sorry, but I'm still learning about this subject", "Resposta": [], "offset": 0, "sessionid": 'session='+str(request.cookies.get('session'))})
            return responses
    else:
        if session.get('lista') is not None:
            resposta = ''
            arg = request.get_json()
            resposta, session['ordem'], session['sort'] = get_perguntas(arg['resposta'], session['lista'], session['sort'], session['ordem'])
            offset = resposta['offset']
            resposta = jsonify(resposta)
            resposta.headers.add("Access-Control-Allow-Credentials", "true")
            resposta.headers.add("Access-Control-Allow-Origin", "http://www.twelves.site")
            
            if offset == 1:
                session.clear()

            return resposta
        else:
            print(str(request.cookies.get('session')))
            return 'Nao Existe Nenhuma sessao'


if __name__ == '__main__':
    
    app.run('0.0.0.0')