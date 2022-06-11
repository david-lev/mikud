.. image:: https://github.com/david-lev/mikud/blob/master/docs/_static/dark_logo.png?raw=true
  :width: 95
  :alt: Alternative text
.. end-logo

`mikud <https://github.com/david-lev/mikud>`_: Search for Israeli zip code numbers
##################################################################################################

.. image:: https://img.shields.io/pypi/dm/mikud?style=flat-square
    :alt: PyPI Downloads
    :target: https://pypi.org/project/mikud/

.. image:: https://www.codefactor.io/repository/github/david-lev/mikud/badge/master
   :target: https://www.codefactor.io/repository/github/david-lev/mikud/overview/master
   :alt: CodeFactor

.. image:: https://readthedocs.org/projects/mikud/badge/?version=latest&style=flat-square
   :target: https://mikud.readthedocs.io
   :alt: Docs


________________________

☎️ mikud is a Python3 library to search israel's zip codes (mikud) by their addresses.

📖 For a **complete documentation** of available functions, see the `Reference <https://mikud.readthedocs.io/en/latest/#id1>`_.

>>️ *This tool based on israelpost website -* `Click here <https://israelpost.co.il/%D7%A9%D7%99%D7%A8%D7%95%D7%AA%D7%99%D7%9D/%D7%90%D7%99%D7%AA%D7%95%D7%A8-%D7%9E%D7%99%D7%A7%D7%95%D7%93/>`_.


🎛 Installation
--------------
.. installation

- **Install using pip3:**

.. code-block:: bash

    pip3 install -U mikud

- **Install from source:**

.. code-block:: bash

    git clone https://github.com/david-lev/mikud.git
    cd mikud && python3 setup.py install

.. end-installation

🎉 **Features**
---------------

* Search zip code by address
* Search address by zip code
* Search cities
* Search streets

👨‍💻 **Usage**
----------------
.. code-block:: python

    from mikud import Mikud

    mikud = Mikud()
    mikud_res = mikud.search_mikud(city_name="ירושלים",
                                   street_name="כנפי נשרים",
                                   house_number="20")
    if search_res['Result']:
        print(search_res['Result']['zip'])

    addr_res = mikud.search_address(zip_code=9546432)
    if search_res['Result']:
        print(search_res['Result'])



💾 **Requirements**
--------------------

- Python 3.6 or higher - https://www.python.org

📖 **Setup and Usage**
-----------------------

See the `Documentation <https://mikud.readthedocs.io/>`_ for detailed instructions

⛔ **Disclaimer**
------------------

**This application is intended for educational purposes only. Any use in professional manner or to harm anyone or any organization doesn't relate to me and can be considered as illegal.**
