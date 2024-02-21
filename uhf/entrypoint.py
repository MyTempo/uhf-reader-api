import time
from turtle import Terminator
import serial
import serial.tools.list_ports
import os

from ctypes import *
from copy import deepcopy
from flask_restful import reqparse
from flask import Flask, current_app, render_template
from flask_cors import CORS
from uhf.conf import ERROR_CODE
from uhf.struct import DeviceFullInfo, DevicePara
from uhf.task import InventoryThread
from uhf.utils import res_jsonify
from uhf.handle import Api
from uhf.task import * 
from uhf.apuracao import *
from uhf.configurations import *
from uhf.tagClass import *


api = Api()

class UHFServices:
    
    '''cria uma aplicação Flask, define a biblioteca CORS e carrega uma biblioteca DLL necessária   
    para controlar o leitor'''
    
    app = Flask(
        __name__, 
        static_url_path='', 
        static_folder="../UHFPrimeReaderWeb", 
        template_folder='../UHFPrimeReaderWeb')
    CORS(app)
    app.lib = cdll.LoadLibrary("./UHFPrimeReader.dll")   
    def serve(self, host="0.0.0.0", port="5000", threaded=True, debug=False):
        self.app.run(host=host, port=port, threaded=threaded, debug=debug)

S = UHFServices()
bruteTag = TagClass("brute")
bruteTag.makeFile()

refinedTag = TagClass("refined")
refinedTag.makeFile()

@UHFServices.app.route("/", methods=["get"])
def index():
    return render_template("index.html")

#indentifica as portas COM
@UHFServices.app.route("/getPorts", methods=["post"])
def getPorts(): 
    comList = list(serial.tools.list_ports.comports())
    comAttr = [list(comList[i])[0] for i in range(len(comList))]
    return res_jsonify(0, ports = comAttr)

#Conectar à porta serial define a velocidade
@UHFServices.app.route("/OpenDevice", methods=["post"])
def OpenDevice(): 
    """Conectar à porta serial"""
    parser = reqparse.RequestParser()
    parser.add_argument('strComPort', type=str, default="0xFF")
    parser.add_argument('Baudrate', type=int, default=4)
    args = parser.parse_args()

    baud = {0: 9600, 1: 19200, 2:38400, 3: 57600, 4: 115200}
    
    ser = serial.Serial()
    ser.baudrate = baud[args["Baudrate"]] 
    ser.port = args["strComPort"]

    try:
        ser.open()
    except Exception as e:
        msgB="O leitor já está aberto, feche o leitor primeiro"
        return res_jsonify(1001, msgB=msgB)
    else:
        ser.close()

    hComm = c_int()
    strComPort = c_char_p(args["strComPort"].encode('utf-8'))
    Baudrate = c_ubyte(args["Baudrate"])

    res = api.OpenDevice(hComm, strComPort, Baudrate)
    if res != 0:
        log, msgB = [f"serial {args['strComPort']} open fail"] * 2
        return res_jsonify(res, msgB= msgB, log=log, success=False)

    current_app.hComm = hComm.value
    log = f"O leitor é aberto com sucesso, o número da porta serial：{args['strComPort']}"
    return res_jsonify(res, log=log, hComm = hComm.value)

#Conectar a uma porta de rede
@UHFServices.app.route("/OpenNetConnection", methods=["post"])
def OpenNetConnection():
    """Conectar porta de rede"""
    parser = reqparse.RequestParser()
    parser.add_argument('ip', type=str, default="192.168.1.200")
    parser.add_argument('port', type=int, required=True, help="Porta do leitor de cartão de entrada")
    parser.add_argument('timeoutMs', type=int, required=True)
    args = parser.parse_args()

    hComm = c_int()
    ip = c_char_p(args["ip"].encode('utf-8'))
    port = c_ushort(args["port"])
    timeoutMs = c_int(args["timeoutMs"])

    res = api.OpenNetConnection(hComm, ip, port, timeoutMs)
    if res != 0:
        msgB, log = [f"falha ao abrir leitor, IP: {ip.value} port: {port} falha na conexão"] * 2
        return res_jsonify(res, msgB, log, False)
    
    current_app.hComm = hComm.value
    log = f"leitor aberto com sucesso, endereço IP：{args['ip']}，port：{args['port']}"
    return res_jsonify(res, log=log, hComm = hComm.value)

