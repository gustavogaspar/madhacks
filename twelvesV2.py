from flask import Flask, session, request
from flask_session import Session
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
#Cria uma chave aletoria para cada sessao
app.secret_key = os.urandom(20)

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

    return recomendacao, valorTotal

#fucao que traz as perguntas na ordem, verifica se a resposta foi sim ou nao 
#adiciona os topicos com resposta negativa na trilha e remove os filhos desse topico
def get_perguntas(param, lista, sort, ordem):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    perguntas = [t for t in lista if t['sort'] == sort]
    if ordem <= len(perguntas) - 1:
        if perguntas[ordem]['father'] == 0:
            if param == 'No':
                session['trilha'].append([perguntas[ordem]['id'], param,now])
                result = [p for p in perguntas if p['father'] != 0]
                if len(result) > 0: 
                    for j in result:
                        session['trilha'].append([j['id'],j['respostas'].split(',')[-1],now])
                sort += 1
                ordem = 0        
            else:
                session['trilha'].append([perguntas[ordem]['id'], param,now])
                result = [p for p in perguntas if p['father'] != 0]
                if len(result) > 0:
                    ordem += 1
                else:
                    ordem = 0
                    sort += 1
        else:
            if ordem < len(perguntas) -1:
                session['trilha'].append([perguntas[ordem]['id'], param,now])
                ordem += 1
            else:
                session['trilha'].append([perguntas[ordem]['id'], param,now])
                ordem = 0
                sort += 1
    if sort <= max(t['sort'] for t in lista):
        pergunta = [t['question'] for t in lista if t['sort'] == sort][ordem]
        respostas = [t['respostas'] for t in lista if t['sort'] == sort][ordem]
        retorno = {"Pergunta" : pergunta, "Respostas": respostas.split(',')}
        return retorno, ordem, sort
    else:
        recomendacao, valor = get_recomendacao(session['trilha'])
        return {"Recomendacao": recomendacao, "Valor Total": valor}, 0 ,1 

#Cria o path relativo do endpoint
@app.route('/tag', methods=['GET', 'POST'])
def tag():
    #verifica se a chamada é um GET ou um POST
    if request.method == 'GET':
        session['lista'] = get_todas_perguntas(request.args.get('tag'))
        if len(session['lista']) > 0:
            session['sort'] = 1
            session['trilha'] = []
            session['ordem'] = 0
            pergunta = [t['question'] for t in session['lista'] if t['sort'] == session['sort'] and t['father'] == 0][0]
            respostas = [t['respostas'] for t in session['lista'] if t['sort'] == session['sort'] and t['father'] == 0][0]
            return {"Pergunta": pergunta, "Resposta": respostas.split(',')}
        else: 
            return 'Profissão não encontrada'
    else:
        if session.get('lista') is not None:
            resposta = ''
            arg = request.get_json()
            resposta, session['ordem'], session['sort'] = get_perguntas(arg['resposta'], session['lista'], session['sort'], session['ordem'])
            return resposta
        else:
            return 'Não Existe Nenhuma sessão'


if __name__ == '__main__':
    
    app.run(debug=False, port=5000)