import json


class BaseRegistryMock(object):

    def get_objects(self, json_path):
        json_data = open(json_path)
        data = json.load(json_data)
        json_data.close()
        return data


class FCSRegistryMock(BaseRegistryMock):

    def get_companies(self, path):
        return self.get_objects('notifications/tests/base/json/fgas_companies.json')

    def get_persons(self, path):
        return self.get_objects('notifications/tests/base/json/fgas_persons.json')


class BDRRegistryMock(BaseRegistryMock):

    def get_companies(self):
        return self.get_objects('notifications/tests/base/json/bdr_companies.json')

    def get_persons(self):
        return self.get_objects('notifications/tests/base/json/bdr_persons.json')
