import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, Tk
from tkcalendar import DateEntry
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

#verficar se o usuário existe
def verificar_usuario(nome_usuario, senha):
    conn = sqlite3.connect('mercado.db')
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE nome_usuario = ? AND senha = ?", (nome_usuario, senha))
    usuario = c.fetchone()
    conn.close()
    return usuario

#adiciona usuário no db
def adicionar_usuario(nome_usuario, senha):
    try:
        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()
        c.execute("INSERT INTO usuarios (nome_usuario, senha) VALUES (?, ?)", (nome_usuario, senha))
        conn.commit()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Nome de usuário já existente. Por favor, escolha outro nome.")
    finally:
        conn.close()

#tela do cadastro
def tela_cadastro_usuario():
    cadastro = tk.Toplevel()
    cadastro.title("Cadastro de Usuário")

    tk.Label(cadastro, text="Nome de Usuário:").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(cadastro, text="Senha:").grid(row=1, column=0, padx=10, pady=5)

    nome_usuario_entry = tk.Entry(cadastro)
    nome_usuario_entry.grid(row=0, column=1, padx=10, pady=5)
    senha_entry = tk.Entry(cadastro, show="*")
    senha_entry.grid(row=1, column=1, padx=10, pady=5)

    def cadastrar_usuario():
        nome_usuario = nome_usuario_entry.get()
        senha = senha_entry.get()
        if nome_usuario and senha:
            adicionar_usuario(nome_usuario, senha)
            cadastro.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

    botao_cadastrar = tk.Button(cadastro, text="Cadastrar", command=cadastrar_usuario)
    botao_cadastrar.grid(row=2, column=1, padx=10, pady=10)

#validação de login
def fazer_login(nome_usuario, senha, tela_login):
    if nome_usuario and senha:
        usuario = verificar_usuario(nome_usuario, senha)
        if usuario:
            messagebox.showinfo("Sucesso", f"Bem-vindo, {nome_usuario}!")
            tela_login.destroy()  # Fecha a tela de login após o login bem-sucedido
            abrir_aplicativo_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
    else:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

#tela de login 
def tela_login():
    tela_login = tk.Tk()
    tela_login.title("Login")

    tk.Label(tela_login, text="Nome de Usuário:").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(tela_login, text="Senha:").grid(row=1, column=0, padx=10, pady=5)

    nome_usuario_entry = tk.Entry(tela_login)
    nome_usuario_entry.grid(row=0, column=1, padx=10, pady=5)
    senha_entry = tk.Entry(tela_login, show="*")
    senha_entry.grid(row=1, column=1, padx=10, pady=5)

    botao_login = tk.Button(tela_login, text="Login", command=lambda: fazer_login(nome_usuario_entry.get(), senha_entry.get(), tela_login))
    botao_login.grid(row=2, column=1, padx=10, pady=10)

    botao_cadastro = tk.Button(tela_login, text="Cadastre-se", command=tela_cadastro_usuario)
    botao_cadastro.grid(row=2, column=0, padx=10, pady=10)

    tela_login.mainloop()

