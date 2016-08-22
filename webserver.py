from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import jinja2
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

# Initialize Jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# SETUP DATABASE
engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def write(self, *a, **kw):
        self.wfile.write(*a, **kw)

    @staticmethod
    def render_str(template, params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, kw))

    def do_GET(self):
        try:
            if self.path.endswith("/delete"):
                restaurant_id_str = self.path.split("/")[2]
                restaurant_id_int = int(restaurant_id_str)
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id_int).one()
                print restaurant

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.render('delete.html', restaurant=restaurant)
                return

            if self.path.endswith("/edit"):

                restaurant_id_str = self.path.split("/")[2]
                restaurant_id_int = int(restaurant_id_str)
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id_int).one()
                print restaurant

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.render('edit.html', restaurant=restaurant)
                return

            if self.path.endswith("/restaurants/new"):

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.render('new_restaurants.html')
                return

            if self.path.endswith("/restaurants"):

                restaurants = session.query(Restaurant).all()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.render('front.html', restaurants=restaurants)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        print self.path
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('new_restaurant')

                    # Create new Restaurant Object
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    new_restaurant_name = fields.get('new_restaurant')[0]
                    restaurant_id_str = fields.get('restaurant_id')[0]
                    restaurant_id_int = int(restaurant_id_str)

                    restaurant = session.query(Restaurant).filter_by(id=restaurant_id_int).one()
                    restaurant.name = new_restaurant_name
                    session.add(restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_id_str = fields.get('restaurant_id')[0]
                    restaurant_id_int = int(restaurant_id_str)
                    restaurant = session.query(Restaurant).filter_by(id=restaurant_id_int).one()
                    session.delete(restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
