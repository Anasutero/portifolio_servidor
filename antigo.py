# Navega no diretorio
import os
# Manipula e Cria um servidir (sem framework)
from http.server import SimpleHTTPRequestHandler
# Gerencia a comunicação com o cliente
import socketserver
from urllib.parse import parse_qs
 
# Criação de Classe com artificio de HTTP
class MyMandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        # Tenta o Código abaixo
        try:
            # Tenta abrir o arquivo index.html
            f = open(os.path.join(path, 'index.html'), 'r')
            # Se existir, envia o conteudo do arquivo
            # Envia para o Cliente o Código de Sucesso
            self.send_response(200)
            # Forma de Tratmento
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Leitura do HTML
            self.wfile.write(f.read().encode('utf-8'))
            # Finaliza para não contnuar o carregamento
            f.close
            return None
        # Caso dê erro
        except FileNotFoundError:
            pass
 
        return super().list_directory(path)
   
    def do_GET(self):
        if self.path =='/login':
            try:
                with open(os.path.join(os.getcwd(), 'login.html'), 'r') as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("content-type","text/html")
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))          
        # Caso dê erro
            except FileNotFoundError:
                pass
           
        elif self.path == '/login_failed':
            # Responde ao cliente a mensagem de login/senha incorreta
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
           
            # Lê o conteudo da pagina login.html
            with open(os.path.join(os.getcwd(), 'login.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()
               
            # adiciona a mensagem de erro no conteudo da pagina
            mensagem = "Login e/ou senha incorreta. Tente novamente"
            content = content.replace('<!-- Mensagem de erro será inserida aqui -->',
                                      f'<div class="error-message">{mensagem}</div>')
           
            # Envia o conteudo modificado para o cliente
            self.wfile.write(content.encode('utf-8'))    
       
        else:
            super().do_GET()
           
    def usuario_existente(self, login, senha):
        #verifica se o login já existe
        with open('dados_login.txt', 'r', encoding='utf-8') as file:
            for line in file:
                stored_login, stored_senha = line.strip().split(';')
                if login == stored_login:
                    return senha == stored_senha
        return False
 
    def do_POST(self):
        # Verifica se a rota é "/enviar_login"
        if self.path == '/enviar_login':
            # Obtém o comprimento do corpo da requesição
            content_length = int(self.headers['content-Length'])
            # Lê o corpo da requisição
            body = self.rfile.read(content_length).decode('utf-8')
            # Parseia os dados o formulário
            form_data = parse_qs(body)
 
            print(form_data)
            # Exibe os dados no terminal
            print("DADOS DO FORMULÁRIO")
            print("E-mail:", form_data.get('email', [''])[0])
            print("Senha:", form_data.get('senha', [''])[0])
           
            # verifica se o usuario já existe
            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]
           
            if self.usuario_existente(login, senha):
                with open(os.path.join(os.getcwd(), 'existente.html'), 'r', encoding='utf-8') as existe:
                    content_file = existe.read()
                # responde ao cliente indicando que o usuario já consta nos registros
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                #mensagem = f"Usuario {login} já consta em nossos registros"
                self.wfile.write(content_file.encode('utf-8'))
           
            else:
                if any(line.startswith(f"{login};") for line in open("dados_login.txt", "r", encoding="UTF-8")):
                    self.send_response(302)
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    return # adicionando um return para evitar a execução
               
                else:
                    with open ("dados_login.txt", "a", encoding="UTF-8") as arquivo:
                        login = form_data.get('email',[''])[0]
                        senha = form_data.get('senha',[''])[0]
                        arquivo.write(f"{login};{senha}\n")
   
                    with open(os.path.join(os.getcwd(), 'resposta.html'), 'r', encoding='utf-8') as cadastro_file:
                        contente = cadastro_file.read()
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(contente.encode('utf-8'))
        else:
            # Se não for a rota "/enviar_login", continua com o comportamento padrão
            super(MyMandler,self).do_POST()
 
 
# Define o IP  e a porta a serem utilizados
endereco_ip = "0.0.0.0"
porta = 8000
 
# Cria um servidor na porta e IP especificos
with socketserver.TCPServer((endereco_ip, porta), MyMandler) as httpd:
    print(f"Servidor iniciando em {endereco_ip}:{porta}")
    # Mantém o servidor em execução
    httpd.serve_forever()
