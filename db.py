import sqlite3

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('mercado.db')
c = conn.cursor()

# Criação da tabela vendedores
c.execute('''
    CREATE TABLE IF NOT EXISTS vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        usuario TEXT NOT NULL,
        senha TEXT NOT NULL
    )
''')

# Salvar as mudanças e fechar a conexão com o banco de dados
conn.commit()
conn.close()