from flask import Flask, session, request
from flask_session import Session
import requests
import os
import json

app = Flask(__name__)
#Cria uma chave aletoria para cada sessao
app.secret_key = os.urandom(20)

#funcao que traz todas as perguntas
def get_todas_perguntas(tag):

    url = "https://eybftnzpirfzozn-siriusdb.adb.us-ashburn-1.oraclecloudapps.com/ords/madhacks/sirius/key_word"
    querystring = {"KEYWORD":tag}
    response = requests.request("GET", url, params=querystring)
    lista = json.loads(response.text)['items']
    return lista

#funcao que traz recomendacao
def get_recomendacao(respostas):

    recomendacao = []
    url = "https://eybftnzpirfzozn-siriusdb.adb.us-ashburn-1.oraclecloudapps.com/ords/madhacks/sirius/recomendation"
    for f in respostas:
        querystring = {"id":f[0], "resposta":f[1]}
        req = json.loads(requests.request("GET", url, params=querystring).text)['items']
        for i in req:
            recomendacao.append(i)
    return recomendacao

#fucao que traz as perguntas na ordem, verifica se a resposta foi sim ou nao 
#adiciona os topicos com resposta negativa na trilha e remove os filhos desse topico
def get_perguntas(param, lista, pai, sort, ordem):
    perguntas = [t for t in lista if t['sort'] == sort]
    if ordem <= len(perguntas) - 1:
        if perguntas[ordem]['father'] == pai:
            if param == 'No':
                session['trilha'].append([perguntas[ordem]['id'], param])
                result = [p for p in perguntas if p['father'] != pai]
                if len(result) > 0: 
                    for j in result:
                        session['trilha'].append([j['id'],j['respostas'].split(',')[-1]])
                sort += 1
                ordem = 0        
            else:
                session['trilha'].append([perguntas[ordem]['id'], param])
                result = [p for p in perguntas if p['father'] != pai]
                if len(result) > 0:
                    ordem += 1
                else:
                    ordem = 0
                    sort += 1
        else:
            if ordem < len(perguntas) -1:
                session['trilha'].append([perguntas[ordem]['id'], param])
                ordem += 1
            else:
                session['trilha'].append([perguntas[ordem]['id'], param])
                ordem = 0
                sort += 1
    if sort <= max(t['sort'] for t in lista):
        pergunta = [t['question'] for t in lista if t['sort'] == sort][ordem]
        respostas = [t['respostas'] for t in lista if t['sort'] == sort][ordem]
        retorno = {"Pergunta" : pergunta, "Respostas": respostas.split(',')}
        return retorno, ordem, sort
    else:
        return {"Recomendacao":get_recomendacao(session['trilha'])}, 0 ,1 

#Cria o path relativo do endpoint
@app.route('/tag', methods=['GET', 'POST'])
def tag():
    #verifica se a chamada é um GET ou um POST
    if request.method == 'GET':
        session['father'] = request.args.get('tag')
        session['lista'] = get_todas_perguntas(session['father'])
        if len(session['lista']) > 0:
            session['sort'] = 1
            session['trilha'] = []
            session['ordem'] = 0
            pergunta = [t['question'] for t in session['lista'] if t['sort'] == session['sort'] and t['father'] == session['father']][0]
            respostas = [t['respostas'] for t in session['lista'] if t['sort'] == session['sort'] and t['father'] == session['father']][0]
            return {"Pergunta": pergunta, "Resposta": respostas.split(',')}
        else: 
            return 'Profissão não encontrada'
    else:
        if session.get('lista') is not None:
            resposta = ''
            arg = request.get_json()
            resposta, session['ordem'], session['sort'] = get_perguntas(arg['resposta'], session['lista'], session['father'], session['sort'], session['ordem'])
            return resposta
        else:
            return 'Não Existe Nenhuma sessão'


if __name__ == '__main__':
    
    app.run(debug=False, host='0.0.0.0', port=5000)