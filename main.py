#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from flask import Flask, jsonify

app = Flask(__name__)

def get_data():
    url = 'https://scan.rss3.io/api?module=logs&action=getLogs&fromBlock=7351004&toBlock=latest&address=0x28F14d917fddbA0c1f2923C406952478DfDA5578&topic0=0x2808f92d5a0fada467cbe4e766f62f323e78271a7471058a87ef63a9e3e4c5c5'
    print(url)
    response = requests.get(url)
    content = response.text

    total = 0
    data = json.loads(content)
    results = data['result']
    output = {
        'total_count': len(results),
        'transactions': []
    }
    for result in results:
        amountHex = result['data'][0:66]
        transaction = {
            'tx_hash': result['transactionHash'],
            'amount': int(int(amountHex, 16) / 10**18)
        }
        output['transactions'].append(transaction)
        total += int(amountHex, 16)
    output['total_amount'] = total / 10**18
    print(output)
    return output

@app.route('/api/data', methods=['GET'])
def api_data():
    data = get_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
