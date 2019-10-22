from flask import Flask, session, request
from flask_session import Session
import requests
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(20)

"""def get_cursos(profissao):

    url = "https://OIC-DIGIDEV-ladsedigdev.integration.ocp.oraclecloud.com:443/ic/api/integration/v1/flows/rest/HELLO_WORLD/1.0/names"
    querystring = {"profissao":profissao}
    headers = {'Authorization': "Basic b2ljZGVtb3VzZXI6T3JhY2xlMTIzNDU2"}
    lista = json.loads(requests.request("GET", url, headers=headers, params=querystring))
    return lista
"""

@app.route('/set')
def set():
    prof = request.args.get('id')
    session['id'] = prof
    return session['id']

@app.route('/get')
def get():
    if session.get('id') is not None:
        return session.get('id')
    else:
        return 'não tem sessão'

if __name__ == '__main__':
    
    app.run(debug=True)