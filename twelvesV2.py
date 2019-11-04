from flask import Flask, session, request, jsonify
from flask_session import Session
#from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
#Cria uma chave aletoria para cada sessao
app.secret_key = os.urandom(12).hex()
#CORS(app)

#funcao que traz todas as perguntas
def get_todas_perguntas(tag):

    url = "https://nrlyqybsaqsrbvj-siriusatp.adb.us-ashburn-1.oraclecloudapps.com/ords/SIRIUS/madkhacks/questions"
    querystring = {"KEYWORD":tag}
    response = requests.request("GET", url, params=querystring)
    lista = json.loads(response.text)['items']
    return lista

#funcao que traz recomendacao
def get_recomendacao(respostas):

    recomendacao = []
    valorTotal = 0
    url = "https://nrlyqybsaqsrbvj-siriusatp.adb.us-ashburn-1.oraclecloudapps.com/ords/SIRIUS/madkhacks/recomendacoes"
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
    url = "https://nrlyqybsaqsrbvj-siriusatp.adb.us-ashburn-1.oraclecloudapps.com/ords/SIRIUS/madkhacks/questions"
    headers = {'Content-Type': "application/json"}
    for data in dados:
        payload = '{"session_id":"'+session['sessionID']+'", "question_id": '+ str(data[0]) + ', "resposta": "'+ data[1] +'"}'
        requests.request("POST", url, data=payload, headers=headers)

#Insert recomendacoes no ADB
def insert_recomendation(recomendacoes):
    url = "https://nrlyqybsaqsrbvj-siriusatp.adb.us-ashburn-1.oraclecloudapps.com/ords/SIRIUS/madkhacks/recomendacoes"
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
            reponses = {"Pergunta": pergunta, "Resposta": respostas.split(','), "offset": 0, "sessionid": 'session='+str(request.cookies.get('session'))}
            #responses = jsonify()
            #responses.headers.add("Access-Control-Allow-Origin", "*")
            return responses
        else: 
            return 'Profissao nao encontrada'
    else:
        if session.get('lista') is not None:
            resposta = ''
            arg = request.get_json()
            resposta, session['ordem'], session['sort'] = get_perguntas(arg['resposta'], session['lista'], session['sort'], session['ordem'])
            #resposta = jsonify(resposta)
            #resposta.headers.add("Access-Control-Allow-Origin", "*")
            return resposta
        else:
            return 'Nao Existe Nenhuma sessao'


if __name__ == '__main__':
    
    app.run()