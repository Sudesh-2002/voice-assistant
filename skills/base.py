from abc import ABC, abstractmethod


class Skill(ABC):
    intent_name: str

    @abstractmethod
    def execute(self, parameters: dict) -> str:
        
        raise NotImplementedError