#def que abre o aplicativo princpal somente após o login feito
def abrir_aplicativo_principal():
    #adcionar item ao banco de dados
    def adicionar_item():
        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()

        c.execute("INSERT INTO itens VALUES (:nomeprod, :quantidade, :preco, :marca)",
                {'nomeprod': nomeprod.get(), 'quantidade': quantidade.get(), 'preco': preco.get(), 'marca': marca.get()})

        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Item adicionado com sucesso!")

        atualizar_itens()

        # Frame para filtros
        filter_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(filter_frame, text="CPF do Cliente:").grid(row=0, column=0, padx=5, pady=5)
        global cpf_entry
        cpf_entry = tk.Entry(filter_frame)
        cpf_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Data Início:").grid(row=0, column=2, padx=5, pady=5)
        global data_inicio_entry
        data_inicio_entry = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        data_inicio_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="Data Fim:").grid(row=0, column=4, padx=5, pady=5)
        global data_fim_entry
        data_fim_entry = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        data_fim_entry.grid(row=0, column=5, padx=5, pady=5)

        # Botão para gerar o PDF
        botao_gerar_pdf = tk.Button(root, text="Gerar Relatório PDF", command=gerar_pdf_relatorio_compras)
        botao_gerar_pdf.pack(pady=10) 
    

    def verificar_estoque_baixo(lista_itens, limite_minimo=8):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT nomeprod, quantidade FROM itens WHERE quantidade <= ?", (limite_minimo,))
            itens_baixo_estoque = c.fetchall()
            if itens_baixo_estoque:
                mensagem = "Atenção! Os seguintes itens estão com estoque baixo:\n"
                for item in itens_baixo_estoque:
                    mensagem += f"- {item[0]}: apenas {item[1]} em estoque\n"
                messagebox.showwarning("Estoque Baixo", mensagem)
            else:
                messagebox.showinfo("Estoque", "Todos os itens estão acima do limite mínimo de estoque.")
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao verificar o estoque: {e}")
        finally:
            if conn:
                conn.close()


    #função para atualizar a lista de itens
    def atualizar_itens():

        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()

        c.execute("SELECT * FROM itens")
        itens = c.fetchall()

        lista_itens.delete(*lista_itens.get_children())

        for item in itens:
            lista_itens.insert('', 'end', values=item)

        conn.commit()
        conn.close()

    #barra de pesquisar itens
    def pesquisar_itens():

        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()

        c.execute("SELECT * FROM itens WHERE nomeprod LIKE ?", ('%' + pesquisa.get() + '%',))
        itens = c.fetchall()

        lista_itens.delete(*lista_itens.get_children())

        for item in itens:
            lista_itens.insert('', 'end', values=item)

        conn.commit()
        conn.close()

    root = tk.Tk()
    root.title("Mercado Solidário")
    root.geometry("1600x900")

    #remover um item selecionado
    def remover_item():

        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()

        item_selecionado = lista_itens.selection()[0]
        item = lista_itens.item(item_selecionado)['values']

        c.execute("DELETE FROM itens WHERE nomeprod = ? AND quantidade = ? AND preco = ? AND marca = ?", item)

        conn.commit()
        conn.close()

        lista_itens.delete(item_selecionado)

        messagebox.showinfo("Sucesso", "Item removido com sucesso!")

    def gerar_pdf_lista_itens():
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT nomeprod, quantidade, preco, marca FROM itens")
            dados_itens = c.fetchall()
            
            caminho_desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            nome_arquivo = os.path.join(caminho_desktop, 'lista_de_itens.pdf')
            c_pdf = canvas.Canvas(nome_arquivo, pagesize=letter)
            
            caminho_logo = 'C:/Users/paulo.dutra/Desktop/projetos/iave.jpeg'
            c_pdf.drawImage(caminho_logo, 40, 750, width=100, height=50)
            
            c_pdf.setFont("Helvetica-Bold", 16)
            c_pdf.drawString(150, 760, 'Lista de Itens')
            
            c_pdf.setStrokeColorRGB(0, 0, 0)
            c_pdf.line(40, 740, 560, 740)
            
            c_pdf.setFont("Helvetica-Bold", 10)
            c_pdf.drawString(50, 720, 'Nome Produto')
            c_pdf.drawString(150, 720, 'Quantidade')
            c_pdf.drawString(250, 720, 'Preço')
            c_pdf.drawString(350, 720, 'Marca')
            c_pdf.line(40, 710, 560, 710)
            c_pdf.setFont("Helvetica", 8)
            y = 700
            for item in dados_itens:
                c_pdf.drawString(50, y, str(item[0]))
                c_pdf.drawString(150, y, str(item[1]))
                c_pdf.drawString(250, y, str(item[2]))
                c_pdf.drawString(350, y, str(item[3]))
                y -= 20
            c_pdf.save()
            messagebox.showinfo('Sucesso', 'A lista de itens foi criada com sucesso na sua área de trabalho!')
            
        except Exception as e:
            messagebox.showerror('Erro', f'Ocorreu um erro ao gerar a lista de itens: {e}')
        finally:
            if conn:
                conn.close()
    #abas ttk notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    #aba para adicionar itens
    aba1 = ttk.Frame(notebook)
    notebook.add(aba1, text="Adicionar Itens")

    tk.Label(aba1, text="Nome Prod.").grid(row=0)
    tk.Label(aba1, text="Quantidade").grid(row=1)
    tk.Label(aba1, text="Preço").grid(row=2)
    tk.Label(aba1, text="Marca").grid(row=3)

    nomeprod = tk.Entry(aba1)
    nomeprod.grid(row=0, column=1)
    quantidade = tk.Entry(aba1)
    quantidade.grid(row=1, column=1)
    preco = tk.Entry(aba1)
    preco.grid(row=2, column=1)
    marca = tk.Entry(aba1)
    marca.grid(row=3, column=1)

    botao_adicionar = tk.Button(aba1, text="Adicionar Item", command=adicionar_item)
    botao_adicionar.grid(row=4, column=1, pady=10)

    #aba para visualizar os itens
    aba2 = ttk.Frame(notebook)
    notebook.add(aba2, text="Visualizar Itens")

    frame_botoes = tk.Frame(aba2)
    frame_botoes.pack(side=tk.BOTTOM, fill=tk.X)

    botao_verificar_estoque = tk.Button(frame_botoes, text="Verificar Estoque Baixo", command=lambda: verificar_estoque_baixo(lista_itens_aba5))
    botao_verificar_estoque.pack(side=tk.LEFT, padx=6, pady=6)

    botao_remover = tk.Button(frame_botoes, text="Remover Item", command=remover_item)
    botao_remover.pack(side=tk.LEFT, padx=5, pady=5)

    #entry para botão de pesquisa na aba "Visualizar Itens"
    pesquisa = tk.Entry(aba2)
    pesquisa.pack()
    botao_pesquisar = tk.Button(aba2, text="Pesquisar", command=pesquisar_itens)
    botao_pesquisar.pack()

    botao_gerar_pdf = tk.Button(aba2, text="Gerar PDF Lista de Itens", command=gerar_pdf_lista_itens)
    botao_gerar_pdf.pack()


    #lista para exibir os itens

    lista_itens = ttk.Treeview(aba2, columns=("Nome Prod.", "Quantidade", "Preço", "Marca"), show='headings')
    lista_itens.heading("Nome Prod.", text="Nome", anchor=tk.CENTER)
    lista_itens.heading("Quantidade", text="Quantidade", anchor=tk.CENTER)
    lista_itens.heading("Preço", text="Preço", anchor=tk.CENTER)
    lista_itens.heading("Marca", text="Marca", anchor=tk.CENTER)
    lista_itens.pack(fill='both', expand=True)
    lista_itens.column("Nome Prod.", anchor=tk.CENTER)
    lista_itens.column("Quantidade", anchor=tk.CENTER)
    lista_itens.column("Preço", anchor=tk.CENTER)
    lista_itens.column("Marca", anchor=tk.CENTER)

    atualizar_itens()

    def abrir_formulario_atualizacao():
        item_selecionado = lista_itens.selection()
        if not item_selecionado:
            messagebox.showinfo("Aviso", "Selecione um item para atualizar.")
            return
        item_selecionado = item_selecionado[0]
        item = lista_itens.item(item_selecionado, 'values')

        # Cria uma nova janela para atualização
        janela_atualizacao = tk.Toplevel()
        janela_atualizacao.title("Atualizar Item")

        # Adiciona campos de entrada para atualização
        tk.Label(janela_atualizacao, text="Nome Prod.").grid(row=0, column=0)
        nomeprod_entry = tk.Entry(janela_atualizacao)
        nomeprod_entry.grid(row=0, column=1)
        nomeprod_entry.insert(0, item[0])

        tk.Label(janela_atualizacao, text="Quantidade").grid(row=1, column=0)
        quantidade_entry = tk.Entry(janela_atualizacao)
        quantidade_entry.grid(row=1, column=1)
        quantidade_entry.insert(0, item[1])

        tk.Label(janela_atualizacao, text="Preço").grid(row=2, column=0)
        preco_entry = tk.Entry(janela_atualizacao)
        preco_entry.grid(row=2, column=1)
        preco_entry.insert(0, item[2])

        tk.Label(janela_atualizacao, text="Marca").grid(row=3, column=0)
        marca_entry = tk.Entry(janela_atualizacao)
        marca_entry.grid(row=3, column=1)
        marca_entry.insert(0, item[3])

        # Botão para salvar as atualizações
        botao_salvar = tk.Button(janela_atualizacao, text="Salvar Atualizações", command=lambda: salvar_atualizacoes(item_selecionado, nomeprod_entry.get(), quantidade_entry.get(), preco_entry.get(), marca_entry.get(), janela_atualizacao))
        botao_salvar.grid(row=4, column=1, pady=10)

    #dfe que salva as infos no db
    def salvar_atualizacoes(item_selecionado, nome, quantidade, preco, marca, janela):
        try:
            conn = sqlite3.connect('mercado.db')
            c = conn.cursor()
            c.execute("UPDATE itens SET nomeprod = ?, quantidade = ?, preco = ?, marca = ? WHERE nomeprod = ?",
                    (nome, quantidade, preco, marca, lista_itens.item(item_selecionado, 'values')[0]))
            conn.commit()
            messagebox.showinfo("Sucesso", "Item atualizado com sucesso!")
            janela.destroy()
            atualizar_itens()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o item: {e}")
        finally:
            conn.close()

    botao_atualizar_item = tk.Button(frame_botoes, text="Atualizar Cadastro do Item", command=abrir_formulario_atualizacao)
    botao_atualizar_item.pack(side=tk.LEFT, padx=5, pady=5)

    #aba para adicionar clientes
    aba3 = ttk.Frame(notebook)
    notebook.add(aba3, text="Adicionar Clientes")

    #labels e grids para os get de info dos clientes
    tk.Label(aba3, text="CPF").grid(row=0)
    tk.Label(aba3, text="Nome").grid(row=1)
    tk.Label(aba3, text="Telefone").grid(row=2)
    tk.Label(aba3, text="Endereço").grid(row=3)
    tk.Label(aba3, text="Crédito").grid(row=4)

    cpf = tk.Entry(aba3)
    cpf.grid(row=0, column=1)
    nome = tk.Entry(aba3)
    nome.grid(row=1, column=1)
    telefone = tk.Entry(aba3)
    telefone.grid(row=2, column=1)
    endereco = tk.Entry(aba3)
    endereco.grid(row=3, column=1)
    credito = tk.Entry(aba3)
    credito.grid(row=4, column=1)

    #quarta aba para visualizar os clientes
    aba4 = ttk.Frame(notebook)
    notebook.add(aba4, text="Visualizar Clientes")

    #aba de vendas
    aba5 = tk.Frame(notebook)
    notebook.add(aba5, text='Realizar venda')

    def adicionar_cliente():
        cpf_valor = cpf.get()
        if len(cpf_valor) == 11 and cpf_valor.isdigit():  # Verifica se o CPF tem 11 dígitos e contém apenas números
            conn = sqlite3.connect('mercado.db')
            c = conn.cursor()

            c.execute("INSERT INTO clientes VALUES (:cpf, :nome, :telefone, :endereco, :credito)",
                    {'cpf': cpf_valor, 'nome': nome.get(), 'telefone': telefone.get(), 'endereco': endereco.get(), 'credito': credito.get()})

            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso!")
        else:
            messagebox.showerror("Erro", "CPF inválido. Por favor, insira um CPF com 11 dígitos.")

    frame_botoes_clientes = tk.Frame(aba4)
    frame_botoes_clientes.pack(side=tk.BOTTOM, fill=tk.X)

    #def para abrir o formulário de atualização do cliente
    def abrir_formulario_atualizacao_cliente():
        cliente_selecionado = lista_clientes.selection()
        if not cliente_selecionado:
            messagebox.showinfo("Aviso", "Selecione um cliente para atualizar.")
            return
        cliente_selecionado = cliente_selecionado[0]
        cliente = lista_clientes.item(cliente_selecionado, 'values')
        janela_atualizacao_cliente = tk.Toplevel()
        janela_atualizacao_cliente.title("Atualizar Cliente")
        tk.Label(janela_atualizacao_cliente, text="CPF").grid(row=0, column=0)
        cpf_entry = tk.Entry(janela_atualizacao_cliente)
        cpf_entry.grid(row=0, column=1)
        cpf_entry.insert(0, cliente[0])
        tk.Label(janela_atualizacao_cliente, text="Nome").grid(row=1, column=0)
        nome_entry = tk.Entry(janela_atualizacao_cliente)
        nome_entry.grid(row=1, column=1)
        nome_entry.insert(0, cliente[1])
        tk.Label(janela_atualizacao_cliente, text="Telefone").grid(row=2, column=0)
        telefone_entry = tk.Entry(janela_atualizacao_cliente)
        telefone_entry.grid(row=2, column=1)
        telefone_entry.insert(0, cliente[2])
        tk.Label(janela_atualizacao_cliente, text="Endereço").grid(row=3, column=0)
        endereco_entry = tk.Entry(janela_atualizacao_cliente)
        endereco_entry.grid(row=3, column=1)
        endereco_entry.insert(0, cliente[3])

        tk.Label(janela_atualizacao_cliente, text="Crédito").grid(row=4, column=0)
        credito_entry = tk.Entry(janela_atualizacao_cliente)
        credito_entry.grid(row=4, column=1)
        credito_entry.insert(0, cliente[4])
        botao_salvar_cliente = tk.Button(janela_atualizacao_cliente, text="Salvar Atualizações", command=lambda: salvar_atualizacoes_cliente(cliente_selecionado, cpf_entry.get(), nome_entry.get(), telefone_entry.get(), endereco_entry.get(), credito_entry.get(), janela_atualizacao_cliente))
        botao_salvar_cliente.grid(row=5, column=1, pady=10)

    #def para salvar as atualizações do cliente no banco de dado
    def salvar_atualizacoes_cliente(cliente_selecionado, cpf, nome, telefone, endereco, credito, janela):
        try:
            conn = sqlite3.connect('mercado.db')
            c = conn.cursor()
            c.execute("UPDATE clientes SET nome = ?, telefone = ?, endereco = ?, credito = ? WHERE cpf = ?",
                    (nome, telefone, endereco, credito, cpf))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cadastro do cliente atualizado com sucesso!")
            janela.destroy()
            atualizar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o cadastro do cliente: {e}")
        finally:
            conn.close()

    #botão para abrir o formulário de atualização do cliente
    botao_atualizar_cliente = tk.Button(frame_botoes_clientes, text="Atualizar Cadastro do Cliente", command=abrir_formulario_atualizacao_cliente)
    botao_atualizar_cliente.pack(side=tk.LEFT, padx=5, pady=5)

    #botão adicionar cliente
    botao_adicionar_cliente = tk.Button(aba3, text="Adicionar Cliente", command=adicionar_cliente)
    botao_adicionar_cliente.grid(row=5, column=1, pady=10)

    #função para atualizar a lsita de clientes
    def atualizar_clientes():

        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()

        c.execute("SELECT * FROM clientes")
        clientes = c.fetchall()

        lista_clientes.delete(*lista_clientes.get_children())

        for cliente in clientes:
            lista_clientes.insert('', 'end', values=cliente)

        conn.commit()
        conn.close()

    #barra de pesquisa dos clientes
    def pesquisar_clientes():

        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()

        c.execute("SELECT * FROM clientes WHERE nome LIKE ?", ('%' + pesquisa_cliente.get() + '%',))
        clientes = c.fetchall()

        lista_clientes.delete(*lista_clientes.get_children())

        for cliente in clientes:
            lista_clientes.insert('', 'end', values=cliente)

        conn.commit()
        conn.close()

    #remover um cliente selecionado
    def remover_cliente():

        conn = sqlite3.connect('mercado.db')
        c = conn.cursor()

        if lista_clientes.selection():
            cliente_selecionado = lista_clientes.selection()[0]
            cliente = lista_clientes.item(cliente_selecionado)['values']

            c.execute("DELETE FROM clientes WHERE cpf = ?", (cliente[0],))

            conn.commit()
            conn.close()

            lista_clientes.delete(cliente_selecionado)

            messagebox.showinfo("Sucesso", "Cliente removido com sucesso!")
        else:
            messagebox.showinfo("Erro", "Nenhum cliente selecionado!")

    #barra pesquis cliente
    pesquisa_cliente = tk.Entry(aba4)
    pesquisa_cliente.pack()
    botao_pesquisar_cliente = tk.Button(aba4, text="Pesquisar", command=pesquisar_clientes)
    botao_pesquisar_cliente.pack()

    #botaõ para remover o cliente
    botao_remover_cliente = tk.Button(frame_botoes_clientes, text="Remover Cliente", command=remover_cliente)
    botao_remover_cliente.pack(side=tk.LEFT, padx=5, pady=5)

    lista_clientes = ttk.Treeview(aba4, columns=("CPF", "Nome", "Telefone", "Endereço", "Crédito"), show='headings')
    lista_clientes.heading("CPF", text="CPF", anchor=tk.CENTER)
    lista_clientes.heading("Nome", text="Nome", anchor=tk.CENTER)
    lista_clientes.heading("Telefone", text="Telefone", anchor=tk.CENTER)
    lista_clientes.heading("Endereço", text="Endereço", anchor=tk.CENTER)
    lista_clientes.heading("Crédito", text="Crédito", anchor=tk.CENTER)
    lista_clientes.pack(fill='both', expand=True)
    lista_clientes.column("CPF", anchor=tk.CENTER)
    lista_clientes.column("Nome", anchor=tk.CENTER)
    lista_clientes.column("Telefone", anchor=tk.CENTER)
    lista_clientes.column("Endereço", anchor=tk.CENTER)
    lista_clientes.column("Crédito", anchor=tk.CENTER)


    atualizar_clientes()

    #def para fazer conexão ao db
    def conectar_db():
        return sqlite3.connect('mercado.db')

    # Def para atualizar os itens de compras
    def atualizar_itens_compra(lista_itens):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT * FROM itens")
            itens = c.fetchall()
            lista_itens.delete(*lista_itens.get_children())
            for item in itens:
                lista_itens.insert('', 'end', values=item)
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        finally:
            if conn:
                conn.close()

    # Def para ajustar os itens que não selecionavam no tree
    def on_item_selected(event, lista_itens):
        selected_items = lista_itens.selection()
        if selected_items:  # Verifica se há itens selecionados
            for selected_item in selected_items:
                item = lista_itens.item(selected_item)['values']
                quantidade = simpledialog.askinteger("Quantidade", f"Digite a quantidade para {item[0]}:", initialvalue=1)
                if quantidade and quantidade > 0:
                    cpf_cliente = simpledialog.askstring("CPF", "Digite o CPF do cliente:")
                    if cpf_cliente:
                        comprar_item(cpf_cliente, item, quantidade, lista_itens)
        else:
            messagebox.showinfo("Aviso", "Nenhum item selecionado.")

    # Def para vender um item
    def comprar_item(cpf_cliente, item, quantidade, lista_itens):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT credito, quantidade FROM clientes, itens WHERE clientes.cpf = ? AND itens.nomeprod = ?", (cpf_cliente, item[0]))
            resultado = c.fetchone()
            if resultado:
                credito_cliente, quantidade_disponivel = resultado
                credito_cliente = float(credito_cliente)
                quantidade_disponivel = int(quantidade_disponivel)
                preco_total_item = float(item[2]) * quantidade

                if quantidade_disponivel >= quantidade:
                    if credito_cliente >= preco_total_item:
                        data_atual = datetime.now().strftime('%d-%m-%y')
                        hora_atual = datetime.now().strftime('%H:%M:%S')
                        c.execute("UPDATE clientes SET credito = credito - ? WHERE cpf = ?", (preco_total_item, cpf_cliente))
                        
                        c.execute("INSERT INTO carrinho (cpf_cliente, nome_produto, quantidade, preco_total, data_compra, hora_compra, marca_produto) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (cpf_cliente, item[0], quantidade, preco_total_item, data_atual, hora_atual, item[3]))  # Inclui a marca do produto
                        
                        c.execute("UPDATE itens SET quantidade = quantidade - ? WHERE nomeprod = ?", (quantidade, item[0]))
                        
                        messagebox.showinfo("Sucesso", "Compra realizada com sucesso!")
                        conn.commit()
                    else:
                        messagebox.showinfo("Erro", "Crédito insuficiente!")
                else:
                    messagebox.showinfo("Erro", "Quantidade insuficiente em estoque!")
            else:
                messagebox.showinfo("Erro", "CPF não encontrado ou item não disponível!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        finally:
            if conn:
                conn.close()

    # Def auxiliar/complementar para compra de itens
    def comprar_item_executar(lista_itens):
        selected_items = lista_itens.selection()
        if selected_items:
            for selected_item in selected_items:
                item = lista_itens.item(selected_item)['values']
                quantidade = simpledialog.askinteger("Quantidade", f"Digite a quantidade para {item[0]}:", initialvalue=1)
                if quantidade and quantidade > 0:
                    cpf_cliente = simpledialog.askstring("CPF", "Digite o CPF do cliente:")
                    if cpf_cliente:
                        comprar_item(cpf_cliente, item, quantidade, lista_itens)
        else:
            messagebox.showinfo("Aviso", "Nenhum item selecionado.")

    # Configuração do Treeview para seleção múltipla na aba 5
    lista_itens_aba5 = ttk.Treeview(aba5, columns=('Nome', 'Preço', 'Quantidade', 'Marca'), show='headings', selectmode='extended')
    lista_itens_aba5.heading('Nome', text='Nome')
    lista_itens_aba5.heading('Preço', text='Preço')
    lista_itens_aba5.heading('Quantidade', text='Quantidade')
    lista_itens_aba5.heading('Marca', text='Marca')

    lista_itens_aba5.pack()

    # Botão para comprar itens
    botao_comprar = tk.Button(aba5, text="Comprar Itens", command=lambda: comprar_item_executar(lista_itens_aba5))
    botao_comprar.pack()

    # Botão para atualizar a lista de vendas
    botao_atualizar_aba5 = tk.Button(aba5, text="Atualizar Itens", command=lambda: atualizar_itens_compra(lista_itens_aba5))
    botao_atualizar_aba5.pack()

    atualizar_itens_compra(lista_itens_aba5)

    # Def que atualiza o carrinho/histórico de compras
    def atualizar_carrinho(lista_carrinho):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT cpf_cliente, nome_produto, quantidade, preco_total, data_compra, hora_compra, marca_produto FROM carrinho")
            carrinho = c.fetchall()
            lista_carrinho.delete(*lista_carrinho.get_children())
            for item in carrinho:
                lista_carrinho.insert('', 'end', values=item)
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        finally:
            if conn:
                conn.close()

    # Aba do carrinho
    aba_carrinho = tk.Frame(notebook)
    notebook.add(aba_carrinho, text='Histórico de compra')

    # Treeview na aba do carrinho
    lista_carrinho = ttk.Treeview(aba_carrinho, columns=('CPF Cliente', 'Nome Produto', 'Quantidade', 'Preço Total', 'Data', 'Hora', 'Marca'), show='headings')
    lista_carrinho.heading('CPF Cliente', text='CPF Cliente')
    lista_carrinho.heading('Nome Produto', text='Nome Produto')
    lista_carrinho.heading('Quantidade', text='Quantidade')
    lista_carrinho.heading('Preço Total', text='Preço Total')
    lista_carrinho.heading('Marca', text='Marca')
    lista_carrinho.heading('Data', text='Data')
    lista_carrinho.heading('Hora', text='Hora')
    lista_carrinho.pack(expand=True, fill='both')

    # Barra de pesquisa no carrinho/histórico
    def pesquisar_no_carrinho(pesquisa, lista_carrinho):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT cpf_cliente, nome_produto, quantidade, preco_total, data_compra, hora_compra, marca_produto FROM carrinho WHERE cpf_cliente LIKE ?", ('%' + pesquisa + '%',))
            itens_filtrados = c.fetchall()
            lista_carrinho.delete(*lista_carrinho.get_children())
            for item in itens_filtrados:
                lista_carrinho.insert('', 'end', values=item)
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        finally:
            if conn:
                conn.close()

    entrada_pesquisa = tk.Entry(aba_carrinho)
    entrada_pesquisa.pack()

    botao_pesquisar = tk.Button(aba_carrinho, text="Pesquisar", command=lambda: pesquisar_no_carrinho(entrada_pesquisa.get(), lista_carrinho))
    botao_pesquisar.pack()

    botao_atualizar_carrinho = tk.Button(aba_carrinho, text="Atualizar Histórico", command=lambda: atualizar_carrinho(lista_carrinho))
    botao_atualizar_carrinho.pack()

    atualizar_carrinho(lista_carrinho)

        #pdf das compras
    def gerar_pdf_relatorio_compras():
            try:
                conn = conectar_db()
                c = conn.cursor()
                c.execute("SELECT cpf_cliente, nome_produto, quantidade, preco_total, data_compra, hora_compra, marca_produto FROM carrinho")
                dados_compras = c.fetchall()
                
                caminho_desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                nome_arquivo = os.path.join(caminho_desktop, 'relatorio_de_compras.pdf')
                c_pdf = canvas.Canvas(nome_arquivo, pagesize=letter)
                
                c_pdf.drawImage('C:/Users/Aluno/Desktop/projetos/iave.jpg', 40, 750, width=100, height=50)
                c_pdf.setFont("Helvetica-Bold", 16)
                c_pdf.drawString(150, 760, 'Relatório de Compras')
                
                c_pdf.setStrokeColorRGB(0, 0, 0)
                c_pdf.line(40, 740, 560, 740)
                
                c_pdf.setFont("Helvetica-Bold", 10)
                c_pdf.drawString(50, 720, 'CPF Cliente')
                c_pdf.drawString(150, 720, 'Nome Produto')
                c_pdf.drawString(250, 720, 'Quantidade')
                c_pdf.drawString(350, 720, 'Preço Total')
                c_pdf.drawString(450, 720, 'Data')
                c_pdf.drawString(500, 720, 'Hora')
                c_pdf.drawString(550, 720, 'Marca')
                c_pdf.line(40, 710, 560, 710)
                c_pdf.setFont("Helvetica", 8)
                y = 700
                for item in dados_compras:
                    c_pdf.drawString(50, y, str(item[0]))
                    c_pdf.drawString(150, y, str(item[1]))
                    c_pdf.drawString(250, y, str(item[2]))
                    c_pdf.drawString(350, y, str(item[3]))
                    c_pdf.drawString(450, y, str(item[4]))
                    c_pdf.drawString(500, y, str(item[5]))
                    c_pdf.drawString(550, y, str(item[6]))
                    y -= 20
                c_pdf.save()
                messagebox.showinfo('Sucesso', 'O relatório de compras foi criado com sucesso na sua área de trabalho!')
                
            except Exception as e:
                messagebox.showerror('Erro', f'Ocorreu um erro ao gerar o relatório de compras: {e}')
            finally:
                if conn:
                    conn.close()


    botao_gerar_pdf = tk.Button(aba_carrinho, text="Gerar Relatório PDF", command=gerar_pdf_relatorio_compras)
    botao_gerar_pdf.pack()

    root.mainloop()

# Início do programa
tela_login()

