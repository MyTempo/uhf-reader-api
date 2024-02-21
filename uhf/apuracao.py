# code self.info
# "m_code": code,   # código da etiqueta em formato hexadecimal


import glob
import copy
import os
import os
from uhf.task import InventoryThread


tempos = {}

ID_leitor = "201" #indentificador do leitor
# diretorio = 'C:\Cronometragem' 
diretorio = "C:/Users/USUARIO/Desktop/TAG_INFO"
diretorio_apurado = "C:/Users/USUARIO/Desktop/APURADO_INFO" #diretorio do arquivo apurado


def apurar() :
    

    # Get a list of all files in the folder
    files = glob.glob(diretorio + '/*.txt')

    # Classifique a lista de arquivos pelo horário de modificação
    files.sort(key=os.path.getmtime)

    try:
    # Get the most recent file
        most_recent_file = files[-1]
    except:
        ('Arquivo não encontrado!')
        
    # Open the file
    tag = most_recent_file
    file_path = f'C:\Cronometragem\{tag}'
    
    # cria txt na pasta
    file_path = os.path.join(diretorio_apurado, "Apurado_info.txt")


    try:
        with open(most_recent_file) as arq:
            # Lê o conteúdo do arquivo como uma string e divide em linhas
            rows = arq.read().splitlines()
            
            # # Percorre as linhas do arquivo
            # tagint = str(tag["m_code"]) + str(tag["timestamp"])

            for row in rows:
                tagint = row
                
                # Extrai o número do atleta e o tempo da linha
                numero_atleta = int(tagint[4:19])
                tempo_atleta = str(tagint[20:31])

                # Adiciona o tempo do atleta ao dicionário
                tempos.setdefault(numero_atleta, []).append(tempo_atleta)
                
    except FileNotFoundError:
        print("Arquivo não encontrado")
    except ValueError:
        print("Erro ao ler o arquivo: valor inválido encontrado")
            
            
    # Percorre o dicionário e imprime os tempos de cada atleta
    for numero_atleta, lista_tempos in tempos.items():

                #separa as variáveis com os dados que vão ser usados
                search_string = horabase = "8:00"

                # retorna os tempos apurados em referencia a hora base
                def search_timestamps(search_string, lista):
                    return [val for val in lista if val.startswith(search_string)]

                values = search_timestamps(search_string, lista_tempos)

                indice = len(values)
                res = lista_tempos[indice:]
                primeiro = res[0]
                ultimo = res[-1]

                int = 1
                
                if int == 1:
                    tempo = primeiro
                elif 0:
                    tempo = ultimo
                        
                soma = ID_leitor + numero_atleta + tempo
                soma = soma.replace(" ", "") #remove espaços

                # Adiciona no arquivo txt na pasta
                file_path = os.path.join(diretorio_apurado, "Apurado.txt")
                with open(file_path, "a") as file:

                    file.write(soma)
                    file.write("\n")