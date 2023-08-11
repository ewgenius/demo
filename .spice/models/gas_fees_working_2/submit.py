#!/usr/bin/env python3

import os
import re
import json
import subprocess
import tempfile
from zipfile import ZipFile
from http import client
import yaml

HOST = 'https://dev-data.spiceai.io'
API_KEY = '333434|509ac91b5e634695a7f98fe247fe6968' # dev cerexhe spice-app-template
#API_KEY = os.environ['SPICE_API_KEY']

def make_conn():
  conn = client.HTTPSConnection if HOST.startswith('https://') else client.HTTPConnection
  return conn(re.sub('https?://', '', HOST))

def get(conn, path):
  conn.request('GET', path, '', {})
  return handle(conn)

def post(conn, path, data):
  print(json.dumps(data, indent=2))
  conn.request('POST', path, json.dumps(data), {
    'Content-type': 'application/json',
  })
  return handle(conn)

def handle(conn):
  rs = conn.getresponse()
  r = rs.read()
  try:
    j = json.loads(r)
    return j
  except:
    return r

def train():
  conn = make_conn()
  tq = '''SELECT number as "ts", CAST(base_fee_per_gas / 1000000000.0 AS DOUBLE) as "y", CAST(transaction_count AS DOUBLE) as "y2" from eth.recent_blocks
WHERE base_fee_per_gas IS NOT NULL'''
  iq = '''SELECT number as "ts", CAST(base_fee_per_gas / 1000000000.0 AS DOUBLE) as "y", CAST(transaction_count AS DOUBLE) as "y2" from eth.recent_blocks
WHERE base_fee_per_gas IS NOT NULL ORDER BY ts DESC LIMIT 35'''

  tq += ' ORDER BY number DESC LIMIT 500' # last 500 blocks

  #with tempfile.TemporaryDirectory() as tmp:
  abort_after_upload = False
  if True:
    tmp = '.'
    zpath = f'{tmp}/function.zip'
    if not os.path.exists(zpath):
      print('creating zip ...')
      with ZipFile(zpath, 'w') as z:
        for filename in ['gas_fees.py', 'requirements.txt']:
          with open(filename, encoding='utf8') as f:
            s = f.read()
            z.writestr(filename, s)
      abort_after_upload = True

    print('upload', zpath)
    subprocess.run(['ipfs', 'add', zpath])
    out = subprocess.run(['ipfs', '--api', '/ip4/20.115.54.73/tcp/5001', 'add', '-nq', zpath], capture_output=True, text=True)
    code_package_cid = out.stdout.strip()
    print(code_package_cid)
    if abort_after_upload:
      print('aborting to give you a chance to manually bash the ipfs caches')
      return

  config = {
    "model_type": 'xgb_gas_fees',
    "lookback_size": 30,
    "forecast_size": 1,
    "epochs": 1,
    "train_query": tq,
    "inference_query": iq,
    'metadata': {
      "lookback_size": 30,
      "forecast_size": 1,
      #"firecache": True,
      "covariate": True,
    },
    'runtime': 'python3.10',
    'code_package_cid': code_package_cid,
    'train_handler': 'gas_fees.train',
    'inference_handler': 'gas_fees.infer',
  }
  with open('context.yaml', 'w', encoding='utf8') as f:
    yaml.dump(config, f)

  rs = post(conn, f'/v0.1/train?api_key={API_KEY}', config)
  print(rs)

if __name__ == '__main__':
  train()

