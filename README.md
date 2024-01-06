recovery of the power value on modbus communication in listening mode between the DDSU666 and the foxess inverter and integration into home assistant 
in use uart to rs485 module and raspberry connecting slave in line inverter <> ddsu666 , create path /home/pi/ddsu666-foxess copy ddsu666-foxess.py

check if ok start python ddsu666-foxess.py 
pi@raspberrypi:~ $ /usr/bin/python3 /home/pi/ddsu666-foxess/ddsu666-foxess.py
True
no rx data
inverter (online) rx: 0103043e2bb98cf5e6
inverter (online) rx: 0103043e4f0d84c2ff
inverter (online) rx: 0103043e566cf43b4c
inverter (online) rx: 0103043e57dbf5dcbc
inverter (online) rx: 0103043e58fc503734
inverter (online) rx: 0103043e59b3d05364

and mosquitto_sub -h localhost -t "#" -v

pi@raspberrypi:~ $ mosquitto_sub -h localhost -t "#" -v
ddsu666-foxess/loads_power 72
ddsu666-foxess/loads_power 75
ddsu666-foxess/loads_power 73
ddsu666-foxess/loads_power 74
ddsu666-foxess/loads_power 73


copy file /etc/systemd/system/ddsu666-foxess.service 
set service: 
sudo systemctl enable ddsu666-foxess.service
sudo systemctl start ddsu666-foxess.service
sudo systemctl set-default graphical.target
install mqtt addon to home assistant and configure ( 127.0.0.1 port 1883 ) and configuration.yaml add mqtt: !include mqtt.yaml


sample home assistant:
type: gauge
entity: sensor.ddsu666_foxess_loads_power
needle: true
max: 9000
severity:
  green: 0
  yellow: 3000
  red: 6000
min: -3000


