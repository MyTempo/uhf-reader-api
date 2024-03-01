import os

try:
    from uhf.configurations import *
    from uhf.helpersClass import *
except:
    from configurations import *
    from helpersClass import *

class TagClass:
    def __init__(self, tag_type) -> None:
        self.tag_type = tag_type
        self.session = Helpers.generateRandomNum(3)
        self.fileName = self.generateTagFileName()
        self.filePath = os.path.join(PATH_READER_DATA, self.fileName)
       
        self.DirPath = ""
        if(self.tag_type == "brute"):
            self.DirPath = PATH_BRUTE_DATA
            self.filePath = os.path.join(PATH_BRUTE_DATA, self.fileName)
        elif(self.tag_type == "refined"):
            self.DirPath = PATH_REF_DATA
            self.filePath = os.path.join(PATH_REF_DATA, self.fileName)


        

    def generateTagFileName(self):
       
        if(self.tag_type == "brute"):
            file_name = f'MyTempo-Bruto-Sess-{self.session} T-{TIME_FORMAT_2}.txt'
        elif(self.tag_type == "refined"):
            file_name = f'MyTempo-Ref-Sess-{self.session} T-{TIME_FORMAT_2}.txt'
        else:
            file_name = self.tag_type
        return file_name
    
    def makeFile(self):
        try:
           
            with open(self.filePath, 'r') as arquivo:
                print(f'O arquivo "{self.filePath}" já existe.')
                return
        except FileNotFoundError:
           
            with open(self.filePath, 'w') as arquivo:
                print(f'O arquivo "{self.filePath}" foi criado.')
                

    def makeDir(self):
        if not os.path.exists(PATH_READER_DATA):
            os.makedirs(PATH_READER_DATA)
        if not os.path.exists(PATH_BRUTE_DATA):
            os.makedirs(PATH_BRUTE_DATA)
        if not os.path.exists(PATH_REF_DATA):
            os.makedirs(PATH_REF_DATA)
            
    def saveOnFile(self, tag_info, type_f="brute"):
        if os.path.exists(self.filePath):
            with open(self.filePath, "a") as file:
                for tag in tag_info:
                    
                    soma = self.session + str(tag["m_code"]) + str(tag["timestamp"]) 
                    soma = soma.replace(" ", "") 
                    file.write(soma)
                    file.write("\n")
        else:
            print("Caminho: ", self.filePath, " não existe")