#fecha a conexão de rede ou COM
@UHFServices.app.route("/CloseDevice", methods=["post"])
def CloseDevice():
    """Feche a porta serial ou porta de rede conectada ao leitor."""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int, default=0)
    args = parser.parse_args()

    hComm = c_int(args["hComm"])

    res = api.CloseDevice(hComm)
    current_app.hComm = 0
    log = "Fechar Leitor"
    return res_jsonify(res, log=log, success=True)

@UHFServices.app.route("/GetTagInfo", methods=["post"]) #rota API_FLASK "/GetTagInfo" no metodo POST
def GetTagInfo():
    
    """Obter informações do rótulo"""
    info = deepcopy(current_app.t.info)# faz uma cópia profunda do dicionário 'info' na classe UHF
    tag_info = list(info.values())# transforma as informações do dicionário em uma lista de valores

    #para cada tag
    for tag in tag_info:
        tag["m_counts"] = "/".join([str(x) for x in tag["m_counts"]])#formata sendo uma string separada por "/"
        
    bruteTag.saveOnFile(tag_info=tag_info, type_f="brute")
    return res_jsonify(0, taginfo = tag_info)# retorna uma resposta JSON com código de status 0 e informações da tag

#define modo de trabalho de energia
@UHFServices.app.route("/SetRFPower", methods=["post"])
def SetRFPower():
    """definir comando de energia"""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int, default=0)
    parser.add_argument('power', type=int)
    parser.add_argument('reserved', type=int)
    args = parser.parse_args()

    hComm = c_int(args["hComm"])
    power = c_ubyte(args["power"])
    reserved = c_ubyte(args["reserved"])

    res = api.SetRFPower(hComm, power, reserved)
    return res_jsonify(res)

#pega as informações e parametros do leitor
@UHFServices.app.route("/GetDevicePara", methods=["post"])
def GetDevicePara():
    """Obter comando de parâmetro do dispositivo"""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int, default=0)
    args = parser.parse_args()

    if current_app.hComm == 0:
        log, msgB = ["Falha ao obter energia, o leitor não está aberto"] * 2
        return res_jsonify(1001, msgB, log, False)
    
    param = DeviceFullInfo()
    hComm = c_int(args["hComm"])

    res = api.GetDevicePara(hComm, param)

    if res != 0:
        log, msgB = [f"Failed to get Power, {ERROR_CODE.get(res)}"] * 2
        return res_jsonify(res, msgB, log, False)

    STRATFREI = list(param.STRATFREI)
    STRATFRED = list(param.STRATFRED)
    STEPFRE = list(param.STEPFRE)

    freq = STRATFREI[0]*256 + STRATFREI[1]
    freqde = STRATFRED[0]*256 + STRATFRED[1]
    step = STEPFRE[0]*256 + STEPFRE[1]

    freq = '{:.3f}'.format((freq * 1000 + freqde) / 1000)

    info = {
        "DEVICEARRD": param.DEVICEARRD, "RFIDPRO": param.RFIDPRO, "WORKMODE": param.WORKMODE, 
        "INTERFACE": param.INTERFACE, "BAUDRATE": param.BAUDRATE, "WGSET": param.WGSET, 
        "ANT": param.ANT, "REGION": param.REGION, "STRATFREI": freq, 
        "STRATFRED": freqde, "STEPFRE": step, "CN": param.CN, 
        "RFIDPOWER": param.RFIDPOWER, "INVENTORYAREA": param.INVENTORYAREA, "QVALUE": param.QVALUE, 
        "SESSION": param.SESSION, "ACSADDR": param.ACSADDR, "ACSDATALEN": param.ACSDATALEN, 
        "FILTERTIME": param.FILTERTIME, "TRIGGLETIME": param.TRIGGLETIME, "BUZZERTIME": param.BUZZERTIME, 
        "INTERNELTIME": param.INTERNELTIME
    }
    return res_jsonify(res, **info)

