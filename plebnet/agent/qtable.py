import json
import os

from appdirs import user_config_dir

from plebnet.controllers import cloudomate_controller


class QTable:
    learning_rate = 0.005
    environment_lr = 0.4
    discount = 0.05


    def __init__(self):
        self.qtable = {}
        self.environment = {}
        self.providers_offers = []
        self.self_state = ""
        pass

    def init_qtable_and_environment(self, providers):
        self.init_providers_offers(providers)

        for provider_of in self.providers_offers:
            prov = {}
            environment_arr = {}
            for provider_offer in self.providers_offers:
                prov[provider_offer["name"]] = self.calculate_measure(provider_offer)
                environment_arr[provider_offer["name"]] = 0
            self.qtable[provider_of["name"]] = prov
            self.environment[provider_of["name"]] = environment_arr

    @staticmethod
    def calculate_measure(provider_offer):
        return 1/(100*float(provider_offer["price"])) * float(provider_offer["connection"]) * float(provider_offer["memory"])

    def init_providers_offers(self, providers):
        for i, id in enumerate(providers):
            options = cloudomate_controller.options(providers[id])
            for i, option in enumerate(options):
                element = {
                    "provider_name": providers[id].get_metadata()[0],
                    "name": option.name,
                    "connection": option.connection,
                    "price": option.price,
                    "memory": option.memory
                }
                self.providers_offers.append(element)

    def update_values(self, curr_provider, status=False):
        self.update_environment(curr_provider, status)

        for provider_offer in self.providers_offers:
            for provider_of in self.providers_offers:
                learning_compound = self.environment[provider_offer["name"]][provider_of["name"]] \
                                    + self.discount * self.max_action_value(provider_offer) \
                                    - self.qtable[provider_offer["name"]][provider_of["name"]]

                self.qtable[provider_offer["name"]][provider_of["name"]] = \
                    self.qtable[provider_offer["name"]][provider_of["name"]] \
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
            if max_value < self.qtable[provider_offer][provider["name"]]:
                max_value = self.qtable[provider_offer][provider["name"]]
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
        candidate = {"option_name": "", "provider_name": "", "score": -1000}
        for i, offer_name in enumerate(self.qtable):
            if candidate["score"] < self.qtable[self.self_state][offer_name]:
                candidate["option_name"] = offer_name
                candidate["score"] = self.qtable[self.self_state][offer_name]
                candidate["provider_name"] = self.find_provider(offer_name)
        return candidate["provider_name"], candidate["option_name"]

    def find_provider(self, offer_name):
        for offers in self.providers_offers:
            if offers["name"] == offer_name:
                return offers["provider_name"]
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
