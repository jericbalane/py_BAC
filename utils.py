from wsgiref.simple_server import make_server
from StringIO import StringIO
from urlparse import parse_qs
import traceback
import sys
import cgi
import contextlib
import inspect
import importlib


@contextlib.contextmanager
def capture_stdout(stream):
    old_stdout = sys.stdout
    sys.stdout = stream
    yield
    sys.stdout = old_stdout


class RedirectException(Exception):
    def __init__(self, path):
        self.path = path


class BadRequestException(Exception):
    def __init__(self, message):
        self.message = message


class Response(object):
    def __init__(self, status="200 OK", content_type="text/html", body=""):
        self.status = status
        self.body = body
        self.headers = [('Content-Type', content_type)]


class Callback(object):
    def __init__(self, callback):
        self.callback = callback
        argspec = inspect.getargspec(callback)

        if hasattr(callback, 'im_class'):
            actual_args = argspec.args[1:]
        else:
            actual_args = argspec.args

        if argspec.defaults:
            required_argument_count = len(actual_args) - len(argspec.defaults)
        else:
            required_argument_count = len(actual_args)

        self.required_parameters = actual_args[:required_argument_count]
        self.optional_parameters = actual_args[required_argument_count:]

        if argspec.keywords:
            self.variable_parameters = True
        else:
            self.variable_parameters = False

    def __call__(self, parameters):
        # we don't want to modify the original dict, so make a copy
        supplied_parameters = parameters.copy()

        missing_parameters = [p for p in self.required_parameters if p not in supplied_parameters]
        if missing_parameters:
            raise BadRequestException('Missing parameters in query string: %s' % ', '.join(missing_parameters))

        if not self.variable_parameters:
            for p, v in supplied_parameters.items():
                if (p not in self.required_parameters
                    and p not in self.optional_parameters):
                    del supplied_parameters[p]

                elif len(v) == 1:
                    supplied_parameters[p] = v[0]

        self.callback(**supplied_parameters)


class App(object):
    def __init__(self):
        self.routes = {
            '/shutdown': Callback(self.shutdown)
        }

        self.shutdown_request = False

    def route(self, path):
        def router(callback):
            self.routes[path] = Callback(callback)
            return callback
        return router

    def run(self, port=8080):
        print "Running server on port %d..." % port
        print "Access the app by pointing your browser to http://localhost:%d/" % port
        print "Stop this app by pressing [ctrl]-[c] in this command line"
        try:
            httpd = make_server('', 8080, self.handle_request)
            while not self.shutdown_request:
                httpd.handle_request()

        except KeyboardInterrupt:
            pass

    def handle_request(self, environ, start_response):
        callback = self.routes.get(environ.get('PATH_INFO'))
        if callback:
            try:
                response = self.handle_found(callback, environ.get('QUERY_STRING'))

            except RedirectException, e:
                response = self.handle_redirect(e.path)

            except BadRequestException, e:
                response = self.handle_badrequest(e.message)

            except Exception:
                response = self.handle_error()

        else:
            response = self.handle_notfound()

        start_response(response.status, response.headers)
        return response.body

    def handle_found(self, callback, query_string):
        params = parse_qs(query_string)
        callback_output = StringIO()
        with capture_stdout(callback_output):
            callback(params)

        callback_output.seek(0)

        return Response(status="200 OK", content_type="text/html", body=callback_output)

    def handle_error(self):
        return Response(status="500 SERVER ERROR", content_type='text/plain', body=traceback.format_exc())

    def handle_notfound(self):
        return Response(status="404 NOT FOUND", content_type='text/plain', body="NOT FOUND")

    def handle_redirect(self, path):
        response = Response(status="302 MOVED TEMPORARILY")
        response.headers.append(('location', path))
        return response

    def handle_badrequest(self, message):
        return Response(status="400 BAD REQUEST", content_type='text/plain', body=message)

    def shutdown(self):
        self.shutdown_request = True
        print "shutdown requested"


def redirect(path):
    raise RedirectException(path)


def test():
    app = App()

    @app.route('/')
    def echo_app(name="World"):
        print "<h1>Hello %s!</h1>" % name

    @app.route('/redirect-test')
    def redirect_test():
        redirect('/')


if __name__ == "__main__":
    test()
