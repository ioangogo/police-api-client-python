class SimpleResource(object):
    """
    An object that is entirely represented by a discrete part of a larger API
    call, meaning we either don't know it exists or we know everything there is
    to know about it.
    """

    def __init__(self, api, data={}):
        self.api = api
        if data:
            self._hydrate(data)

    def _hydrate(self, data):
        for field in self.fields:
            hydrate_field = getattr(self, '_hydrate_%s' % field, lambda x: x)
            setattr(self, field, hydrate_field(data.get(field)))

    def __repr__(self):
        return self.__str__()


class Resource(SimpleResource):
    """
    An object that has a dedicated API call that can be made to retreive all
    pertinent information. Can be initialised and used with a subset of that
    information, and the dedicated call will not be made until information not
    surfaced anywhere but that call is required. For example, a subset of force
    information exists in the /forces call, but a lot more information is
    available at /forces/[force].
    """

    _requested = False
    api_method = None
    fields = []

    def __init__(self, api, preload=False, **attrs):
        super(Resource, self).__init__(api)
        for key, val in attrs.items():
            setattr(self, key, val)
            if key in self.fields:
                self.fields = list(self.fields)
                self.fields.remove(key)
        if preload:
            self._make_api_request()

    def __getattr__(self, attr):
        if not self._requested and attr in self.fields:
            self._make_api_request()
        return self.__getattribute__(attr)

    def _make_api_request(self):
        self._response_data = self.api.service.request(
            'GET', self._get_api_method())
        self._hydrate(self._response_data)
        self._requested = True

    def _get_api_method(self):
        if self.api_method is None:
            raise RuntimeError('You must set the api_method attribute')
        return self.api_method
