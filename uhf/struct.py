
from ctypes import *
class DeviceFullInfo(Structure):
    _fields_ = [
        ('DEVICEARRD', c_ubyte),
        ('RFIDPRO', c_ubyte),
        ('WORKMODE', c_ubyte),
        ('INTERFACE', c_ubyte),
        ('BAUDRATE', c_ubyte),
        ('WGSET', c_ubyte),
        ('ANT', c_ubyte),
        ('REGION', c_ubyte),
        ('STRATFREI', c_ubyte*2),
        ('STRATFRED', c_ubyte*2),
        ('STEPFRE', c_ubyte*2),
        ('CN', c_ubyte),
        ('RFIDPOWER', c_ubyte),
        ('INVENTORYAREA', c_ubyte),
        ('QVALUE', c_ubyte),
        ('SESSION', c_ubyte),
        ('ACSADDR', c_ubyte),
        ("ACSDATALEN", c_ubyte),
        ("FILTERTIME", c_ubyte),
        ("TRIGGLETIME", c_ubyte),
        ("BUZZERTIME", c_ubyte),
        ("INTERNELTIME", c_ubyte)
    ]
    
class DevicePara(Structure):
    _fields_ = [
        ('DEVICEARRD', c_ubyte),
        ('RFIDPRO', c_ubyte),
        ('WORKMODE', c_ubyte),
        ('INTERFACE', c_ubyte),
        ('BAUDRATE', c_ubyte),
        ('WGSET', c_ubyte),
        ('ANT', c_ubyte),
        ('REGION', c_ubyte),
        ('STRATFREI', c_ubyte*2),
        ('STRATFRED', c_ubyte*2),
        ('STEPFRE', c_ubyte*2),
        ('CN', c_ubyte),
        ('RFIDPOWER', c_ubyte),
        ('INVENTORYAREA', c_ubyte),
        ('QVALUE', c_ubyte),
        ('SESSION', c_ubyte),
        ('ACSADDR', c_ubyte),
        ("ACSDATALEN", c_ubyte),
        ("FILTERTIME", c_ubyte),
        ("TRIGGLETIME", c_ubyte),
        ("BUZZERTIME", c_ubyte),
        ("INTERNELTIME", c_ubyte)
    ]

class TagInfo(Structure): #usada para armazenar informações sobre uma tag
    _fields_ = [
        ('m_no', c_ushort),  # número de série da etiqueta
        ('m_rssi', c_short), # nível de sinal recebido da etiqueta, convertido para dBm
        ("m_ant", c_ubyte),  # numero da antena que detectou a tag
        ("m_channel", c_ubyte), # canal utilizado para a leitura da etiqueta
        ("m_crc", c_ubyte*2), # lista com os valores de CRC da etiqueta
        ("m_pc", c_ubyte*2), # lista com os valores de PC da etiqueta
        ("m_len", c_ubyte), # comprimento do código da etiqueta
        ("m_code", c_ubyte*255) # código da etiqueta em formato hexadecimal
    
    
    
    ]