from flask import Flask, session, request
from flask_session import Session
import requests
import os
import json

app = Flask(__name__)
#Cria uma chave aletória para cada sessão
app.secret_key = os.urandom(20)

def get_cursos(tag):

    """url = "https://OIC-DIGIDEV-ladsedigdev.integration.ocp.oraclecloud.com:443/ic/api/integration/v1/flows/rest/HELLO_WORLD/1.0/names"
    querystring = {"profissao":profissao}
    headers = {'Authorization': "Basic b2ljZGVtb3VzZXI6T3JhY2xlMTIzNDU2"}
    lista = json.loads(requests.request("GET", url, headers=headers, params=querystring))"""
    lista = [1,tag,3]
    return lista

#Cria o path relativo do endpoint
@app.route('/tag', methods=['GET', 'POST'])
def tag():
    #verifica se a chamada é um GET ou um POST
    if request.method == 'GET':
        session['lista'] = get_cursos(request.args.get('tag'))
        return str(session['lista'][0])
    else:
        if session.get('lista') is not None:
            return str(session.get('lista')[1])
        else:
            return 'Não Existe Nenhuma sessão'


if __name__ == '__main__':
    
    app.run(debug=True)