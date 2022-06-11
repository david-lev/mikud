from requests import Session
from json import dump, load, JSONDecodeError
from os import path, remove
from typing import Union

BASE_URL = 'https://apimftprd.israelpost.co.il'


class Mikud:
    def __init__(self, config_file=None):
        self._session = Session()
        self.headers = {'Application-API-Key': 'CA4ED65C-DC64-4969-B47D-EF564E3763E7',
                        'Ocp-Apim-Subscription-Key': '97a72e22d26044f68b29cb6e94a6cd14',
                        'Application-Name': 'PostIL',
                        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; SM-A505F Build/RP1A.200720.012)'}
        self.access_token = None
        self.config_file = config_file if config_file else "mikud_config.json"

    def search_mikud(self, city_name: str = "",
                     city_id: Union[str, int] = "",
                     street_name: str = "",
                     street_id: Union[str, int] = "",
                     house_number: Union[str, int] = "",
                     pob: Union[str, int] = "",
                     entry: str = ""):
        """
        Get zip code (mikud) of address.
            - You can specify the name of the city and street (or their id from :py:func:`search_cities` and :py:func:`search_streets`) and the house number.
            - Alternatively, you can specify just the ``city_name`` (or ``city_id``) and the ``pob`` (Post office box) to get the zip code.

        :param city_name: City name. Default - empty. Optional if ``pob`` provided.
        :param city_id: City ID. Default - empty. Optional if ``city_name`` provided.
        :param street_name: Street name. Default - empty. Optional if ``pob`` provided.
        :param street_id: Street ID. Default - empty. Optional if ``street_name`` or ``pob`` provided.
        :param house_number: House number. Default - empty.  Optional if `pob` provided.
        :param pob: Post office box. Default - empty. Optional if ``city_name``, ``street_name`` and ``house_number`` provided.
        :param entry: Entry. for example - ``א``, ``ב``. Default - empty. Optional if ``pob`` provided.
        :return: dict with zip code of this address.

        Example::

            {
                'ReturnCode': 0,
                'ErrorMessage': None,
                'Result': {
                    'zip': '9546432',
                    'cityname': 'ירושלים',
                    'pob': None,
                    'msgtype': 'address',
                    'messageResult': 'המיקוד לכתובת הינו: 9546432',
                    'cityid': '1046',
                    'streetid': '100691',
                    'indexer': 0
                }
            }
        """
        if ((not city_name or city_id) and (not street_name or street_id) and not house_number) and not pob:
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
        return self._request('/zip/SearchZip', body)

    def search_address(self, zip_code: Union[int, str]) -> dict:
        """
        Get address of zip code (mikud).
        :param zip_code: Zip code of 7 numbers.
        :raises Exception: if zip code length is not 7 numbers.
        :return: dict of address details.

        Example::

            {
                'ReturnCode': 0,
                'ErrorMessage': None,
                'Result': {
                    'city': 'ירושלים',
                    'cityID': '1046',
                    'citySym': '3000',
                    'street': 'כנפי נשרים',
                    'housenumber': '20',
                    'low': None,
                    'high': None,
                    'entrance': '',
                    'msgtype': 'address',
                    'streetID': '100691',
                    'streetSym': '0995',
                    'messageResult': 'ירושלים כנפי נשרים 20 ',
                    'indexer': 0
                }
            }
        """
        if len(str(zip_code)) != 7:
            raise Exception("Zip code must be 7 numbers!")
        body = {
            "Zipcode": str(zip_code)
        }
        return self._request('/zip/SearchAddress', body)

    def search_cities(self, city_name: str) -> dict:
        """
        Search cities by name to use in :py:func:`search_mikud` and in :py:func:`search_streets`.

        :param city_name: The full name or part of it of the city.
        :return: dict with city details.

        Example::

            {
                'ErrorMessage': None,
                'Result': [
                    {
                        'divided': True,
                        'id': '1046',
                        'n': 'ירושלים',
                        'sym': '3000',
                        'syn': 'ירושלים',
                        'zip': ''
                    }
                ],
                'ReturnCode': 0
            }
        """
        body = {"CityStartsWith": str(city_name)}
        return self._request('/zip/GetCities', body)

    def search_streets(self, city_name: str, street_name: str, city_id: Union[str, int] = "") -> dict:
        """
        Search street by name to use in :py:func:`search_mikud`.

        :param city_name: The full name or part of it of the city name. Optional if ``city_id`` provided.
        :param city_id: City id from :py:func:`~mikud.Mikud.search_cities`. Optional if ``city_name`` provided.
        :param street_name: The full name or part of it of the street name.
        :return: dict with street details.

        Example::

            {
                'ReturnCode': 0,
                'ErrorMessage': None,
                'Result': [
                    {
                        'n': 'כנפי נשרים',
                        'id': '100691',
                        'sym': '0995',
                        'syn': 'כנפי נשרים',
                        'cityID': '1046',
                        'citySym': '3000'
                    }
                ]
            }
        """
        body = {
            "CityID": str(city_id),
            "CityName": str(city_name),
            "SearchMode": "ID-StartsWith",
            "StartsWith": str(street_name)
        }
        return self._request('/zip/GetStreets', body)

    def _request(self, endpoint: str, body: dict, auth: bool = True) -> dict:
        """
        Internal function to make requests into israel post api.
        """
        headers = self.headers
        if auth:
            if not self.access_token:
                self._get_token()
            headers['Authorization'] = self.access_token
        r = self._session.post(url=BASE_URL + endpoint, json=body, headers=self.headers)
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
            if not path.isfile(str(self.config_file)):
                return self._get_token(new=True)
            with open(self.config_file, 'r') as config_file:
                try:
                    data = load(config_file)
                except JSONDecodeError:
                    remove(self.config_file)
                    return self._get_token(new=True)
                if data.get('access_token'):
                    self.access_token = data['access_token']
                    return True
        else:
            credentials = {"Password": "Saxo3239", "Username": "ono@aadftprd.onmicrosoft.com"}
            r = self._request('/auth/GetToken', credentials, auth=False)
            if r['IsSuccess']:
                with open(self.config_file, 'w') as config_file:
                    dump({'access_token': "Bearer " + r['AccessToken']}, config_file)
                    self.access_token = "Bearer " + r['AccessToken']
                return True
            raise Exception("Can't generate new access token!\n" + str(r))
        return False
