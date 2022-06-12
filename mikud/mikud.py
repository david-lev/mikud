from __future__ import annotations
from abc import ABCMeta
from requests import Session
from json import dump, load, JSONDecodeError
from os import path, remove
from typing import Union, List
import inspect

BASE_URL = 'https://apimftprd.israelpost.co.il'


class Mikud:
    def __init__(self, config_file=None):
        self._session = Session()
        self._headers = {'Application-API-Key': 'CA4ED65C-DC64-4969-B47D-EF564E3763E7',
                        'Ocp-Apim-Subscription-Key': '97a72e22d26044f68b29cb6e94a6cd14',
                        'Application-Name': 'PostIL',
                        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; SM-A505F Build/RP1A.200720.012)'}
        self._access_token = None
        self._config_file = config_file if config_file else "mikud_config.json"

    def search_mikud(self, city_name: str = "",
                     city_id: Union[str, int] = "",
                     street_name: str = "",
                     street_id: Union[str, int] = "",
                     house_number: Union[str, int] = "",
                     pob: Union[str, int] = "",
                     entry: str = "") -> Address:
        """
        Get zip code (mikud) of address.
            - You can specify the name of the city and street (or their id from :py:func:`search_cities` and :py:func:`search_streets`) and the house number.
            - Alternatively, you can specify just the ``city_name`` (or ``city_id``) and the ``pob`` (Post office box) to get the zip code.

        :param city_name: City name. Default - empty. Optional if ``pob`` provided.
        :type city_name: str
        :param city_id: City ID. Default - empty. Optional if ``city_name`` provided.
        :type city_id: Union[int, str]
        :param street_name: Street name. Default - empty. Optional if ``pob`` provided.
        :type street_name: str
        :param street_id: Street ID. Default - empty. Optional if ``street_name`` or ``pob`` provided.
        :type street_id: Union[int, str]
        :param house_number: House number. Default - empty.  Optional if `pob` provided.
        :type house_number: Union[int, str]
        :param pob: Post office box. Default - empty. Optional if ``city_name``, ``street_name`` and ``house_number`` provided.
        :type pob: Union[int, str]
        :param entry: Entry. for example - ``א``, ``ב``. Default - empty. Optional if ``pob`` provided.
        :type entry: str
        :return: Object :func:`Address`
        :rtype: :func:`~Address`
        """
        if ((not city_name or not city_id) and (not street_name or not street_id) and not house_number) and not pob:
            raise Exception("You need to specify city street and house or city and pob!")
        body = {
            "ByMaanimID": "true",
            "City": str(city_name),
            "CityID": str(city_id),
            "Entry": str(entry),
            "House": str(house_number),
            "POB": str(pob),
            "Street": str(street_name),
            "StreetID": str(street_id)
        }
        data = self._request('/zip/SearchZip', body)['Result']
        if not data:
            return Address()
        addr_keys = Address()._init_parameters.keys()
        for key in data.copy():
            if key not in addr_keys:
                del data[key]
        return Address(**data)

    def search_address(self, zip_code: Union[int, str]) -> Address:
        """
        Get address of zip code (mikud).

        :param zip_code: Zip code of 7 numbers.
        :type zip_code: Union[int, str]
        :raises Exception: if zip code length is not 7 numbers.
        :return: Object :func:`~Address`.
        :rtype: :func:`~Address`
        """
        if len(str(zip_code)) != 7:
            raise Exception("Zip code must be 7 numbers!")
        body = {
            "Zipcode": str(zip_code)
        }
        data = self._request('/zip/SearchAddress', body)['Result']
        if not data:
            return Address()
        addr_keys = Address()._init_parameters.keys()
        for key in data.copy():
            if key not in addr_keys:
                del data[key]
        return Address(**data)

    def get_cities(self, city_name: str) -> List[City]:
        """
        Search cities by name to use in :py:func:`search_mikud` and in :py:func:`search_streets`.

        :param city_name: The full name or part of it of the city.
        :type city_name: str
        :return: list with cities :func:`~City`.
        :rtype: List[:func:`~City`]
        """
        body = {"CityStartsWith": str(city_name)}
        cities = self._request('/zip/GetCities', body)['Result']
        if not cities:
            return [City()]
        index = 0
        city_keys = City()._init_parameters.keys()
        for city in cities:
            for key in city.copy():
                if key not in city_keys:
                    del cities[index][key]
            index += 1
        return [City(**city) for city in cities]

    def get_streets(self, city_name: str, street_name: str, city_id: Union[int, str] = "") -> List[Street]:
        """
        Search street by name to use in :py:func:`search_mikud`.

        :param city_name: The full name or part of it of the city name. Optional if ``city_id`` provided.
        :type city_name: str
        :param city_id: City id from :py:func:`~search_cities`. Optional if ``city_name`` provided.
        :type city_id: Union[int, str]
        :param street_name: The full name or part of it of the street name.
        :type street_name: str
        :return: List of :func:`~Street`.
        :rtype: List[:func:`~Street`]
        """
        body = {
            "CityID": str(city_id),
            "CityName": str(city_name),
            "SearchMode": "ID-StartsWith",
            "StartsWith": str(street_name)
        }
        streets = self._request('/zip/GetStreets', body)['Result']
        if not streets:
            return [Street()]
        index = 0
        street_keys = Street()._init_parameters.keys()
        for street in streets:
            for key in street.copy():
                if key not in street_keys:
                    del streets[index][key]
            index += 1
        return [Street(**street) for street in streets]

    def _request(self, endpoint: str, body: dict, auth: bool = True) -> Union[list, dict]:
        """
        Internal function to make requests into israel post api.
        """
        headers = self._headers
        if auth:
            if not self._access_token:
                self._get_token()
            headers['Authorization'] = self._access_token
        r = self._session.post(url=BASE_URL + endpoint, json=body, headers=self._headers)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            if self._get_token(new=True):
                return self._request(endpoint, body, auth)
        raise Exception(r.json()['message'])

    def _get_token(self, new=False) -> bool:
        """
        Internal function to generate and manage access token in order to make requests to israel post api.
        """
        if not new:
            if not path.isfile(str(self._config_file)):
                return self._get_token(new=True)
            with open(self._config_file, 'r') as config_file:
                try:
                    data = load(config_file)
                except JSONDecodeError:
                    remove(self._config_file)
                    return self._get_token(new=True)
                if data.get('access_token'):
                    self._access_token = data['access_token']
                    return True
        else:
            credentials = {"Password": "Saxo3239", "Username": "ono@aadftprd.onmicrosoft.com"}
            r = self._request('/auth/GetToken', credentials, auth=False)
            if r['IsSuccess']:
                with open(self._config_file, 'w') as config_file:
                    dump({'access_token': "Bearer " + r['AccessToken']}, config_file)
                    self._access_token = "Bearer " + r['AccessToken']
                return True
            raise Exception("Can't generate new access token!\n" + str(r))
        return False


