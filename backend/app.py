from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

def get_conn():
    # il MySQL nel container Docker (sezione 1)
    return mysql.connector.connect(
        host="127.0.0.1", user="root",
        password="root", database="musica")

def riga_to_dict(r):
    return {"id": r[0], "nome": r[1],
            "secondi": float(r[2]),
            "durata_min": float(r[3])}

@app.get("/api/brani")
def lista_brani():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, secondi, "
                "secondi / 60 AS durata_min "
                "FROM brani")
    righe = cur.fetchall()
    cur.close(); conn.close()
    brani = [riga_to_dict(r) for r in righe]
    return jsonify(brani), 200



@app.get("/api/brani/<int:id>")
def dettaglio(id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, nome, secondi, "
                "secondi / 60 AS durata_min "
                "FROM brani WHERE id = %s", (id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    if r is None:
        return jsonify({"errore": "non trovato"}), 404
    return jsonify(riga_to_dict(r)), 200

# nuova playlist: i dati arrivano nel BODY
# {"utente": "Rossi", "totale": 8.00, "brani": [1, 4]}
@app.post("/api/playlist")
def crea_playlist():
    dati = request.get_json()        # JSON → dizionario
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO playlist (utente, totale) "
                "VALUES (%s, %s)",
                (dati["utente"], dati["totale"]))
    nuovo_id = cur.lastrowid         # id appena creato
    for pid in dati["brani"]:      # una riga per brano
        cur.execute("INSERT INTO righe_playlist "
                    "(playlist_id, brano_id) VALUES (%s, %s)",
                    (nuovo_id, pid))
    conn.commit()                    # salva tutto insieme
    cur.close(); conn.close()
    return jsonify({"id": nuovo_id}), 201