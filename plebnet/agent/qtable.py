import json
import os

from appdirs import user_config_dir

from plebnet.controllers import cloudomate_controller


class QTable:
    learning_rate = 0.005
    environment_lr = 0.4
    discount = 0.05
    qtable = {}
    environment = []
    providers_offers = []

    def __init__(self):
        pass

    def init_qtable_and_environment(self, providers):
        self.init_providers_offers(providers)

        for provider_of in self.providers_offers:
            prov = {}
            environment_arr = {}
            for i, provider_name in enumerate(self.providers_offers):
                provider_offer = self.providers_offers[provider_name]
                prov[provider_offer["Name"]] = self.calculate_measure(provider_offer)
                environment_arr[provider_offer["Name"]] = 0
            self.qtable[provider_of["Name"]] = prov
            self.environment[provider_of["Name"]] = environment_arr

    @staticmethod
    def calculate_measure(provider_offer):
        return float(provider_offer["Price"]) * float(provider_offer["Connection"]) * float(provider_offer["Memory"])

    def init_providers_offers(self, providers):
        for provider in providers:
            options = cloudomate_controller.options(provider)
            print(options)
            for i, option in enumerate(options):
                element = {
                    "ProviderName": provider.get_metadata()[0] + str(i),
                    "Name": option.name,
                    "Connection": option.connection,
                    "Price": option.price,
                    "Memory": option.memory
                }
                print(element)
                self.providers_offers.append(element)

    def update_values(self, curr_provider, status=False):
        self.update_environment(curr_provider, status)

        for i, provider_offer in enumerate(self.providers_offers):
            for j, provider_of in enumerate(self.providers_offers):
                learning_compound = (self.environment[provider_offer][provider_of]\
                                                            + self.discount * self.max_action_value(provider_offer) \
                                                            - self.qtable[provider_offer][provider_of])

                self.qtable[provider_offer][provider_of] = self.qtable[provider_offer][provider_of][1]\
                                                           + self.learning_rate * learning_compound

    def update_environment(self, provider, status):

        for i, actions in enumerate(self.environment):
            if not status:
                self.environment[actions][provider] -= self.environment_lr
            else:
                self.environment[actions][provider] += self.environment_lr

    def max_action_value(self, provider):
        max_value = -100000
        for i, provider_offer in enumerate(self.qtable):
            if max_value < self.qtable[provider_offer][provider]:
                max_value = self.qtable[provider_offer][provider]
        return max_value

    def read_dictionary(self, providers=None):

        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')

        if not os.path.exists(filename):
            self.init_qtable_and_environment(providers)
            self.write_dictionary()
        else:
            with open(filename) as json_file:
                data = json.load(json_file)
                self.environment = data['environment']
                self.qtable = data['qtable']
                self.providers_offers = data['providers_offers']

    def write_dictionary(self):
        """
        Writes the DNA configuration to the DNA.json file.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')
        to_save_var = {
            "environment": self.environment,
            "qtable": self.qtable,
            "providers_offers": self.providers_offers

        }
        with open(filename, 'w') as json_file:
            json.dump(to_save_var, json_file)