class _ParameterReader(ABCMeta):
    """Internal class to get class init parameters"""
    def __init__(cls, *args, **kwargs):
        parameters = inspect.signature(cls.__init__).parameters
        parameters = {key: value for key, value in parameters.items() if key not in ['self', 'args', 'kwargs']}
        try:
            cls._init_parameters = cls.__bases__[0]._init_parameters.copy()
            cls._init_parameters.update(parameters)
        except AttributeError:
            cls._init_parameters = parameters

        super().__init__(*args, **kwargs)


class Address(metaclass=_ParameterReader):
    """
    This class represent a Address object.
        - The following parameters are the attributes of this object.
        - Ignore the names of the parameters in the class structure ^, they are there to deal with the json parsing.

    :param zip: Zip code of 7 numbers.
    :type zip: Union[int, None]
    :param city_name: The name of the city.
    :type city_name: Union[str, None]
    :param city_id: The id of the city.
    :type city_id: Union[int, None]
    :param street_name: The name of the street.
    :type street_name: Union[str, None]
    :param street_id: The id of the street.
    :type street_id: Union[int, None]
    :param house_number: The number of the house.
    :type house_number: Union[int, None]
    :param pob: The number of the post office box.
    :type pob: Union[int, None]
    :param results: The message from the api.
    :type results: Union[str, None]
    """
    def __init__(self,
                 zip: Union[int, None] = None,
                 city: Union[str, None] = None,
                 cityname: Union[str, None] = None,
                 cityid: Union[int, None] = None,
                 cityID: Union[int, None] = None,
                 street: Union[str, None] = None,
                 streetid: Union[int, None] = None,
                 streetID: Union[int, None] = None,
                 housenumber: Union[int, None] = None,
                 pob: Union[int, None] = None,
                 messageResult: Union[str, None] = None,
                 ):
        self.zip = zip
        if self.zip:
            self.zip = int(self.zip)
        self.city_name = city or cityname
        self.city_id = cityid or cityID
        if self.city_id:
            self.city_id = int(self.city_id)
        self.street_name = street
        self.street_id = streetid or streetID
        if self.street_id:
            self.street_id = int(self.street_id)
        self.house_number = housenumber
        if self.house_number:
            self.house_number = int(self.house_number)
        self.pob = pob
        if pob:
            self.pob = int(self.pob)
        self.results = messageResult

        self._appear = f"ADDRESS: [city: {self.city_name}, street: {self.street_name}, zip: {self.zip}]"

    def __str__(self):
        return self._appear

    def __repr__(self):
        return self._appear


class City(metaclass=_ParameterReader):
    """
    This class represent a city object.
        - The following parameters are the attributes of this object.
        - Ignore the names of the parameters in the class structure ^, they are there to deal with the json parsing.

    :param id: The id of the city.
    :type id: Union[int, None]
    :param name: The name of the city.
    :type name: Union[str, None]
    :param zip: The zip code of the city.
    :type zip: Union[int, None]
    """
    def __init__(self,
                 id: Union[int, None] = None,
                 n: Union[str, None] = None,
                 zip: Union[int, None] = None,
                 ):
        self.id = id
        self.name = n
        self.zip = zip
        self._appear = f"CITY: [name: {self.name}, id: {self.id}, zip: {self.zip}]"

    def __str__(self):
        return self._appear

    def __repr__(self):
        return self._appear


class Street(City, metaclass=_ParameterReader):
    """
    This class represent a street object.
        - The following parameters are the attributes of this object.
        - Ignore the names of the parameters in the class structure ^, they are there to deal with the json parsing.

    :param id: The id of the street.
    :type id: Union[int, None]
    :param city_id: The id of the city.
    :type city_id: Union[int, None]
    :param name: The name of the city.
    :type name: Union[str, None]
    :param zip: The zip code of the address.
    :type zip: Union[int, None]
    """
    def __init__(self, cityID: Union[int, None] = None):
        super().__init__()
        self.city_id = cityID
        if self.city_id:
            self.city_id = int(self.city_id)
        self._appear = f"STREET: [name: {self.name}, id: {self.id}]"

    def __str__(self):
        return self._appear

    def __repr__(self):
        return self._appear
