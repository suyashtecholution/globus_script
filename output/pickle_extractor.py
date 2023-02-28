import datetime
import pickle
from PIL import Image

import numpy as np
from ArduCAM_USB_Camera_Shield_Python_Demo.ImageConvert import convert_image

dbfile = open('examplePickle22', 'rb')
db = pickle.load(dbfile)
print(db.keys(),type(db['data']))
import cv2
import time
cfg={'u32CameraType': 0, 'u32Width': 12000, 'u32Height': 9000, 'usbType': 3, 'u8PixelBytes': 1, 'u16Vid': 0, 'u32Size': 108000000, 'u8PixelBits': 8, 'u32I2cAddr': 90, 'emI2cMode': 0, 'emImageFmtMode': 0, 'u32TransLvl': 0, 'u64Time': 133215457679849152}
data=memoryview(db['data'])
color_mode=0

time_before_image = time.time()

#image = convert_image(data, cfg, color_mode)
print('config', data, type(data))

db['data'] = bytes(data)
# data.to_pickle('examplepciker')

time_after_image = time.time()
print('time after Image', time_before_image - time_after_image)


time_before_write = time.time()
print('time before writing image', time_after_image - time_before_write)


"""
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ Working FINAL\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
"""

def white_balance_loops(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 2.5)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 2.5)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result

"""
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
"""

image = white_balance_loops(convert_image(data, cfg, color_mode))
#final = np.hstack((image, white_balance_loops(image)))
cv2.imwrite(f'next{datetime.date.today().month}-{datetime.date.today().day}-{datetime.datetime.now().hour}_{datetime.datetime.now().minute}_{datetime.datetime.now().second}.png',image)
#cv2.imwrite('random.png', image)
exit_ = True
time_after_write = time.time()
print('time after write', time_before_write - time_after_write)

dbfile.close()
