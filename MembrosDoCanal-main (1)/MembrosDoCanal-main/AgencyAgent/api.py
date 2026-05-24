from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_game_score(nome_time):
    conn = sqlite3.connect('futebol_jogos.db')
    c = conn.cursor()
    #nome_time = nome_time.lower()
    c.execute('SELECT * FROM jogos WHERE nome_time = ?', (nome_time,))
    result = c.fetchone()
    conn.close()
    if result:
        keys = ["jogo_id", "status", "time_da_casa", "time_da_casa_gols", "time_visitante", "time_visitante_gols"]
        return dict(zip(keys, result[1:]))
    else:
        return {"nome_time": nome_time, "score": "unknown"}

@app.route('/')
def home():
    return jsonify({
        'message': 'Bem-vindo a API dos resultados dos jogos do Campeoanto Brasileiro. Use /placar?time=<nome_time> para buscar placares de jogos.'
    })

@app.route('/placar', methods=['GET'])
def score():
    nome_time = request.args.get('time', '')
    if not nome_time:
        return jsonify({'error': 'Missing team name'}), 400
    score = get_game_score(nome_time)
    return jsonify(score)

if __name__ == '__main__':
    app.run(debug=True)