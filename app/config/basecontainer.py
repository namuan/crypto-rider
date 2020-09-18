class BaseContainer:
    def __init__(self, locator):
        self.locator = locator

    def lookup_object(self, object_name):
        return self.locator.o(object_name)

    def lookup_service(self, service_name):
        return self.locator.s(service_name)