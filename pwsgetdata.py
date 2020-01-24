import sys, io, serial, time
import os
from datetime import datetime

def sensordir():

#getting time to make file and directory
    datestring = datetime.utcnow().isoformat(); # starting time
#print(datestring, 'that is me now')

    dt = time.strptime(datestring,'%Y-%m-%dT%H:%M:%S.%f')
    start_day = dt[2]
    yy = str(dt[0])
    mm = str(dt[1])
    if len(mm) < 2:
       mm = '0' + mm
    dd = str(dt[2])
    if len(dd) < 2:
       dd = '0' + dd
    name = 'ncas-pws-1_' + yy + mm + dd + '.txt'
    dirpath = '/home/pi/data/{0}/{1}/'.format(yy,mm)
    if os.path.isdir(dirpath):
        outfile = os.path.join(dirpath, name)
    else:
        dir_data = os.makedirs(dirpath) #output data directory
        outfile = os.path.join(dirpath, name)

    return outfile

def sensordata(outfile):
    port = "/dev/ttyS0" #serial port
    baudrate = 9600 #baud number
    dir_data = '/home/pi/data/' #output data directory

    #open the serial board of the instrument
    ser =serial.Serial()

    #configure port timeout refers to the data rate
    ser.port = port
    ser.baudrate = baudrate
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.bytesize = serial.EIGHTBITS
    ser.timeout = 60

    #checking to see if the file is open or not. As it may over write or not save.
    if ser.isOpen():
        ser.close()
    ser.open()
    ser.isOpen()

    #get and write the data
    #example of data string SWS100,001,060,05.14 KM,99.999,04,+99.9 C,05.19 KM,XOO

    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1), encoding='ascii')
    sio._CHUNK_SIZE =1

    while ser.isOpen():

        #get datetime
        datestring = datetime.utcnow().isoformat()
        #print(type(datestring))


        datastring = sio.readline()
        #print(datastring)
        #print(type(datastring))
        datastring.strip('\r')
        print(datestring+ ',' + datastring)
        data = (datestring+ ',' + datastring)

        #check for new day
        dt = time.strptime(datestring,'%Y-%m-%dT%H:%M:%S.%f')
        start_day = dt[2]
        now_day = dt[2];
        if now_day != start_day:
            start_day = now_day
            yy = str(dt[0])
            mm = str(dt[1])
            if len(mm) < 2:
                mm = '0' + mm
                dd = str(dt[2])
            if len(dd) < 2:
                dd = '0' + dd

            names = 'ncas-pws-1_' + yy + mm + dd + '.txt'
            outfile = os.path.join(dirpath, names)

        f = open(outfile,'a')
        f.write(data)
        f.close()
'''
if __name__ == "__main__":
    #i.e. if file run directly
    sensordata(sensordir())
'''
