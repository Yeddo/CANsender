"""
send_can_message.py

A Python script to send a CAN message with specified parameters via command-line arguments,
with dynamic timing adjustment to prevent bus overload.

Dependencies:
- python-can library (install with `pip install python-can`)

Usage example:
python send_can_message.py -c can0 -p 65262 -s 33 -d 0 0 0 0 0 0 0 0
"""

import argparse
import time
import can

def send_can_message(channel, pgn, source_address, priority, data, initial_message_interval):
    try:
        # Create CAN bus interface
        can_bus = can.interface.Bus(channel=channel, bustype='socketcan')

        # Create a CAN message
        msg = can.Message(
            arbitration_id=pgn | (priority << 18),
            data=data,
            extended_id=True
        )

        message_interval = initial_message_interval
        last_send_time = time.monotonic()

        while True:
            # Calculate time elapsed since last message sent
            current_time = time.monotonic()
            time_elapsed = current_time - last_send_time

            if time_elapsed < message_interval:
                time.sleep(message_interval - time_elapsed)

            # Record current time before sending message
            last_send_time = time.monotonic()

            # Send the CAN message
            can_bus.send(msg)

    except KeyboardInterrupt:
        print("\nProgram interrupted. Cleaning up...")
        can_bus.shutdown()

if __name__ == '__main__':
    # Command-line argument parser
    parser = argparse.ArgumentParser(description='Send a CAN message with specified parameters, '
                                                 'with dynamic timing adjustment.')
    parser.add_argument('-c', '--channel', type=str, required=True, help='CAN channel (e.g., can0)')
    parser.add_argument('-p', '--pgn', type=int, required=True, help='J1939 PGN')
    parser.add_argument('-s', '--source-address', type=int, required=True, help='Source address')
    parser.add_argument('-r', '--priority', type=int, default=6, help='Message priority (default: 6)')
    parser.add_argument('-d', '--data', type=int, nargs='+', required=True, help='Data bytes (up to 8 bytes)')
    parser.add_argument('-i', '--initial-interval', type=float, default=1.0,
                        help='Initial message interval in seconds (default: 1.0)')
    
    args = parser.parse_args()

    # Validate data length
    if len(args.data) > 8:
        parser.error('Data length cannot exceed 8 bytes.')

    # Convert data to bytes
    data = [byte & 0xFF for byte in args.data]

    # Call function to send CAN message with dynamic timing adjustment
    send_can_message(args.channel, args.pgn, args.source_address, args.priority, data, args.initial_interval)
