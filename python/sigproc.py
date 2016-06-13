#This program is for reading and writing sigproc filterbank files.

#  Copyright 2015 Ben Barsdell
#  Copyright 2016 NVIDIA Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
telescope_id:  0 (FAKE)
machine_id:    0 (FAKE)
data_type:     2 # Time-series data
rawdatafile:   <delete>
source_name:   <observer-specified>
barycentric:   0
pulsarcentric: <delete>
az_start:      <delete> or <observer-specified>
za_start:      <delete> or <observer-specified>
src_raj:       <observer-specified> or <delete>
src_dej:       <observer-specified> or <delete>
tstart:        MJD of first sample
tsamp:         (secs) E.g., 0.5/(2400*24kHz=57.6MHz)=8.68055556ns
nbits:         8
nsamples:      No. time samples in file ("rarely used any more")
fch1:          58.776 MHz (center frequency)
foff:           MHz
nchans:        1
nifs:          2 (pols)
refdm:         0.0 [pc/cm^3]
period:        <delete>
data:          [time][pol][nbit] (General case: [time][if/pol][chan][nbit])
"""

import struct
from collections import defaultdict
import numpy as np

#header parameter names which precede strings
_STRING_VALUES = ['source_name',
                  'rawdatafile']
#header parameter names which precede doubles
_DOUBLE_VALUES = ['az_start',
                  'za_start',
                  'src_raj',
                  'src_dej',
                  'tstart',
                  'tsamp',
                  'period',
                  'fch1',
                  'foff',
                  'refdm']
#header parameter names which precede integers
_INTEGER_VALUES = ['nchans',
                   'telescope_id',
                   'machine_id',
                   'data_type',
                   'ibeam',
                   'nbeams',
                   'nbits',
                   'barycentric',
                   'pulsarcentric',
                   'nbins',
                   'nsamples',
                   'nifs',
                   'npuls']
#this header parameter precedes a character
_CHARACTER_VALUES = ['signed']

#the data_type parameter names' translation
_DATA_TYPES = defaultdict(lambda: 'unknown',
                          {0: 'raw data',
                           1: 'filterbank',
                           2: 'time series',
                           3: 'pulse profile',
                           4: 'amplitude spectrum',
                           5: 'complex spectrum',
                           6: 'dedispersed subbands'})
#the telescope_id parameter names' translation
_TELESCOPES = defaultdict(lambda: 'unknown',
                          {0:  'Fake',
                           1:  'Arecibo',
                           2:  'Ooty',
                           3:  'Nancay',
                           4:  'Parkes',
                           5:  'Jodrell',#'Lovell',
                           6:  'GBT',
                           7:  'GMRT',
                           8:  'Effelsberg',
                           52: 'LWA-OV',
                           53: 'LWA-SV'})
#the machine_id parameter names' translation
_MACHINES = defaultdict(lambda: 'unknown',
                        {0:  'FAKE',
                         1:  'PSPM',
                         2:  'WAPP',
                         3:  'AOFTM',
                         4:  'BPP',
                         5:  'OOTY',
                         6:  'SCAMP',
                         7:  'GMRTFB',
                         8:  'PULSAR2000',
                         52: 'LWA-DP',
                         53: 'LWA-ADP'})

def _header_write_string(file_object, key):
    file_object.write(struct.pack('=i', len(key)))
    file_object.write(key)

def _header_write_value(file_object, key, value):
    if isinstance(value, int):
        fmt = '=i'
    elif isinstance(value, float):
        fmt = '=d'
    elif key == 'signed':
        fmt = '=b'
    else:
        raise TypeError("Invalid value type")
    _header_write_string(file_object, key)
    file_object.write(struct.pack(fmt, value))

def _header_read_one_parameter(file_object):
    length = struct.unpack('=i', file_object.read(4))[0]
    if length <= 0 or length >= 80:
        return None
    return file_object.read(length)

def _write_header(hdr, file_object):
    """write the entire header to the current position of a file"""
    _header_write_string(file_object, "HEADER_START")
    for key, val in hdr.items():
        if key in _STRING_VALUES:
            _header_write_string(file_object, key)
            _header_write_string(file_object, val)
        elif key in _DOUBLE_VALUES:
            _header_write_value(file_object, key, float(val))
        elif key in _INTEGER_VALUES:
            _header_write_value(file_object, key, int(val))
        elif key == "header_size":
            pass
        else:
            #raise KeyError("Unknown sigproc header key: %s"%key)
            print "WARNING: Unknown sigproc header key: %s" % key
    _header_write_string(file_object, "HEADER_END")

def _read_header(file_object):
    """Get the entire header from a file, and return as dictionary"""
    if _header_read_one_parameter(file_object) != "HEADER_START":
        file_object.seek(0)
        raise ValueError("Missing HEADER_START")
    expecting = None
    header = {}
    while True:
        key = _header_read_one_parameter(file_object)
        if key is None:
            raise ValueError("Failed to parse header")
        elif key == 'HEADER_END':
            break
        elif key in _STRING_VALUES:
            expecting = key
        elif key in _DOUBLE_VALUES:
            header[key] = struct.unpack('=d', file_object.read(8))[0]
        elif key in _INTEGER_VALUES:
            header[key] = struct.unpack('=i', file_object.read(4))[0]
        elif key in _CHARACTER_VALUES:
            header[key] = struct.unpack('=b', file_object.read(1))[0]
        elif expecting is not None:
            header[expecting] = key
            expecting = None
        else:
            print "WARNING: Unknown header key", key
    if 'nchans' not in header:
        header['nchans'] = 1
    header['header_size'] = file_object.tell()
    #frame_bits = header['nifs'] * header['nchans'] * header['nbits']
    #if 'nsamples' not in header or header['nsamples'] == 0:
    #   file_object.seek(0, 2) # Seek to end of file
    #   header['nsamples'] = (file_object.tell() - header['header_size'])*8 / frame_bits
    #   file_object.seek(header['header_size'], 0) # Seek back to end of header
    return header

def pack(data, nbit):
    """downgrade data from 8bits to nbits (per value)"""
    data = data.flatten()
    if 8 % nbit != 0:
        raise ValueError("unpack: nbit must divide into 8")
    if data.dtype not in (np.uint8, np.int8):
        raise TypeError("unpack: dtype must be 8-bit")
    outdata = np.zeros(data.size/(8/nbit)).astype('uint8')
    for index in range(1, 8/nbit):
        outdata += data[index::8/nbit]/(2**nbit)**index
    return outdata

def _write_data(data, nbit, file_object):
    if nbit < 8:
        data = pack(data, nbit)
    data.tofile(file_object)

# TODO: Move this elsewhere?
def unpack(data, nbit):
    """upgrade data from nbits to 8bits"""
    if nbit > 8:
        raise ValueError("unpack: nbit must be <= 8")
    if 8 % nbit != 0:
        raise ValueError("unpack: nbit must divide into 8")
    if data.dtype not in (np.uint8, np.int8):
        raise TypeError("unpack: dtype must be 8-bit")
    if nbit == 8:
        return data
    elif nbit == 4:
        # Note: This technique assumes LSB-first ordering
        tmpdata = data.astype(np.int16)#np.empty(upshape, dtype=np.int16)
        tmpdata = (tmpdata | (tmpdata <<  8)) & 0x0F0F
        tmpdata = tmpdata << 4 # Shift into high bits to avoid needing to sign extend
        updata = tmpdata
    elif nbit == 2:
        tmpdata = data.astype(np.int32)#np.empty(upshape, dtype=np.int16)
        tmpdata = (tmpdata | (tmpdata << 16)) & 0x000F000F
        tmpdata = (tmpdata | (tmpdata <<  8)) & 0x03030303
        tmpdata = tmpdata << 6 # Shift into high bits to avoid needing to sign extend
        updata = tmpdata
    elif nbit == 1:
        tmpdata = data.astype(np.int64)#np.empty(upshape, dtype=np.int16)
        tmpdata = (tmpdata | (tmpdata << 32)) & 0x0000000F0000000F
        tmpdata = (tmpdata | (tmpdata << 16)) & 0x0003000300030003
        tmpdata = (tmpdata | (tmpdata <<  8)) & 0x0101010101010101
        tmpdata = tmpdata << 7 # Shift into high bits to avoid needing to sign extend
        updata = tmpdata
    return updata.view(data.dtype)

# TODO: Add support for writing
#       Add support for data_type != filterbank
class SigprocFile(object):
    def __init__(self, filename=None):
        if filename is not None:
            self.open(filename)
    def open(self, filename):
        # Note: If nbit < 8, pack_factor = 8 / nbit and the last dimension
        #         is divided by pack_factor, with dtype set to uint8.
        self.file_object = open(filename, 'rb')
        self.header = _read_header(self.file_object)
        self.header_size = self.header['header_size']
        self.frame_shape = (self.header['nifs'], self.header['nchans'])
        self.nbit = self.header['nbits']
        signed = 'signed' in self.header and self.header['signed'] is True
        if self.nbit >= 8:
            if signed:
                self.dtype = {8: np.int8,
                              16: np.int16,
                              32: np.float32,
                              64: np.float64}[self.nbit]
            else:
                self.dtype = {8: np.uint8,
                              16: np.uint16,
                              32: np.float32,
                              64: np.float64}[self.nbit]
        else:
            self.dtype = np.int8 if signed else np.uint8
            pack_factor = 8 / self.nbit
            self.frame_shape = (self.frame_shape[0],
                                self.frame_shape[1]/pack_factor)
            #self.frame_shape[-1] /= pack_factor
        self.frame_size = self.frame_shape[0]*self.frame_shape[1]
        self.frame_nbyte = self.frame_size*self.dtype().itemsize
        return self
    def close(self):
        self.file_object.close()
    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        self.close()
    def seek(self, offset, whence=0):
        if whence == 0:
            offset += self.header_size
        self.file_object.seek(offset, whence)
    def bandwidth(self):
        return self.header['nchans'] * self.header['foff']
    def cfreq(self):
        return self.header['fch1'] + 0.5*(self.header['nchans']-1)*self.header['foff']
    def duration(self):
        return self.header['tsamp'] * self.nframe()
    def nframe(self):
        if 'nsamples' not in self.header or self.header['nsamples'] == 0:
            curpos = self.file_object.tell()
            self.file_object.seek(0, 2) # Seek to end of file
            frame_bits = self.header['nifs'] * self.header['nchans'] * self.header['nbits']
            nframe = (self.file_object.tell() - self.header['header_size'])*8 / frame_bits
            self.header['nsamples'] = nframe
            self.file_object.seek(curpos, 0) # Seek back to where we were
        return self.header['nsamples']
    def read(self, nframe_or_start, end=None):
        if end is not None:
            start = nframe_or_start or 0
            self.seek(start * self.frame_nbyte)
            if end == -1:
                end = self.nframe()
            nframe = end - start
        else:
            nframe = nframe_or_start
        data = np.fromfile(self.file_object, count=nframe*self.frame_size, dtype=self.dtype)
        nframe = data.size // self.frame_size
        data = data.reshape((nframe,)+self.frame_shape)
        nbit = self.header['nbits']
        if nbit < 8:
            data = unpack(data, nbit)
        return data
    def readinto(self, buf):
        return self.file_object.readinto(buf)
    def __str__(self):
        hmod = self.header.copy()
        data_type = hmod['data_type']
        hmod['data_type'] = "%i (%s)" % (data_type, _DATA_TYPES[data_type])
        telescope_id = hmod['telescope_id']
        hmod['telescope_id'] = "%i (%s)" % (telescope_id, _TELESCOPES[telescope_id])
        machine_id = hmod['machine_id']
        hmod['machine_id']   = "%i (%s)" % (machine_id, _MACHINES[machine_id])
        return '\n'.join(['% 16s: %s' % (key, val) for (key, val) in hmod.items()])
    def __getitem__(self, key):
        if isinstance(key, type("")): # Header key lookup
            return self.header[key]
        elif isinstance(key, int): # Extract one time slice
            return self.read(key, key+1)[0]
        elif isinstance(key, slice): # 1D slice
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else -1
            data = self.read(start, stop)
            #data = self.read(stop) if start == 0 else \
            #       self.read(start, key.stop)
            return data[::key.step]
        elif isinstance(key, tuple): # ND key
            raise NotImplementedError

class SigprocSettings(object):
    """defines, reads, writes sigproc settings"""
    def __init__(self):
        self.nifs = 0
        self.nchans = 0
        self.dtype = np.uint8
        self.nbits = 8
        self._header_dict = {}
    def _interpret_header(self):
        """redefine variables from header dictionary"""
        self.nifs = self._header_dict['nifs']
        self.nchans = self._header_dict['nchans']
        self.nbits = self._header_dict['nbits']
        signed = 'signed' in self._header_dict and self._header_dict['signed'] is True
        if self.nbits >= 8:
            if signed:
                self.dtype = {8: np.int8,
                              16: np.int16,
                              32: np.float32,
                              64: np.float64}[self.nbits]
            else:
                self.dtype = {8: np.uint8,
                              16: np.uint16,
                              32: np.float32,
                              64: np.float64}[self.nbits]
        else:
            self.dtype = np.int8 if signed else np.uint8
    def __str__(self):
        """print settings in string format"""
        hmod = self._header_dict.copy()
        data_type = hmod['data_type']
        hmod['data_type'] = "%i (%s)" % (data_type, _DATA_TYPES[data_type])
        telescope_id = hmod['telescope_id']
        hmod['telescope_id'] = "%i (%s)" % (telescope_id, _TELESCOPES[telescope_id])
        machine_id = hmod['machine_id']
        hmod['machine_id'] = "%i (%s)" % (machine_id, _MACHINES[machine_id])
        return '\n'.join(['% 16s: %s' % (key, val) for (key, val) in hmod.items()])
    @property
    def header(self):
        """fetches the header dictionary, possibly
        editing for readability(unimplemented)"""
        return self._header_dict
    @header.setter
    def header(self, input_header):
        self._header_dict = input_header
        self._interpret_header()

class SigprocData(SigprocSettings):
    """Reads, slices, writes data"""
    def __init__(self):
        super(SigprocData, self).__init__()
        self._local_data = np.ndarray([])
        self.nframe = 0
    def _find_nframe_from_data(self):
        self.nframe = self._local_data.shape[0]
    def append_data(self, input_data):
        """append data to local data"""
        self._local_data.flatten()
        self._local_data = np.append(self._local_data, input_data.flatten())
        frame_shape = (self.nframe+input_data.shape[0], self.nifs, self.nchans)
        self._local_data = np.reshape(self._local_data, frame_shape)
        self._find_nframe_from_data()
    @property
    def data(self):
        """fetches local data, possibly reading as it goes"""
        return self._local_data
    @property
    def duration(self):
        """calculates the duration of the observation"""
        return self.nframe*self._header_dict['tsamp']

class SigprocFileRW(SigprocData):
    """Reads from or writes to a sigproc filterbank file"""
    def __init__(self):
        super(SigprocFileRW, self).__init__()
        self.file_object = None
    def open(self, filename, mode):
        """open the filename, and read the header and data from it"""
        if 'b' not in mode:
            raise NotImplementedError("No support for non-binary files")
        self.file_object = open(filename, mode)
        self.read_header()
        self.read_data()
        return self
    def close(self):
        """closes file object"""
        self.file_object.close()
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
    def read_header(self):
        """reads in a header from the file and sets local settings"""
        self._header_dict = _read_header(self.file_object)
        self._interpret_header()
    #get all data from file and store it locally
    def read_data(self):
        """read data from file and store it locally"""
        data = np.fromfile(self.file_object, dtype=self.dtype)
        self.nframe = data.size/self.nifs/self.nchans
        data = data.reshape((self.nframe, self.nifs, self.nchans))
        if self.nbits < 8:
            data = unpack(data, self.nbits)
        self._local_data = data
    def write_to(self, filename):
        """writes data and header to a different file"""
        file_object = open(filename, 'wb')
        _write_header(self._header_dict, file_object)
        _write_data(self._local_data, self.nbits, file_object)
    #check if should read data from file before returning
