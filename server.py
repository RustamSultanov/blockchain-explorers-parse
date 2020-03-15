import json as JSON
import os
import websockets

from sanic import Sanic
from sanic.response import json


try:
    port = int(os.environ['PORT'])
except KeyError as e:
    port = 3001

try:
    initialPeers = os.environ['PEERS'].split(",")
except Exception as e:
    initialPeers = []



class Server(object):

    def __init__(self):

        self.app = Sanic()
        self.sockets = []
        self.app.add_route(self.blocks, '/blocks', methods=['GET'])

    async def blocks(self, request):
        filepath = 'block_expl_info.json'
        with open(filepath, 'r') as block_file:
            block_expl_info = JSON.load(block_file)
        return json(block_expl_info)



if __name__ == '__main__':

    server = Server()
    server.app.run(host='104.248.37.147', port=port, debug=False)