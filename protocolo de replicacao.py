import rpyc
from rpyc.utils.server import ThreadedServer
import threading
import os
import time

id = input("Informe o ID entre 1 e N")
id = int(id)
porta = 5000 + id

fila = []
x = 0
if id == 1:
    p = True
else:
    p = False
h = {}
a = False

def interface():
    global fila
    global a
    global h
    global x
    global id
    global p
    while True:
        f = int(input("Digite que operação deseja fazer\n 1)ler o valor atual de x\n 2)ler o historico de alteracoes de x\n 3)alterar o valor de x\n 4)finalizar o programa\n"))
        if f == 1:
            print("A variavel x e: {}\n".format(x))  
        if f == 2:
            print("Historico de atualizacoes:{}\n".format(h))
        if f == 3:
            #verificação
            if not p:
                #tomando as possiveis listas de outros processos que ja entraram antes dele na fila
                for i in range(4):
                        id_teste_k = i+1
                        if id_teste_k!=id:
                            conn = rpyc.connect('localhost',5000+i+1)
                            fila_atual = conn.root.exposed_fila()
                            if len(fila_atual) != 0:                            
                                for elemento in fila_atual:
                                    fila.append(elemento)
                            conn.close()
                fila.append(id)
                fila = list(dict.fromkeys(fila))
                while True:
                    time.sleep(1)
                    for i in range(4):
                        id_teste_i = i+1
                        if id_teste_i != id:
                            conn = rpyc.connect('localhost',5000+id_teste_i)
                            p_teste = conn.root.exposed_tem_chapeu()
                            conn.close()
                            if p_teste:
                                conn = rpyc.connect('localhost',5000+id_teste_i)
                                a_teste = conn.root.exposed_esta_escrevendo()
                                conn.close()
                                break
                    if not a_teste and len(fila) == 1:
                        copia_primaria.exposed_pegar_chapeu(copia_primaria,id_teste_i)
                        a = True
                        fila.remove(id)
                        for i in range(4):
                            id_teste_j = i+1
                            if id_teste_j!=id:
                                conn = rpyc.connect('localhost',5000+id_teste_j)
                                conn.root.exposed_atualizar_fila(id)
                                conn.close()
                        break
            else:
                a = True
            c = input("Digite o novo valor que deseja para a variavel x\n")
            c = int(c)
            copia_primaria.exposed_modificar_variavel_local(copia_primaria,c)
            while True:
                c = input("Digite o novo valor que deseja para variavel local, caso nao queira digite a letra n\n")
                if c == 'n':
                    print("Finalizando as alteracoes, enviando o valor final para os outros processos\n")
                    for k in range (4):
                        id_teste=k+1
                        if id_teste!= id:
                            conn = rpyc.connect('localhost',5000+id_teste)
                            conn.root.exposed_modificar_variavel_global(id,x)
                            conn.close()
                    a = False
                    break                       
                else:
                    c = int(c)
                    copia_primaria.exposed_modificar_variavel_local(copia_primaria,c)
       
        if f == 4:
            print("Encerrando...")
            os._exit(1)
    
#funções classe copia primaria
class copia_primaria(rpyc.Service):
    
   
    def exposed_pegar_chapeu(self,id_chapeu):
        global p
        conn = rpyc.connect('localhost',5000+id_chapeu)
        conn.root.exposed_tira_chapeu()
        conn.close()
        p = True
    
    
    def exposed_fila(self):
        global fila
        return fila
    
    
    def exposed_atualizar_fila(self,id_retirado):
        global fila
        try:
            fila.remove(id_retirado)
        except:
            pass 
                    
    
    def exposed_modificar_variavel_global(self,id,mod):
        global x
        global h
        x = mod
        aux1 = []
        aux2 = {}
        try:
            for i in h[id]:
                aux1.append(i)
        except:
            pass
        aux1.append(x)
        aux2[id] = aux1
        h.update(aux2) 
        
               
    def exposed_tira_chapeu(self):
        global p
        p = False
    
       
    def exposed_tem_chapeu(self):
        global p
        return p
    
    
    def exposed_esta_escrevendo(self):
        global a
        return a
                        
    
    def exposed_modificar_variavel_local(self,novo_valor):
        global x
        global id
        global p 
        x = novo_valor
        aux1 = []
        aux2 = {}
        try:
            for i in h[id]:
                aux1.append(i)
        except:
            pass
        aux1.append(x)
        aux2[id] = aux1
        h.update(aux2) 


t1 = threading.Thread(target = interface,args=())
t1.start()
server = ThreadedServer(copia_primaria,port = porta)
server.start()
                    
                
