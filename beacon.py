class Beacon:
    def __init__(
            self,
            mac_address="", uuid="",
            major_number=0, minor_number=0,
            tx_power=0, rssi=0,
            timestamp=0
    ):
        self.mac_address = mac_address
        self.uuid = uuid
        self.major_number = major_number
        self.minor_number = minor_number
        self.tx_power = tx_power
        self.rssi = rssi
        self.timestamp = timestamp

    def jsonify(self):
        return {
            "mac": self.mac_address,
            "id": self.uuid,
            "major": self.major_number,
            "minor": self.minor_number,
            "tx": self.tx_power,
            "rssi": self.rssi,
            "timestamp": self.timestamp
        }

    def __eq__(self, other):
        return self.mac_address == other.mac_address

    def __str__(self):
        return "MAC Address: " + self.mac_address + ", TX Power: " + str(self.tx_power)


def parse_beacon_list(obj_list):
    # print(obj_list)
    beacons = []
    for obj in obj_list:
        data = obj.split(",")
        beacons.append(Beacon(data[0], data[1], data[2], data[3], data[4], data[5]))

    return beacons
