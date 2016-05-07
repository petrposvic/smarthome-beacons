#!/usr/bin/python2.7
import time
import json
import requests

import blescan
import sys

import bluetooth._bluetooth as bluez
import beacon as b

# Use mock data
mock = False


class Main:
    """Main class"""

    sock_bt = None
    timer = 0

    def __init__(self, device_name, rest_url, beacons):
        """Gets configuration"""

        self.device_name = device_name
        self.rest_url = rest_url
        self.beacons = beacons

        if not mock:
            dev_id = 0
            try:
                self.sock_bt = bluez.hci_open_dev(dev_id)
                print("ble thread started")
            except:
                print("error accessing bluetooth device...")
                sys.exit(1)

            blescan.hci_le_set_scan_parameters(self.sock_bt)
            blescan.hci_enable_le_scan(self.sock_bt)

    def run(self):
        """Run infinite loop"""

        if not mock and self.sock_bt is None:
            print("bluetooth socket error")
            sys.exit(0)

        while True:
            self.loop()

    def loop(self):
        """Discover all BLE devices and update beacon list

        Send keepAlive message each {self.interval} seconds.
        """

        now = time.time()
        time.sleep(1)

        if mock:
            discovered = b.parse_beacon_list([
                'fc:be:ba:1c:e5:30,5689a6fabfa2bd01467d6e00fbabad05,5642,6151,6,-90',
            ])

        else:
            discovered = b.parse_beacon_list(blescan.parse_events(
                self.sock_bt, len(self.beacons)
            ))

        # Update beacons by discovered beacons
        payload = []
        for beacon in discovered:
            try:
                index = self.beacons.index(beacon)
                self.beacons[index].tx_power = beacon.tx_power
                self.beacons[index].rssi = beacon.rssi
                self.beacons[index].timestamp = now
                payload.append(self.beacons[index].jsonify())
            except ValueError:
                # print "unknown beacon " + str(beacon)
                pass

        for beacon in self.beacons:
            if beacon.timestamp < now - 60:
                if beacon.active:
                    beacon.active = False
                    self.send("/api/beacons", json.dumps(beacon.jsonify()))
            else:
                if not beacon.active:
                    beacon.active = True
                    self.send("/api/beacons", json.dumps(beacon.jsonify()))

    def send(self, url, payload):
        """
        Sends payload to server by TCP/IP socket

        :param url: Endpoint
        :param payload: JSON data
        """

        print(url + ": " + payload)
        try:
            r = requests.post(
                self.rest_url + url,
                headers={
                    "Content-Type": "application/json"
                },
                data=payload
            )
            # print(r)
        except requests.exceptions.ConnectionError:
            print('Connection error')


if __name__ == "__main__":
    Main("livingroom", "http://192.168.1.203:3000", [
        b.Beacon("fc:be:ba:1c:e5:30", "kocar1"),
        b.Beacon("84:a4:66:89:39:58", "kocar2"),
    ]).run()

