import json
import os

from appdirs import user_config_dir

from plebnet.controllers import cloudomate_controller


class QTable:
    learning_rate = 0.005
    environment_lr = 0.4
    discount = 0.05
    qtable = {}
    environment = {}
    providers_offers = []
    self_state = ""

    def __init__(self):
        pass

    def init_qtable_and_environment(self, providers):
        self.init_providers_offers(providers)

        for provider_of in self.providers_offers:
            prov = {}
            environment_arr = {}
            for provider_offer in self.providers_offers:
                prov[provider_offer["Name"]] = self.calculate_measure(provider_offer)
                environment_arr[provider_offer["Name"]] = 0
            self.qtable[provider_of["Name"]] = prov
            self.environment[provider_of["Name"]] = environment_arr

    @staticmethod
    def calculate_measure(provider_offer):
        return 1/(100*float(provider_offer["Price"])) * float(provider_offer["Connection"]) * float(provider_offer["Memory"])

    def init_providers_offers(self, providers):
        for i, id in enumerate(providers):
            options = cloudomate_controller.options(providers[id])
            for i, option in enumerate(options):
                element = {
                    "ProviderName": providers[id].get_metadata()[0],
                    "Name": option.name,
                    "Connection": option.connection,
                    "Price": option.price,
                    "Memory": option.memory
                }
                self.providers_offers.append(element)

    def update_values(self, curr_provider, status=False):
        self.update_environment(curr_provider, status)

        for provider_offer in self.providers_offers:
            for provider_of in self.providers_offers:
                learning_compound = self.environment[provider_offer["Name"]][provider_of["Name"]] \
                                    + self.discount * self.max_action_value(provider_offer) \
                                    - self.qtable[provider_offer["Name"]][provider_of["Name"]]

                self.qtable[provider_offer["Name"]][provider_of["Name"]] = \
                    self.qtable[provider_offer["Name"]][provider_of["Name"]] \
                    + self.learning_rate * learning_compound

    def update_environment(self, provider, status):

        for i, actions in enumerate(self.environment):
            if not status:
                self.environment[actions][provider] = self.environment[actions][provider] - self.environment_lr
            else:
                self.environment[actions][provider] += self.environment_lr

    def max_action_value(self, provider):
        max_value = -100000
        for i, provider_offer in enumerate(self.qtable):
            if max_value < self.qtable[provider_offer][provider["Name"]]:
                max_value = self.qtable[provider_offer][provider["Name"]]
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

    def choose_best_option(self):
        candidate = {"OptionName": "", "ProviderName": "", "Score": -1000}
        for i, offer_name in enumerate(self.qtable):
            if candidate["Score"] < self.qtable[self.self_state][offer_name]:
                candidate["OptionName"] = offer_name
                candidate["Score"] = self.qtable[self.self_state][offer_name]
                candidate["ProviderName"] = self.find_provider(offer_name)
        return candidate["ProviderName"], candidate["OptionName"]

    def find_provider(self, offer_name):
        for offers in self.providers_offers:
            if offers["Name"] == offer_name:
                return offers["ProviderName"]
        raise ValueError("Can't find provider for " + offer_name)

    def set_self_state(self, self_state):
        self.self_state = self_state

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
