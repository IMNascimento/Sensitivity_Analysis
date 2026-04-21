import gsi
import grpc

project = None

try:
    project = gsi.OpenProject(r"C:\caminho\para\seu_projeto.gsz")

    # chamadas da API aqui

except grpc.RpcError as e:
    print(f"Erro gRPC: {e.code()} - {e.details()}")
except Exception as e:
    print(f"Erro geral: {e}")
finally:
    if project:
        project.Close()


#teste de chamada de API interna
#import gsi

#project = gsi.OpenProject(r"C:\Projetos\meu_modelo.gsz")
#print("Projeto aberto com sucesso")
#project.Close()
#print("Projeto fechado")