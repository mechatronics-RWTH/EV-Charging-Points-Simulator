from typing import List
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import HierachicalRlOption


class OptionsFramework:

    def __init__(self):
        self.options: List[HierachicalRlOption] = None
        self.meta_policy = None
        self.current_active_option: HierachicalRlOption = None
        self.meta_action = None
        self.option_mapping = {}

    def create_option_mapping(self):
        if self.options == None or len(self.options) == 0:
            raise ValueError("No options to map")
        for option in self.options:
            self.option_mapping[option.option_name] = option

    def select_option(self):
        pass