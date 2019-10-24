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

    url = "https://eybftnzpirfzozn-siriusdb.adb.us-ashburn-1.oraclecloudapps.com/ords/madhacks/sirius/key_word"
    querystring = {"KEYWORD":tag}
    response = requests.request("GET", url, params=querystring)
    lista = json.loads(response.text)['items']
    return lista

#fucao que traz as perguntas na ordem, verifica se a resposta foi sim ou nao 
#adiciona os topicos com resposta negativa na trilha e remove os filhos desse topico
def get_perguntas(param, lista, pai, sort, ordem):
    perguntas = [t for t in lista if t['sort'] == sort]
    if param != 'Sim':
        if ordem <= len(perguntas) - 1:
            if perguntas[ordem]['father'] == pai:
                result = [p for p in perguntas if p['father'] == perguntas[ordem]['question']]
                for j in result:
                    session['trilha'].append(j['id_question_pk'])
                sort += 1
                ordem = 0
            if ordem == len(perguntas) - 1:
                ordem = 0
                sort += 1
            else:
                session['trilha'].append(perguntas[ordem]['id_question_pk'])
                ordem += 1
        else:
            sort += 1
            ordem = 0
    else:
        if ordem <= len(perguntas) - 1:
            if ordem == len(perguntas) - 1:
                sort += 1
                ordem = 0
            else:
                ordem += 1
    if max(t['sort'] for t in lista) >= sort:
        resposta = 'Você conhece ' + str([t['question'] for t in lista if t['sort'] == sort][ordem]) + '?'
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
            pergunta = str([t['question'] for t in session['lista'] if t['sort'] == session['sort'] and t['father'] == session['father']][0])
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