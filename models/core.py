import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Attack:
    _id: str
    name: str
    media: str
    description: str
    damage_range: Tuple[int, int]

    def get_damage(self) -> int:
        x, y = self.damage_range
        return random.randint(x, y)

    def mana_usage(self) -> int:
        average = sum(self.damage_range) // 2
        return average

@dataclass
class Account:
    user_id: int
    currency: int
    exp: int
    max_exp: int
    attacks: List[Attack]

    def level(self) -> int:
        # max exp goes up in intervals of 50
        return self.max_exp // 50

TEST_ATTACK = Attack(
    _id="test-attack-e42y1312",
    name="Test Attack",
    description="Test Attack",
    media="https://imgix.ranker.com/user_node_img/50125/1002481001/original/1002481001-photo-u1?auto=format&q=60&fit=crop&fm=pjpg&dpr=2&w=375",
    damage_range=(50, 100)
)
