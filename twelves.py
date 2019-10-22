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
    lista = json.loads('{"items":[{"key_word":"CD","Question":"SQL","Father":"CD","Sort":1},{"key_word":"CD","Question":"RP","Father":"CD","Sort":2},{"key_word":"CD","Question":"Estatistica","Father":"CD","Sort":3},{"key_word":"CD","Question":"MOD","Father":"Estatistica","Sort":4}]}')['items']
    return lista

#fucao que traz as perguntas na ordem, verifica se a resposta foi sim ou nao 
#adiciona os topicos com resposta negativa na trilha e remove os filhos desse topico
def get_perguntas(param, lista, ordem):
    length = len(lista)
    prox = ordem + 1
    if param != 'Sim':
        for i in range(ordem,length):
            if i <= len(lista[i]) is not None:
                if lista[i]['Father'] == lista[ordem]['Question']:
                    lista.pop(i)
        session['trilha'].append(lista[ordem]['Question'])
    if ordem >= (len(lista) - 1):
        return 'Essa é a sua Trilha:' + str(session['trilha'])
    session['ordem'] = prox
    return 'Você Conhece ' + lista[prox]['Question'] + '?'

#Cria o path relativo do endpoint
@app.route('/tag', methods=['GET', 'POST'])
def tag():
    #verifica se a chamada é um GET ou um POST
    if request.method == 'GET':
        session['lista'] = get_cursos(request.args.get('tag'))
        session['ordem'] = 0
        session['trilha'] = []
        return 'Você Conhece ' + session['lista'][0]['Question'] + '?'
    else:
        if session.get('lista') is not None:
            return get_perguntas(request.args.get('resposta'), session['lista'], session['ordem'])
        else:
            return 'Não Existe Nenhuma sessão'


if __name__ == '__main__':
    
    app.run(debug=True)