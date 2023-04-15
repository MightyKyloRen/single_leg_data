
#!/usr/bin/python3 -B
# Copyright 2021 Josh Pieper, jjp@pobox.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This example commands multiple servos connected to a pi3hat.  It
uses the .cycle() method in order to optimally use the pi3hat
bandwidth.
"""

import asyncio
import math
import moteus
import moteus_pi3hat
import time
import serial
import csv
import struct

 
row = [0,0,0,0,0,0,0]
epi = "Sit_Stand__Center"
filename = 'Dataset_15_04.csv'
async def main():
    # We will be assuming a system where there are 4 servos, each
    # attached to a separate pi3hat bus.  The servo_bus_map argument
    # describes which IDs are found on which bus.
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map = {
            1:[12],2:[13],
        },
    )

    # We create one 'moteus.Controller' instance for each servo.  It
    # is not strictly required to pass a 'transport' since we do not
    # intend to use any 'set_*' methods, but it doesn't hurt.
    #
    # This syntax is a python "dictionary comprehension":
    # https://docs.python.org/3/tutorial/datastructures.html#dictionaries
    qr = moteus.QueryResolution()
    qr.q_current = moteus.F32
    qr.d_current = moteus.F32
    qr._extra = {
         moteus.Register.CONTROL_TORQUE : moteus.F32,
    } 
    servos = {
        servo_id : moteus.Controller(id=servo_id, transport=transport, query_resolution=qr)
        for servo_id in [12,13,]
    }

    # We will start by sending a 'stop' to all servos, in the event
    # that any had a fault.
    await transport.cycle([x.make_stop() for x in servos.values()])
    k = 0
    now = 0
    while True:
        # The 'cycle' method accepts a list of commands, each of which
        # is created by calling one of the `make_foo` methods on
        # Controller.  The most common thing will be the
        # `make_position` method.

        if now == 0:
        	start = time.time()
                
        now = time.time()
        now = now - start

        # For now, we will just construct a position command for each
        # of the 4 servos, each of which consists of a sinusoidal
        # velocity command starting from wherever the servo was at to
        # begin with.
        #
        # 'make_position' accepts optional keyword arguments that
        # correspond to each of the available position mode registers
        # in the moteus reference manual.
        commands = [
            servos[12].make_position(
                position=0.135638*abs(math.sin(now)),
                query=True),
            servos[13].make_position(
                position=-0.242956*abs(math.sin(now)),
                query=True),
        ]

        # By sending all commands to the transport in one go, the
        # pi3hat can send out commands and retrieve responses
        # simultaneously from all ports.  It can also pipeline
        # commands and responses for multiple servos on the same bus.
        results = await transport.cycle(commands)

        # The result is a list of 'moteus.Result' types, each of which
        # identifies the servo it came from, and has a 'values' field
        # that allows access to individual register results.
        #
        # Note: It is possible to not receive responses from all
        # servos for which a query was requested.
        #
        # Here, we'll just print the ID, position, and velocity of
        # each servo for which a reply was returned.
        
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
        #print(", ".join(
        #    f"({result.arbitration_id} " +
        #    f"{result.values[moteus.Register.POSITION]} " +
        #    f"{result.values[moteus.Register.VELOCITY]})"
        #    for result in results))
        #print(line)
        
        row[0] =  line
        i =  0        
        for result in results:
             i = i + 1
             row[i] = result.values[moteus.Register.POSITION]
        for result in results:
             i = i + 1
             row[i] = result.values[moteus.Register.VELOCITY]
        for result in results:
             i = i + 1
             row[i] = result.values[moteus.Register.TORQUE]
        #for result in results:
        #     i = i + 1
        #     row[i] = result.values[moteus.Register.TORQUE_ERROR]
        #for result in results:
        #     i = i + 1
        #     row[i] = result.values[moteus.Register.Q_CURRENT]
        #for result in results:
        #     i = i + 1
        #     row[i] = result.values[moteus.Register.D_CURRENT]
        #for result in results:
        #     i = i + 1
        #     row[i] = result.values[moteus.Register.VOLTAGEDQ_D]
        #for result in results:
        #     i = i + 1
        #     row[i] = result.values[moteus.Register.VOLTAGEDQ_Q]          
        add_row = {'Episode':epi, 'Timestamp': now, 'Position_Shank':row[2],'Position_Thigh':row[1],'Velocity_Shank':row[4],'Velocity_Thigh':row[3],'Torque_Shank':row[6],'Torque_Thigh':row[5],'Force':line}
        print(add_row)
        with open(filename, 'a', newline='') as f:
             # Create a dictionary writer with the dict keys as column fieldnames
             writer = csv.DictWriter(f, fieldnames=add_row.keys())
             # Append single row to CSV
             writer.writerow(add_row)
        # We will wait 20ms between cycles.  By default, each servo
        # has a watchdog timeout, where if no CAN command is received
        # for 100ms the controller will enter a latched fault state.
        await asyncio.sleep(0.002)
        


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    asyncio.run(main())
