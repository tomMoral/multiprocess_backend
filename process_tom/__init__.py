import os

VALID_BACKEND = ['pipe', 'conn', 'sock']

MP_COMM_CHANNEL = None
if 'MP_COMM_CHANNEL' in os.environ.keys():
    MP_COMM_CHANNEL = os.environ['MP_COMM_CHANNEL']
