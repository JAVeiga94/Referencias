import sys
from cx_Freeze import setup, Executable

# Inclua aqui os arquivos adicionais que seu programa precisa, como imagens, ícones, etc.
include_files = ['C:/Users/paulo.dutra/Desktop/projetos/mercado.db', 'C:/Users/paulo.dutra/Desktop/projetos/iave.jpeg']  # Exemplo: 'data.db', 'config.json'

# Inclua aqui os pacotes adicionais que seu programa precisa
packages = ['tkinter', 'sqlite3', 'reportlab']

# Dependendo do seu sistema operacional, defina a base
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # Isso remove a janela do console

executables = [
    Executable(
        'Mercado Solidário V2.py',
        base=base,
        icon='caminho/para/seu/icone.ico',  # Opcional: adicione um ícone ao seu executável
    )
]

setup(
    name='Mercado Solidário',
    version='1.0',
    description='None',
    options={
        'build_exe': {
            'packages': packages,
            'include_files': include_files,
        }
    },
    executables=executables
)