import json

from bluedot.btcomm import BluetoothClient
from signal import pause

def data_received(data):
    print(data)

c = BluetoothClient("Eastec-SOne", data_received)
c.send("helloworld")

data = {
    "key": "value"
}
c.send(json.dumps(data))
pause()