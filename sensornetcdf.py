import sys
from collections import namedtuple
import pandas as pd
import numpy as np
from netCDF4 import Dataset
from datetime import datetime
import os
import re


#get year,month,day 

def getfile():
    outfiles = []
    infiles = []
    datatxt = '/home/users/kwinfield/amf/data/'
    for years in os.listdir(datatxt):
        yearsdir = os.path.join(datatxt,years)
        for months in os.listdir(yearsdir):
            monthsdir = os.path.join(yearsdir,months)
            for files in os.listdir(monthsdir):

                filesdir = os.path.join(monthsdir,files)

                expression = re.compile('ncas-pws-1_(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}).txt')
                matched = expression.match(files)


                if matched:
                    year = str(matched.group('year'))
                    month = str(matched.group('month'))
                    day = str(matched.group('day')) 

                    if len(month) < 2:
                        month = '0' + month

                    if len(day) < 2:
                        day = '0' + day


                in_files =str('/home/users/kwinfield/amf/data/{0}/{1}/ncas-pws-1_{2}{3}{4}.txt'.format(year,month,year,month,day))
                infiles.append(in_files)
                
                
    return infiles
       
def outfile(infile):
     return infile.replace('data','data-netcdf').replace('.txt','.nc')
            
        
def makenetcdf(filelist):
    for f in filelist:
    
    
        dataset = Dataset(outfile(f),'w', format='NETCDF4')

        #reads files
        df = pd.read_csv(f, header=None, names=['times','model','id','average','range1','bb','code','99','range2','X00'],parse_dates = ['times'] )


        times = df['times']   
        range1 = df['range1'].str.replace(r' KM', '')
        code = df['code']
        range2 = df['range2'].str.replace(r' KM', '')

        #add in qc
        df['pws_flag'] = 1
        df['average_range'] = 1
        df['instantaneous_range'] = 1


        #converts into numpy
        range1np = np.array(range1)
        codenp = np.array(code)
        range2np = np.array(range2)
        pws_flagnp = np.array(df['pws_flag'])
        range1flagnp = np.array(df['average_range'])
        range2flagnp = np.array(df['instantaneous_range'])

        #creating dimensions
        longitude = dataset.createDimension('longitude')
        latitude = dataset.createDimension('latitude')
        time = dataset.createDimension('time')

        #creating variables
        #time
        timess = dataset.createVariable('times',np.float64,('time',))
        #converting time to seconds
        base_time = times[0]
        time_values = []
        for t in times:
            value = t- base_time
            ts = value.total_seconds()
            time_values.append(ts)

        timess.units = "seconds since" + base_time.strftime('%Y-%m-%d %H:%M:%S')
        timess[:] = np.float64(time_values)


        #average meteorological optical range
        arange = dataset.createVariable('Average_meteorological_optical_range(km)',np.float32, ('time',))
        arange.type = 'float32'
        arange.units = 'KM'
        arange.long_name = 'Average meteorological optical range'
        arange.coordinates = 'latitude longitude'
        arange[:] = np.float32(range1np)

        arangeflag = dataset.createVariable('Average_meteorological_optical_range_flag',np.int8, ('time',))
        arangeflag.type = 'byte'
        arangeflag.units = '1'
        arangeflag.long_name = 'Average meteorological optical range flag'
        arangeflag.coordinates = 'latitude longitude'
        arangeflag.flag_values = '0b,1b,2b,3b'
        arangeflag.flag_meanings = 'not_used' + '\n'
        arangeflag.flag_meanings = arangeflag.flag_meanings + 'good_data' + '\n'
        arangeflag.flag_meanings = arangeflag.flag_meanings + 'suspect_data_data_not_quality_controlled' + '\n'
        arangeflag.flag_meanings = arangeflag.flag_meanings + 'bad_data_do_not_use' 
        arangeflag[:] = np.int8(range1flagnp)


         #present weather code
        pws = dataset.createVariable('Present_weather_code',np.float32, ('time',))
        pws.type = 'float32'
        pws.units = '1'
        pws.long_name = 'Present Weather Code'
        pws.coordinates = 'latitude longitude'
        pws[:] = np.float32(codenp)

        pwsflag = dataset.createVariable('Present_weather_code_flag',np.int8, ('time',))
        pwsflag.type = 'byte'
        pwsflag.units = '1'
        pwsflag.long_name = 'Present Weather Code flag'
        pwsflag.coordinates = 'latitude longitude'
        pwsflag.flag_values = '0b,1b,2b,3b'
        pwsflag.flag_meanings = 'not_used' + '\n'
        pwsflag.flag_meanings = pwsflag.flag_meanings + 'good_data' + '\n'
        pwsflag.flag_meanings = pwsflag.flag_meanings + 'suspect_data_data_not_quality_controlled' + '\n'
        pwsflag.flag_meanings = pwsflag.flag_meanings + 'bad_data_do_not_use' 
        pwsflag[:] = np.int8(pws_flagnp)


        #istantaneous meteorological optical range
        irange = dataset.createVariable('Instantaneous_meteorological_Optical_range(km)',np.float32, ('time',))
        irange.type = 'float32'
        irange.units = 'KM'
        irange.long_name = 'Instantaneous meteorological optical range'
        irange.coordinates = 'latitude longitude'
        irange[:] = np.float32(range2np)

        irangeflag = dataset.createVariable('Instantaneous_meteorological_optical_range_flag',np.int8, ('time',))
        irangeflag.type = 'byte'
        irangeflag.units = '1'
        irangeflag.long_name = 'Instantaneous meteorological optical range flag'
        irangeflag.flag_values = '0b,1b,2b,3b'
        irangeflag.flag_meanings = 'not_used' + '\n'
        irangeflag.flag_meanings = irangeflag.flag_meanings + 'good_data' + '\n'
        irangeflag.meanings = irangeflag.flag_meanings + 'suspect_data_data_not_quality_controlled' + '\n'
        irangeflag.flag_meanings = irangeflag.flag_meanings + 'bad_data_do_not_use' 

        irangeflag[:] = np.int8(range2flagnp)

        #global attributes
        #read metadata file and add it in
        metadata_file_dir = '/home/users/kwinfield/amf/metadata.xlsx'
        meta = pd.read_excel(metadata_file_dir)
        name = meta.loc[:, 'Name':'Name':1].values
        exp = meta.loc[:, 'Example':'Example':1].values

        for i in range(0,len(name)):
            msg1 = np.array(name[i])
            msg2 = np.array(exp[i])
            dataset.setncattr(msg1[0], msg2[0])
        
        dataset.close()


if __name__ == "__main__":
    #i.e. if file run directly
    makenetcdf(getfile())
