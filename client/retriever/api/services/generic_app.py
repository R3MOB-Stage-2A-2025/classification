class Service:
    def __init__(self, apiurl: str = None, apikey: str = None,
                 mailto: str = None, timeout: int = 20):
        self.name = "GenericService"

        self._apiurl = apiurl
        self._apikey = apikey
        self._mailto = mailto
        self._timeout = timeout

