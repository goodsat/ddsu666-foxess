import serial
import time
import binascii
import paho.mqtt.client as mqtt
import struct

#https://www.framboisier.com/blog/2023/01/28/mieux-que-linky-avec-home-assistant-2023/
def crc16_modbus(data : bytearray, offset, length):
    if data is None or offset < 0 or offset > len(data) - 1 and offset + length > len(data):
        return 0
    crc = 0xFFFF
    for i in range(length):
        crc ^= data[offset + i]
        for j in range(8):
            if ((crc & 0x1) == 1):
                crc = int((crc / 2)) ^ 40961
            else:
                crc = int(crc / 2)
    return crc & 0xFFFF


ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600)
ser.timeout = 2     # serial read timeout
print(ser.is_open)  # True for opened


if ser.is_open:
    rx2 = bytearray(9)
    rx_byte_crc = bytearray(2)
    rx_byte_puissance = bytearray(4)

    client = mqtt.Client(client_id="ddsu666-foxess")
    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()
    
    while True:
        ser.write(b'\x01\x03\x20\x04\x00\x02\x8e\x0a') # send master modbus function 03 for inverter (offline)
        size = ser.inWaiting()
        
        if size > 9: # if inverter (online) in serial to echo master modbus function 03 (cmd + reply)
            rx = ser.read(size)
            i = 0
            size = size - 17
            while i <= size: # loop echo master (cmd + reply)
                if rx[i] == 0x01 and rx[i+1] == 0x03 and rx[i+2] == 0x20 and rx[i+3] == 0x04 : # 01032004 cmd
                    if rx[i+8] == 0x01 and rx[i+9] == 0x03 and rx[i+10] == 0x04 : # 010304 reply
                        b = 0                 
                        while b < 9: # copy reply data
                            rx2[b] = rx[i+8+b]
                            b = b + 1
                        
                        # check reply value crc
                        crc = crc16_modbus(rx2, 0, 7)
                        rx_byte_crc[0] = rx2[8]
                        rx_byte_crc[1] = rx2[7]
                        rx_byte_crc_int = int.from_bytes(rx_byte_crc, "big")
                        if crc == rx_byte_crc_int:
                            print("inverter (online) rx: " + binascii.hexlify(rx2).decode("utf-8"))        
                            # 01 03 04 3f4d70a4 424b
                            rx_byte_puissance[0] = rx2[3]
                            rx_byte_puissance[1] = rx2[4]
                            rx_byte_puissance[2] = rx2[5]
                            rx_byte_puissance[3] = rx2[6]
                            c = str(round(struct.unpack('!f', bytes.fromhex(binascii.hexlify(rx_byte_puissance).decode("utf-8")))[0] * 1000))
                            client.publish("ddsu666-foxess/loads_power", c) 
                            time.sleep(1)
                            
                i = i + 1
                
        elif size == 9: # if inverter (offline) in serial to master modbus reply function 03
            rx = ser.read(size) 
            if rx[0] == 0x01 and rx[1] == 0x03 and rx[2] == 0x04 : # if modbus function 03 010304 reply
                # check reply value crc
                crc = crc16_modbus(rx, 0, 7)
                rx_byte_crc[0] = rx[8]
                rx_byte_crc[1] = rx[7]
                rx_byte_crc_int = int.from_bytes(rx_byte_crc, "big")
                if crc == rx_byte_crc_int:
                    print("inverter (offline) rx: " + binascii.hexlify(rx).decode("utf-8"))
                    # 01 03 04 3f4d70a4 424b
                    rx_byte_puissance[0] = rx[3]
                    rx_byte_puissance[1] = rx[4]
                    rx_byte_puissance[2] = rx[5]
                    rx_byte_puissance[3] = rx[6]
                    c = str(round(struct.unpack('!f', bytes.fromhex(binascii.hexlify(rx_byte_puissance).decode("utf-8")))[0] * 1000))
                    client.publish("ddsu666-foxess/loads_power", c) 
                
        else:
            print('no rx data')
            
        time.sleep(1)      
else:
    print('serial not open')

if ser.is_open:
    ser.close()
    

client.loop_stop()
client.disconnect()
