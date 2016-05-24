class Beacon:
    len = 5

    def __init__(
            self,
            mac_address="", uuid="",
            major_number=0, minor_number=0,
            actual_tx_power=0, actual_rssi=0,
            timestamp=0
    ):
        self.mac_address = mac_address
        self.uuid = uuid
        self.major_number = major_number
        self.minor_number = minor_number
        self.tx_power = [actual_tx_power] * self.len
        self.rssi = [actual_rssi] * self.len
        self.timestamp = timestamp

        self.active = False
        self.rssi_avg_last = actual_rssi
        self.active_last = 0
        self.inactive_last = 0

    def last_tx_power(self):
        return self.tx_power[len(self.tx_power) - 1]

    def last_rssi(self):
        return self.rssi[len(self.rssi) - 1]

    def average_tx_power(self):
        return sum(self.tx_power) / len(self.tx_power)

    def average_rssi(self):
        return sum(self.rssi) / len(self.rssi)

    def is_rssi_changed(self):
        avg = self.average_rssi()
        diff = abs(avg - self.rssi_avg_last)

        # print("diff = " + str(diff))
        if diff > 15:
            self.rssi_avg_last = avg
            print("diff " + str(diff))
            return True

        return False

    def is_active_long_time(self, now):
        if now - self.active_last > 300:
            self.active_last = now
            print("active long time")
            return True
        return False

    def is_inactive_long_time(self, now):
        if now - self.inactive_last > 300:
            self.inactive_last = now
            print("inactive long time")
            return True
        return False

    def jsonify(self):
        return {
            "mac": self.mac_address,
            "uuid": self.uuid,
            "major": self.major_number,
            "minor": self.minor_number,
            "tx": self.last_tx_power(),
            "rssi": self.rssi_avg_last,
            "timestamp": self.timestamp,
            "active": self.active
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
        beacons.append(Beacon(data[0], data[1], int(data[2]), int(data[3]), int(data[4]), int(data[5])))

    return beacons
