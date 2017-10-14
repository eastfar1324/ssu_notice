import webapp2
import apiai

class MainHandler(webapp2.RequestHandler):

    def __init__(self, request, response):
        self.initialize(request, response)
        self.ai = apiai.ApiAI('9e2f805b26a44df3955374bb8278e848')

    def get(self):
        request = self.ai.text_request()
        request.lang = 'en'
        request.query = "show me 5 recent notices"
        response = request.getresponse()
        self.response.write(response.read())

    def post(self):
        req = self.request.get_json(silent=True, force=True)
        res = self.response
        res.headers['Content-Type'] = 'application/json'
        return res

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
