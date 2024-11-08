import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
from cryptography.fernet import Fernet
from bcrypt import hashpw, gensalt, checkpw
import datetime
import base64
import os
from bson.objectid import ObjectId

# Conexão com MongoDB Atlas
uri = "mongodb+srv://arthursodoni:Mui5BtJ9KNj9jFnB@cluster0.7ez9y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['ProjetoDeBD']
usuarios = db["usuarios"]
registros_medicos = db["registros_medicos"]

# Teste de conexão
try:
    client.admin.command('ping')
    print("Pinged your deployment. Conectado ao MongoDB!")
except Exception as e:
    print(e)

# Definir chave Fernet fixa
CHAVE_FERNET = "_3aL-VQ8cLdBaFZ1jC91PxwrZpUwL2cTezDZr1NoRQ4="

# Função para criar registro médico
def criar_registro(nome_paciente, historico_medico, tratamentos, id_medico):
    fernet = Fernet(CHAVE_FERNET)
    
    # Criptografa os dados
    registro_criptografado = {
        "id_medico": id_medico,
        "nome_paciente": fernet.encrypt(nome_paciente.encode()).decode(),
        "historico_medico": fernet.encrypt(historico_medico.encode()).decode(),
        "tratamentos": fernet.encrypt(tratamentos.encode()).decode(),
        "data_criacao": datetime.datetime.utcnow()
    }
    
    # Insere o registro no banco de dados
    registros_medicos.insert_one(registro_criptografado)
    messagebox.showinfo("Sucesso", "Registro médico criado com sucesso!")

# Função para acessar registro médico
def acessar_registro(id_registro):
    fernet = Fernet(CHAVE_FERNET)
    
    try:
        # Tenta converter o ID do registro para ObjectId
        id_registro_obj = ObjectId(id_registro)
        registro = registros_medicos.find_one({"_id": id_registro_obj})

        if registro:
            nome_paciente = fernet.decrypt(registro["nome_paciente"].encode()).decode()
            historico_medico = fernet.decrypt(registro["historico_medico"].encode()).decode()
            tratamentos = fernet.decrypt(registro["tratamentos"].encode()).decode()
            
            messagebox.showinfo("Registro Médico", f"Nome: {nome_paciente}\nHistórico: {historico_medico}\nTratamentos: {tratamentos}")
        else:
            messagebox.showwarning("Aviso", "Registro não encontrado.")
    
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao acessar o registro: {e}")

# Função para criar usuário com senha hasheada
def criar_usuario(nome, email, senha):
    senha_hash = hashpw(senha.encode(), gensalt())
    usuario = {
        "nome": nome,
        "email": email,
        "senha_hash": senha_hash.decode(),
        "2fa_secret": base64.b32encode(os.urandom(10)).decode('utf-8'),  # Chave secreta 2FA
        "permissoes": ["criar", "acessar", "compartilhar"]
    }
    usuarios.insert_one(usuario)
    messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")

# Função para autenticar usuário
def autenticar_usuario(email, senha):
    usuario = usuarios.find_one({"email": email})
    
    if usuario and checkpw(senha.encode(), usuario["senha_hash"].encode()):
        messagebox.showinfo("Sucesso", "Autenticação bem-sucedida!")
        return True
    else:
        messagebox.showerror("Erro", "Falha na autenticação.")
        return False

# Interface Gráfica com Tkinter
root = tk.Tk()
root.title("Sistema de Registros Médicos")

# Funções de Interface
def interface_criar_usuario():
    nome = entry_nome.get()
    email = entry_email.get()
    senha = entry_senha.get()
    criar_usuario(nome, email, senha)

def interface_autenticar_usuario():
    email = entry_email.get()
    senha = entry_senha.get()
    autenticar_usuario(email, senha)

def interface_criar_registro():
    nome_paciente = entry_nome_paciente.get()
    historico_medico = entry_historico.get()
    tratamentos = entry_tratamentos.get()
    id_medico = entry_id_medico.get()

    if nome_paciente and historico_medico and tratamentos and id_medico:
        criar_registro(nome_paciente, historico_medico, tratamentos, id_medico)
    else:
        messagebox.showerror("Erro", "Preencha todos os campos.")

