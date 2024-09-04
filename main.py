#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from flask import Flask, jsonify

app = Flask(__name__)

def get_latest_block():
    url = 'https://scan.rss3.io/api?module=block&action=eth_block_number'
    response = requests.get(url)
    data = response.json()
    return int(data['result'], 16)

def get_data():

    latest_block = get_latest_block()
    print(latest_block)
    from_block = 7351004
    step = 100000
    transactions = []
    total = 0


    while from_block < latest_block:
        to_block = min(from_block + step, latest_block)
        url = f'https://scan.rss3.io/api?module=logs&action=getLogs&fromBlock={from_block}&toBlock={to_block}&address=0x28F14d917fddbA0c1f2923C406952478DfDA5578&topic0=0x2808f92d5a0fada467cbe4e766f62f323e78271a7471058a87ef63a9e3e4c5c5'
        response = requests.get(url)
        data = response.json()
        results = data['result']

        for result in results:
            amountHex = result['data'][0:66]
            transaction = {
                'tx_hash': result['transactionHash'],
                'amount': int(int(amountHex, 16) / 10**18)
            }
            transactions.append(transaction)
            total += int(amountHex, 16)

        from_block = to_block + 1

    output = {
        'total_count': len(transactions),
        'transactions': transactions,
        'total_amount': int(total / 10**18)
    }
    return output


@app.route('/api/data', methods=['GET'])
def api_data():
    data = get_data()
    return jsonify(data)

@app.route('/api/stat', methods=['GET'])
def api_stat():
    data = get_data()
    stat = {
        'total_count': data['total_count'],
        'total_amount': data['total_amount']
    }
    return jsonify(stat)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
