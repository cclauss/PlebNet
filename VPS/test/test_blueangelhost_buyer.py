import unittest

from BlueAngelHostBuyer import BlueAngelHostBuyer


class TestBlueAngelHostBuyer(unittest.TestCase):
    server = BlueAngelHostBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
