import mysql.connector

# Connessione al database
conn = mysql.connector.connect(
    host="sql7.freesqldatabase.com",  # Host del database
    user="sql7765718",                # Username del database
    password="aKDVVF7wAK",            # Password del database
    database="sql7765718",            # Nome del database
    port=3306                          # Porta del database (di solito 3306 per MySQL)
)

# Funzione per ottenere i dati
def db_get(diz):
    cur = conn.cursor(dictionary=True)  # Uso del dizionario per ottenere le colonne come chiavi
    query = "SELECT * FROM film"  # Query di esempio, puoi cambiarla con altre personalizzazioni
    cur.execute(query)
    dati = cur.fetchall()
    cur.close()  # Chiudiamo il cursore
    return dati

# Funzione per inserire i dati
def db_set(diz):
    cur = conn.cursor()
    query = "INSERT INTO film (title, director, year) VALUES (%s, %s, %s)"
    values = (diz['title'], diz['director'], diz['year'])  # Parametri da passare
    cur.execute(query, values)
    conn.commit()  # Commit per rendere permanenti le modifiche
    cur.close()  # Chiudiamo il cursore

# Funzione per aggiornare i dati
def db_update(diz):
    cur = conn.cursor()
    query = "UPDATE film SET title = %s, director = %s, year = %s WHERE id = %s"
    values = (diz['title'], diz['director'], diz['year'], diz['id'])  # Parametri da passare
    cur.execute(query, values)
    conn.commit()  # Commit per rendere permanenti le modifiche
    cur.close()  # Chiudiamo il cursore

# Funzione per cancellare i dati
def db_delete(diz):
    cur = conn.cursor()
    query = "DELETE FROM film WHERE id = %s"
    values = (diz['id'],)  # Parametro da passare
    cur.execute(query, values)
    conn.commit()  # Commit per rendere permanenti le modifiche
    cur.close()  # Chiudiamo il cursore

# Funzione principale per testare il tutto
if __name__ == '__main__':
    diz = {
        'title': 'The Matrix',
        'director': 'The Wachowskis',
        'year': 1999
    }
    
    # Chiamata per inserire un nuovo record
    db_set(diz)
    
    # Chiamata per ottenere i dati (questo restituirà tutti i film dalla tabella)
    risultati = db_get(diz)
    print(risultati)
    
    # Modificare un record (esempio di aggiornamento)
    diz_update = {
        'id': 1,  # Supponiamo che l'id del film che vogliamo aggiornare sia 1
        'title': 'The Matrix Reloaded',
        'director': 'The Wachowskis',
        'year': 2003
    }
    db_update(diz_update)
    
    # Cancellare un record (esempio di eliminazione)
    diz_delete = {'id': 1}
    db_delete(diz_delete)
