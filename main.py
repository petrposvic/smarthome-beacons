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
    started_at = time.time()

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
                'c6:f8:b3:66:d1:95,e2c56db5dffb48d2b060d0f5a71096e0,0,0,-59,-37',
            ])
        else:
            discovered = b.parse_beacon_list(blescan.parse_events(
                self.sock_bt, len(self.beacons)
            ))

        # Update beacons by discovered beacons
        for beacon in discovered:
            try:
                index = self.beacons.index(beacon)
                self.beacons[index].tx_power.pop(0)
                self.beacons[index].tx_power.append(beacon.last_tx_power())
                self.beacons[index].rssi.pop(0)
                self.beacons[index].rssi.append(beacon.last_rssi())
                self.beacons[index].timestamp = now
            except ValueError:
                # print "unknown beacon " + str(beacon)
                pass

        for beacon in self.beacons:
            if beacon.timestamp < now - 20:
                if beacon.active:
                    beacon.active = False
                    self.send("/api/beacons", json.dumps(beacon.jsonify()))
                else:
                    if beacon.is_inactive_long_time(now):
                        if now - self.started_at > 10:
                            self.send("/api/beacons", json.dumps(beacon.jsonify()))
                        else:
                            print("too early to send changed rssi")
            else:
                if not beacon.active:
                    beacon.active = True
                    self.send("/api/beacons", json.dumps(beacon.jsonify()))
                else:
                    if beacon.is_active_long_time(now) or beacon.is_rssi_changed():
                        if now - self.started_at > 10:
                            self.send("/api/beacons", json.dumps(beacon.jsonify()))
                        else:
                            print("too early to send changed rssi")

    def send(self, url, payload):
        """
        Sends payload to server by TCP/IP socket

        :param url: Endpoint
        :param payload: JSON data
        """

        print(url + ": " + payload)
        try:
            requests.post(
                self.rest_url + url,
                headers={
                    "Content-Type": "application/json"
                },
                data=payload
            )
        except requests.exceptions.ConnectionError:
            print('Connection error')


if __name__ == "__main__":
    Main("livingroom", "http://192.168.1.203:3000", [
        b.Beacon("c6:f8:b3:66:d1:95", "kocar"),
    ]).run()

