import copy
import unittest

from plebnet.agent.qtable import QTable
from plebnet.controllers import cloudomate_controller


class TestQTable(unittest.TestCase):
    qtable = {}
    providers = {}

    def setUp(self):
        self.qtable = QTable()
        self.providers = cloudomate_controller.get_vps_providers()
        del self.providers["proxhost"]

    def tearDown(self):
        pass

    def test_init_providers(self):
        assert (len(self.qtable.providers_offers) == 0)

        self.qtable.init_providers_offers(self.providers)
        assert (len(self.qtable.providers_offers) > 0)

    def test_init_qtable_and_environment(self):
        assert (len(self.qtable.environment) == 0)
        self.qtable.init_qtable_and_environment(self.providers)
        assert (len(self.qtable.environment) > 0)
        assert (len(self.qtable.qtable) > 0)

    def test_calculate_measure(self):
        provider_offer = {"Price": 5, "Connection": 3, "Memory": 2}
        assert (self.qtable.calculate_measure(provider_offer) == 0.012)

    def test_update_environment(self):
        self.qtable.init_qtable_and_environment(self.providers)
        environment_copy = copy.deepcopy(self.qtable.environment)
        self.qtable.update_environment(self.providers[0])
        assert (environment_copy != self.qtable.environment)

    def test_update_environment(self):
        self.qtable.init_qtable_and_environment(self.providers)
        environment_copy = copy.deepcopy(self.qtable.environment)
        assert (environment_copy == self.qtable.environment)
        linevast_offers = cloudomate_controller.options(self.providers["linevast"])
        self.qtable.update_environment(linevast_offers[0].name, False)
        assert (environment_copy != self.qtable.environment)

    def test_update_values(self):
        self.qtable.init_qtable_and_environment(self.providers)
        qtable_copy = copy.deepcopy(self.qtable.qtable)
        assert (qtable_copy == self.qtable.qtable)
        linevast_offers = cloudomate_controller.options(self.providers["linevast"])
        self.qtable.update_values(linevast_offers[0].name, False)
        assert (qtable_copy != self.qtable.qtable)

    def test_choose_best_option(self):
        self.qtable.set_self_state("Advanced")
        self.qtable.init_qtable_and_environment(self.providers)
        best_option = self.qtable.choose_best_option()
        print(best_option)
        assert (best_option[0] == "BlueAngelHost")
        assert (best_option[1] == "KVM-6")

    def test_find_provider(self):
        self.qtable.set_self_state("Advanced")
        self.qtable.init_qtable_and_environment(self.providers)
        provider_name = self.qtable.find_provider("Basic Plan")
        assert (provider_name == "BlueAngelHost")


if __name__ == '__main__':
    unittest.main()
