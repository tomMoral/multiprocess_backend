import os


MP_COMM_CHANNEL = 'conn'
if ('MP_COMM_CHANNEL' in os.environ.keys() and
        os.environ['MP_COMM_CHANNEL'] == 'pipe'):
    MP_COMM_CHANNEL = 'pipe'
