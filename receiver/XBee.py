import serial
from collections import deque


class XBee:
    RxBuff = bytearray()
    RxMessages = deque()

    def __init__(self, serial_port, baud_rate=230400):
        self.serial = serial.Serial(port=serial_port, baudrate=baud_rate)

    def receive(self):
        """
            Receives data from serial and checks buffer for potential messages.
            Returns the next message in the queue if available.
        """
        remaining = self.serial.inWaiting()

        while remaining:
            chunk = self.serial.read(remaining)
            remaining -= len(chunk)
            self.RxBuff.extend(chunk)

        msgs = self.RxBuff.split(bytes(b'\x7E'))

        for msg in msgs[:-1]:
            self.validate(msg)

        self.RxBuff = (bytearray() if self.validate(msgs[-1]) else msgs[-1])

        if self.RxMessages:
            return self.RxMessages.popleft()
        else:
            return None

    def validate(self, message):
        """
        Parses a byte or bytearray object to verify the contents are a
          properly formatted XBee message.

        Args:
            message: An incoming XBee message

        Returns:
            True or False, indicating message validity
        """
        # 9 bytes is Minimum length to be a valid Rx frame
        #  LSB, MSB, Type, Source Address(2), RSSI,
        #  Options, 1 byte data, checksum
        if (len(message) - message.count(bytes(b'0x7D'))) < 9:
            return False
        # All bytes in message must be unescaped before validating content
        frame = self.un_escape(message)
        if frame is None:
            return False
        # print('frame: {}'.format(frame))

        length = int.from_bytes(frame[0:2], byteorder='big', signed=False)
        # Frame (minus checksum) must contain at least length equal to LSB
        if length > (len(frame[2:]) - 1):
            return False

        # Validate checksum
        if (sum(frame[2:3 + length]) & 0xFF) != 0xFF:
            return False

        # print("Rx: " + self.format(bytearray(b'\x7E') + message))
        self.RxMessages.append(frame)
        return True

    def send_str(self, message, address=0xFFFF, options=0x01, frame_id=0x00):
        """
        Args:
            message: A message, in string format, to be sent
            address: The 16 bit address of the destination XBee
                (default: 0xFFFF broadcast)
            options: Optional byte to specify transmission options
                (default 0x01: disable acknowledge)
            frame_id: Optional frame_id, only used if Tx status is desired

        Returns:
            Number of bytes sent
        """
        return self.send(message.encode('utf-8'), address, options, frame_id)

    def send(self, message, address=0xFFFF, options=0x01, frame_id=0x00):
        """
        Args:
            message: A message, in bytes or byte array format, to be sent to an XBee
            address: The 16 bit address of the destination XBee
                (default broadcast)
            options: Optional byte to specify transmission options
                (default 0x01: disable ACK)
            frame_id: Optional frame_id, only used if transmit status is desired

        Returns:
            Number of bytes sent
        """
        if not message:
            return 0

        hexes = '7E 00 {:02X} 01 {:02X} {:02X} {:02X} {:02X}'.format(
            len(message) + 5,  # LSB (length)
            frame_id,
            (address & 0xFF00) >> 8,  # Destination address high byte
            address & 0xFF,  # Destination address low byte
            options
        )

        frame = bytearray.fromhex(hexes)
        #  Append message content
        frame.extend(message)

        # Calculate checksum byte
        frame.append(0xFF - (sum(frame[3:]) & 0xFF))

        # Escape any bytes containing reserved characters
        frame = self.escape(frame)

        print("Tx: " + self.format(frame))
        return self.serial.write(frame)

    @staticmethod
    def un_escape(message):
        """
        Helper function to unescaped an XBee API message.

        Args:
            message: An byte or byte array object containing a raw XBee message
                minus the start delimiter

        Returns:
            XBee message with original characters.
        """
        if message[-1] == 0x7D:
            # Last byte indicates an escape, can't un_escape that
            return None

        out = bytearray()
        skip = False
        for i in range(len(message)):
            if skip:
                skip = False
                continue

            if message[i] == 0x7D:
                out.append(message[i + 1] ^ 0x20)
                skip = True
            else:
                out.append(message[i])

        return out

    @staticmethod
    def escape(message):
        """
        Escapes reserved characters before an XBee message is sent.

        Args:
            message: A bytes or byte array object containing an original message to
                be sent to an XBee

         Returns:
            A byte array object prepared to be sent to an XBee in API mode
         """
        escaped = bytearray()
        reserved = bytearray(b"\x7E\x7D\x11\x13")

        escaped.append(message[0])
        for m in message[1:]:
            if m in reserved:
                escaped.append(0x7D)
                escaped.append(m ^ 0x20)
            else:
                escaped.append(m)

        return escaped

    @staticmethod
    def format(message):
        """
        Formats a byte or byte array object into a more human readable string
            where each bytes is represented by two ascii characters and a space

        Args:
            message: A bytes or byte array object

        Returns:
            A string representation
        """
        return " ".join("{:02x}".format(b) for b in message)