#seta as informações e parametros do leitor
@UHFServices.app.route("/SetDevicePara", methods=["post"])
def SetDevicePara():
    """Definir comando de parâmetro do dispositivo"""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int, default=0)
    parser.add_argument('DEVICEARRD', type=int)
    parser.add_argument('RFIDPRO', type=int)
    parser.add_argument('WORKMODE', type=int)
    parser.add_argument('INTERFACE', type=int)
    parser.add_argument('BAUDRATE', type=int)
    parser.add_argument('WGSET', type=int)
    parser.add_argument('ANT', type=int)
    parser.add_argument('REGION', type=int)
    parser.add_argument('STRATFREI', type=str)
    parser.add_argument('STRATFRED', type=str)
    parser.add_argument('STEPFRE', type=int)
    parser.add_argument('CN', type=int)
    parser.add_argument('RFIDPOWER', type=int)
    parser.add_argument('INVENTORYAREA', type=int)
    parser.add_argument('QVALUE', type=int)
    parser.add_argument('SESSION', type=int)
    parser.add_argument('ACSADDR', type=int)
    parser.add_argument('ACSDATALEN', type=int)
    parser.add_argument('FILTERTIME', type=int)
    parser.add_argument('TRIGGLETIME', type=int)
    parser.add_argument('BUZZERTIME', type=int)
    parser.add_argument('INTERNELTIME', type=int)
    args = parser.parse_args()

    if current_app.hComm == 0:
        log, msgB = ["Falha ao obter energia, o leitor não está aberto"] * 2
        return res_jsonify(1001, msgB, log, False)

    freq = int(float(args["STRATFREI"]))
    freqde = int(float(args["STRATFREI"]) * 1000 - freq * 1000)
    
    STRATFREI = (c_ubyte*2)(freq>>8, freq&0xff)
    STRATFRED = (c_ubyte*2)(freqde>>8, freqde&0xff)
    STEPFRE = (c_ubyte*2)(args["STEPFRE"]>>8, args["STEPFRE"]&0xff)

    param = DevicePara(
        args["DEVICEARRD"], args["RFIDPRO"], args["WORKMODE"], args["INTERFACE"], args["BAUDRATE"], 
        args["WGSET"], args["ANT"], args["REGION"], STRATFREI, STRATFRED, STEPFRE, args["CN"], args["RFIDPOWER"], 
        args["INVENTORYAREA"],  args["QVALUE"], args["SESSION"], args["ACSADDR"], args["ACSDATALEN"], 
        args["FILTERTIME"],  args["TRIGGLETIME"], args["BUZZERTIME"], args["INTERNELTIME"]
    )
    hComm = c_int(args["hComm"])

    try:
        res = api.SetDevicePara(hComm, param)
    except Exception as e:
        msgB, log = [str(e)] * 2
        return res_jsonify(1001, msgB, log, False)
    return res_jsonify(res)

