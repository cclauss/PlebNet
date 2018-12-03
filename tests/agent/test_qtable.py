import copy
import unittest

from plebnet.agent.qtable import QTable
from plebnet.controllers import cloudomate_controller


class TestQTable(unittest.TestCase):

    def tearDown(self):
        pass

    def test_init_qtable_and_environment(self):
        qtable = QTable()
        assert (len(qtable.environment) == 0)
        qtable.init_qtable_and_environment(cloudomate_controller.get_vps_providers())
        assert (len(qtable.environment) > 0)
        assert (len(qtable.qtable) > 0)

    def test_calculate_measure(self):
        provider_offer = {"Price": 5, "Connection": 3, "Memory": 2}
        qtable = QTable()
        assert (qtable.calculate_measure(provider_offer) == 60)

    def test_update_environment(self):
        qtable = QTable()
        providers = cloudomate_controller.get_vps_providers()
        qtable.init_qtable_and_environment(providers)
        environment_copy = copy.deepcopy(qtable.environment)
        qtable.update_environment(providers[0])
        assert (environment_copy != qtable.environment)

    def test_update_values(self):
        qtable = QTable()
        providers = cloudomate_controller.get_vps_providers()
        qtable.init_qtable_and_environment(providers)
        qtable_copy = copy.deepcopy(qtable.qtable)
        assert (qtable_copy == qtable.qtable)
        qtable.update_environment(providers[0])
        assert (qtable_copy != qtable.qtable)


if __name__ == '__main__':
    unittest.main()
