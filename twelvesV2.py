from flask import Flask, session, request
from flask_session import Session
import requests
import os
import json

app = Flask(__name__)
#Cria uma chave aletoria para cada sessao
app.secret_key = os.urandom(20)

#funcao que traz todos os cursos associadas a tag pesquisada
def get_cursos(tag):

    """url = "https://OIC-DIGIDEV-ladsedigdev.integration.ocp.oraclecloud.com:443/ic/api/integration/v1/flows/rest/HELLO_WORLD/1.0/names"
    querystring = {"profissao":profissao}
    headers = {'Authorization': "Basic b2ljZGVtb3VzZXI6T3JhY2xlMTIzNDU2"}
    lista = json.loads(requests.request("GET", url, headers=headers, params=querystring))"""
    lista = json.loads('{"items":[{"key_word":"CD","Question":"SQL","Father":"CD","Sort":1},{"key_word":"CD","Question":"RP","Father":"CD","Sort":2},{"key_word":"CD","Question":"Estatistica","Father":"CD","Sort":3},{"key_word":"CD","Question":"MOD","Father":"Estatistica","Sort":3}]}')['items']
    return lista

#fucao que traz as perguntas na ordem, verifica se a resposta foi sim ou nao 
#adiciona os topicos com resposta negativa na trilha e remove os filhos desse topico
def get_perguntas(param, lista, pai, sort, ordem):
    perguntas = [t for t in lista if t['Sort'] == sort]
    if param != 'Sim':
        session['trilha'].append(perguntas[ordem]['Question'])
        for i in range(ordem, len(perguntas)):
            if ordem <= len(perguntas) - 1:
                if perguntas[i]['Father'] == pai:
                    sort += 1
                    ordem = 0
                else:
                    ordem += 1
            else:
                print('aqui2')
                sort += 1
                ordem = 0
    else:
        if ordem <= len(perguntas) - 1:
            if ordem == len(perguntas) - 1:
                sort += 1
                ordem = 0
            else:
                ordem += 1
    if max(t['Sort'] for t in lista) >= sort:
        resposta = 'Você conhece ' + str([t['Question'] for t in lista if t['Sort'] == sort][ordem]) + '?'
        return resposta, ordem, sort
    else:
        return 'Essa é sua lista ' + str(session['trilha']), 0 ,1 

#Cria o path relativo do endpoint
@app.route('/tag', methods=['GET', 'POST'])
def tag():
    #verifica se a chamada é um GET ou um POST
    if request.method == 'GET':
        session['father'] = request.args.get('tag')
        session['lista'] = get_cursos(session['father'])
        if len(session['lista']) > 0:
            session['sort'] = 1
            session['trilha'] = []
            session['ordem'] = 0
            pergunta = str([t['Question'] for t in session['lista'] if t['Sort'] == session['sort'] and t['Father'] == session['father']][0])
            return 'Você Conhece ' + pergunta + '?'
        else: 
            return 'Profissão não encontrada'
    else:
        if session.get('lista') is not None:
            resposta = ''
            resposta, session['ordem'], session['sort'] = get_perguntas(request.args.get('resposta'), session['lista'], session['father'], session['sort'], session['ordem'])
            return resposta
        else:
            return 'Não Existe Nenhuma sessão'


if __name__ == '__main__':
    
    app.run(debug=True)