#inicia a execução do aparelho
@UHFServices.app.route("/StartCounting", methods=["post"])
def startCounting():
    """começar"""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int, default=0)
    parser.add_argument('DEVICEARRD', type=int)
    parser.add_argument('RFIDPRO', type=int)
    parser.add_argument('WORKMODE', type=int)
    parser.add_argument('INTERFACE', type=int)
    parser.add_argument('BAUDRATE', type=int)
    parser.add_argument('WGSET', type=int)
    parser.add_argument('ANT', type=int)
    parser.add_argument('REGION', type=int)
    parser.add_argument('STRATFREI', type=str)
    parser.add_argument('STRATFRED', type=str)
    parser.add_argument('STEPFRE', type=int)
    parser.add_argument('CN', type=int)
    parser.add_argument('RFIDPOWER', type=int)
    parser.add_argument('INVENTORYAREA', type=int)
    parser.add_argument('QVALUE', type=int)
    parser.add_argument('SESSION', type=int)
    parser.add_argument('ACSADDR', type=int)
    parser.add_argument('ACSDATALEN', type=int)
    parser.add_argument('FILTERTIME', type=int)
    parser.add_argument('TRIGGLETIME', type=int)
    parser.add_argument('BUZZERTIME', type=int)
    parser.add_argument('INTERNELTIME', type=int)
    args = parser.parse_args()

    freq = int(float(args["STRATFREI"]))
    freqde = int(float(args["STRATFREI"]) * 1000 - freq * 1000)
    
    STRATFREI = (c_ubyte*2)(freq>>8, freq&0xff)
    STRATFRED = (c_ubyte*2)(freqde>>8, freqde&0xff)
    STEPFRE = (c_ubyte*2)(args["STEPFRE"]>>8, args["STEPFRE"]&0xff)

    param = DevicePara(
        args["DEVICEARRD"], args["RFIDPRO"], args["WORKMODE"], args["INTERFACE"], args["BAUDRATE"], 
        args["WGSET"], args["ANT"], args["REGION"], STRATFREI, STRATFRED, STEPFRE, args["CN"], args["RFIDPOWER"], 
        args["INVENTORYAREA"],  args["QVALUE"], args["SESSION"], args["ACSADDR"], args["ACSDATALEN"], 
        args["FILTERTIME"],  args["TRIGGLETIME"], args["BUZZERTIME"], args["INTERNELTIME"]
    )
    hComm = c_int(args["hComm"])
    
    try:
        if args["WORKMODE"] == 0:
            if current_app.inventory:
                current_app.t.terminate()
                api.InventoryStop(hComm, 10000)
            api.SetDevicePara(hComm, param)
            time.sleep(0.1)
            api.InventoryContinue(hComm, c_ubyte(0), c_int(0))
            current_app.work_mode = 0
        else:
            if current_app.inventory:
                current_app.t.terminate()
            api.SetDevicePara(hComm, param)
            time.sleep(0.1)
            current_app.work_mode = 1

        timeout = c_int(1000)

        current_app.inventory = True

        t = InventoryThread(hComm, timeout)  
        t.setDaemon(True)
        current_app.t = t
        current_app.t.start()
    except Exception as e:
        msgB, log = [f"Rótulo de inventário falhou：{str(e)}"] * 2
        return res_jsonify(1001, msgB, log,  False)
    msgB = "Iniciar inventário"
    return res_jsonify(0, msgB)

#para o inventario
@UHFServices.app.route("/InventoryStop", methods=["post"])
def InventoryStop():
    """parar o inventário"""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int, default=0)
    parser.add_argument('timeout', type=int, required=True, help="Tempo de espera pelos dados, unidade ms")
    args = parser.parse_args()

    hComm = c_int(args["hComm"])
    timeout = c_int(args["timeout"])
    if current_app.hComm == 0:
        return res_jsonify(0)

    try:
        res = 0
        if current_app.inventory:
            current_app.t.terminate()
            if current_app.work_mode == 0:
                res = api.InventoryStop(hComm, 1000)
            current_app.inventory = False
    except Exception as e:
        msgB = str(e)
        return res_jsonify(1000, msgB, "", False)

    log = "Inventário Parado"
    return res_jsonify(res, "", log)

#fecha relé
@UHFServices.app.route("/Close_Relay", methods=["post"])
def Close_Relay():
    """Definir relé fechado"""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int)
    parser.add_argument('time', type=int, default=0)
    args = parser.parse_args()

    if current_app.hComm == 0:
        log, msgB = ["Falha ao obter energia, o leitor não está aberto"] * 2
        return res_jsonify(1001, msgB, log, False)

    hComm = c_int(args["hComm"])
    time = c_ubyte(0)

    try:
        res = api.Close_Relay(hComm, time)
    except Exception as e:
        msgB = str(e)
        return res_jsonify(1001, msgB, "", False)
    log = "Definir sucesso do Close_Relay do dispositivo"
    return res_jsonify(res, "", log)

#abre relé
@UHFServices.app.route("/Release_Relay", methods=["post"])
def Release_Relay():
    """Definir relé aberto"""
    parser = reqparse.RequestParser()
    parser.add_argument('hComm', type=int)
    args = parser.parse_args()

    if current_app.hComm == 0:
        log, msgB = ["Falha ao obter energia, o leitor não está aberto"] * 2
        return res_jsonify(1001, msgB, log, False)

    hComm = c_int(args["hComm"])
    time = c_ubyte(0)
    
    try:
        res = api.Release_Relay(hComm, time)
    except Exception as e:
        msgB = str(e)
        return res_jsonify(1001, msgB, "", False)
    log = "Definir sucesso do Release_Relay do dispositivo"
    return res_jsonify(res, "", log)

