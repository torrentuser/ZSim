from typing import TYPE_CHECKING, Iterable

from .PreloadDataClass import PreloadData
from .PreloadStrategy import SwapCancelStrategy

if TYPE_CHECKING:
    from zsim.sim_progress.Character.skill_class import Skill
    from zsim.simulator.dataclasses import LoadData
    from zsim.simulator.simulator_class import Simulator


class PreloadClass:
    def __init__(
        self,
        skills: Iterable["Skill"],
        *,
        load_data: "LoadData",
        apl_path: str | None = None,
        sim_instance: "Simulator | None" = None,
        **kwargs,
    ):
        self.preload_data: "PreloadData" = PreloadData(
            skills, load_data=load_data, sim_instance=sim_instance
        )
        self.apl_path = apl_path
        self.strategy = SwapCancelStrategy(self.preload_data, apl_path)

    def do_preload(self, tick, enemy, name_box, char_data):
        if self.preload_data.name_box is None:
            self.preload_data.name_box = name_box
        if self.preload_data.char_data is None:
            self.preload_data.char_data = char_data
        self.strategy.generate_actions(enemy, tick)

    def reset_myself(self, namebox):
        self.preload_data.reset_myself(namebox)
