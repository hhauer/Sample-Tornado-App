from tornado.websocket import WebSocketHandler
from tornado.ioloop import PeriodicCallback
import tornado.ioloop
import tornado.web
import json

class WebSocketTest(WebSocketHandler):
    def open(self):
        print "Opened websocket."
        self.game_data = {}
        self.loop_callback = PeriodicCallback(self.do_loop, 5000)
        
        self.game_data['wood'] = 10
        self.game_data['heat'] = 0
        self.game_data['progress'] = 0
        self.write_json(self.game_data)
        self.loop_callback.start()
        
    def on_message(self, message):
        print "Message: {}".format(message)
        message = json.loads(message)
        if message['type'] == 'add_1':
            self.game_data['wood'] += 1
            self.write_json(self.game_data)
        if message['type'] == 'add_5':
            self.game_data['wood'] += 5
            self.write_json(self.game_data)
    
    def do_loop(self):
        if self.game_data['wood'] < 1:
            self.turns_no_wood += 1
            self.game_data['heat'] -= (5 * self.turns_no_wood)
            if self.game_data['heat'] < 1:
                self.game_data['heat'] = 0
        else:
            self.turns_no_wood = 0
            self.game_data['heat'] += (5 * self.game_data['wood'])
            self.game_data['wood'] -= (self.game_data['heat'] / 50)
            if self.game_data['wood'] < 1:
                self.game_data['wood'] = 0
                
        if self.game_data['heat'] > 2000:
            self.game_data['progress'] += 1
        
        if self.game_data['heat'] > 2500:
            print "Heat failure."
            self.game_data['fail'] = True
        
        if self.game_data['progress'] > 9:
            print "Success."
            self.game_data['success'] = True
            
        self.write_json(self.game_data) 
            
    def on_close(self):
        print "Closed websocket."
        self.loop_callback.stop()
    
    def write_json(self, message):
        self.write_message(json.dumps(message))


application = tornado.web.Application([
    (r"/", WebSocketTest),
], debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()