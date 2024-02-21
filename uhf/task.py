from ctypes import *
from threading import Thread
import time
import datetime
from uhf.error import UhfException

from uhf.handle import Api
from uhf.struct import TagInfo
from uhf.utils import hex_array_to_string

api = Api()


#realizar a leitura de tags RFID.

class InventoryThread(Thread):
    
    def __init__(self, hComm,  timeout):    
        
        super(InventoryThread, self).__init__()
        self.info = {} #dicionario das informações das tags
        self.hComm = hComm
        self.timeout = timeout
        self.flag = False

    def run(self): #faz a leitura
        try:
            while True:
                try:
                    self.tagInfo = TagInfo()

                    if self.flag:
                        break

                    res = api.GetTagUii(self.hComm, self.tagInfo, 1000)
                    
                    lens = self.tagInfo.m_len
                    byte_array = list(self.tagInfo.m_code)
                    byte_array = byte_array[:lens]
                    code = hex_array_to_string(byte_array, lens)
                    
                    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3] #pega a hora do aparelho computador

                    #Se o identificador já existir no dicionário, ele atualiza os campos
                    if self.info.get(code):
                        if self.tagInfo.m_ant > 0 and self.tagInfo.m_ant <= 4:
                            self.info[code]["m_counts"][self.tagInfo.m_ant -1] += 1
                        self.info[code]["m_rssi"] = self.tagInfo.m_rssi / 10
                        self.info[code]["m_channel"] = self.tagInfo.m_channel
                        self.info[code]["timestamp"] = current_time
                    else: #Senão ele cria uma nova entrada de dicionário para a etiqueta e preenche os campos
                        m_counts = [0, 0, 0, 0]
                        m_counts[self.tagInfo.m_ant - 1] = 1

                        self.info[code] = {
                            'm_no': self.tagInfo.m_no,           # número de série da etiqueta
                            'm_rssi': self.tagInfo.m_rssi / 10,  # nível de sinal recebido da etiqueta, convertido para dBm
                            "m_counts": m_counts,                # lista com as contagens de leitura para cada antena (a posição correspondente à antena utilizada para esta leitura é inicializada com 1 e as outras posições com 0)
                            "m_channel": self.tagInfo.m_channel, # canal utilizado para a leitura da etiqueta
                            "m_crc": list(self.tagInfo.m_crc),   # lista com os valores de CRC da etiqueta    
                            "m_pc": list(self.tagInfo.m_pc),     # lista com os valores de PC da etiqueta
                            "m_len": self.tagInfo.m_len,         # comprimento do código da etiqueta
                            "m_code": code,                      # código da etiqueta em formato hexadecimal
                            "timestamp": current_time            # hora em que a leitura da etiqueta foi realizada (no formato "HH:MM:SS.%f")[:-3]
                        }
                        # dicionario = self.tagInfo

                except Exception as e:
                    if str(e) in ["-241", "-238"]:
                        continue
                    raise UhfException("O leitor responde a um erro de formato de dados ou Aguardando resposta do leitor expirou")

                if res == -249:
                    break
                if self.tagInfo.m_ant == 0  or self.tagInfo.m_ant > 4:
                    continue
        except Exception as e:
            api.InventoryStop(self.hComm, 1000)
            
            
    def terminate(self):
        self.flag = True