def interface_acessar_registro():
    id_registro = entry_id_registro.get()

    if id_registro:
        acessar_registro(id_registro)
    else:
        messagebox.showerror("Erro", "ID do registro não fornecido.")

# Título Criar Usuário
titulo_criar_usuario = tk.Label(root, text="CRIAR USUÁRIO", font=("Arial", 18, "bold"), fg="red")
titulo_criar_usuario.grid(row=0, column=0, columnspan=2, pady=20)

# Campos de Entrada para Usuário
tk.Label(root, text="Nome", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10)
entry_nome = tk.Entry(root, font=("Arial", 14), width=40)
entry_nome.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Email", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10)
entry_email = tk.Entry(root, font=("Arial", 14), width=40)
entry_email.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Senha", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10)
entry_senha = tk.Entry(root, font=("Arial", 14), show="*", width=40)
entry_senha.grid(row=3, column=1, padx=10, pady=10)

# Botões de Ação para Usuário
btn_criar_usuario = tk.Button(root, text="Criar Usuário", font=("Arial", 14), command=interface_criar_usuario, width=20, height=2)
btn_criar_usuario.grid(row=5, column=0, pady=10)

btn_autenticar = tk.Button(root, text="Autenticar", font=("Arial", 14), command=interface_autenticar_usuario, width=20, height=2)
btn_autenticar.grid(row=5, column=1, pady=10)

# Título da criação de registros após os botões de criação de usuário
titulo_criar_registro = tk.Label(root, text="CRIAÇÃO DE REGISTROS", font=("Arial", 18, "bold"), fg="blue")
titulo_criar_registro.grid(row=6, column=0, columnspan=2, pady=20)

# Campos de Entrada para Registro Médico
tk.Label(root, text="Nome do Paciente", font=("Arial", 14)).grid(row=7, column=0, padx=10, pady=10)
entry_nome_paciente = tk.Entry(root, font=("Arial", 14), width=40)
entry_nome_paciente.grid(row=7, column=1, padx=10, pady=10)

tk.Label(root, text="Histórico Médico", font=("Arial", 14)).grid(row=8, column=0, padx=10, pady=10)
entry_historico = tk.Entry(root, font=("Arial", 14), width=40)
entry_historico.grid(row=8, column=1, padx=10, pady=10)

tk.Label(root, text="Tratamentos", font=("Arial", 14)).grid(row=9, column=0, padx=10, pady=10)
entry_tratamentos = tk.Entry(root, font=("Arial", 14), width=40)
entry_tratamentos.grid(row=9, column=1, padx=10, pady=10)

tk.Label(root, text="ID do Médico", font=("Arial", 14)).grid(row=10, column=0, padx=10, pady=10)
entry_id_medico = tk.Entry(root, font=("Arial", 14), width=40)
entry_id_medico.grid(row=10, column=1, padx=10, pady=10)

# Botões de Ação para Registro Médico
btn_criar_registro = tk.Button(root, text="Criar Registro", font=("Arial", 14), command=interface_criar_registro, width=20, height=2)
btn_criar_registro.grid(row=11, column=0, pady=10)

# Título de Acesso a Registros após o botão de Criar Registro
titulo_acessar_registro = tk.Label(root, text="ACESSO A REGISTROS", font=("Arial", 18, "bold"), fg="green")
titulo_acessar_registro.grid(row=12, column=0, columnspan=2, pady=20)

# Campos de Entrada para Acesso a Registro
tk.Label(root, text="ID do Registro", font=("Arial", 14)).grid(row=13, column=0, padx=10, pady=10)
entry_id_registro = tk.Entry(root, font=("Arial", 14), width=40)
entry_id_registro.grid(row=13, column=1, padx=10, pady=10)

# Botão de Ação para Acesso a Registro
btn_acessar_registro = tk.Button(root, text="Acessar Registro", font=("Arial", 14), command=interface_acessar_registro, width=20, height=2)
btn_acessar_registro.grid(row=14, column=0, pady=10)

root.mainloop()