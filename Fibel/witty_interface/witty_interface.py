import smbus

##$v_in;$v_out;$cur_out\n";

class wpi_interface:
    #7 bit address (will be left shifted to ad$

    def __init__(self, busnumber=1, deviceaddress=0x69):
        self.bus = smbus.SMBus(busnumber)
        self.DEVICE_ADDRESS = deviceaddress

    def read_v_in(self)-> float:
        byte1 = self.bus.read_byte_data(self.DEVICE_ADDRESS, 1)
        byte2 = self.bus.read_byte_data(self.DEVICE_ADDRESS, 2)
        typeconversion = float(str(byte1)+"."+str(byte2))
        return typeconversion

    def read_v_out(self)-> float:
        byte1 = self.bus.read_byte_data(self.DEVICE_ADDRESS, 3)
        byte2 = self.bus.read_byte_data(self.DEVICE_ADDRESS, 4)
        typeconversion = float(str(byte1)+"."+str(byte2))
        return typeconversion

    def read_cur_out(self)-> float:
        byte1 = self.bus.read_byte_data(self.DEVICE_ADDRESS, 5)
        byte2 = self.bus.read_byte_data(self.DEVICE_ADDRESS, 6)
        typeconversion = float(str(byte1)+"."+str(byte2))
        return typeconversion

if __name__ == "__main__":
    a = wpi_interface()
    print("current v in: "+str(a.read_v_in()))
    print("current v out: "+str(a.read_v_out()))
    print("current a out: "+str(a.read_cur_out()))
