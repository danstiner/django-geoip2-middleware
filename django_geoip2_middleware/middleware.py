from django.contrib.gis.geoip2 import GeoIP2

class GeoIP2Middleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.geoip2 = GeoIP2()

    def __call__(self, request):
        request.geolocation = self.determine_geolocation(request)
        return self.get_response(request)

    def determine_geolocation(self, request):
        client_ip = self.get_client_ip(request)
        if hasattr(request, 'session') and 'geolocation' in request.session:
            session_geolocation = request.session['geolocation']
            if 'client_ip' in session_geolocation and session_geolocation['client_ip'] == client_ip:
                return session_geolocation
        ip_geolocation = self.geoip2.city(client_ip)
        ip_geolocation['client_ip'] = client_ip
        if hasattr(request, 'session'):
            if 'geolocation' in request.session and 'client_ip' in session_geolocation and session_geolocation['client_ip'] == client_ip:
                pass
            else:
                request.session['geolocation'] = ip_geolocation
        return ip_geolocation

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def process_template_response(self, request, response):
        if hasattr(request, 'geolocation'):
            response.context_data['geolocation'] = request.geolocation
        return response
