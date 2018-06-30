import sc2
import random
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY

class Proxy2GateBot(sc2.BotAI):
    def __init__(self):
        self.proxy_location_reached = False
        self.proxy_pylon_built = False
        self.proxy_gateways_built = False
        

    async def on_step(self, iteration):
        if not self.proxy_pylon_built:
            await self.distribute_workers()

        self.proxy_location = self.game_info.map_center.towards(self.enemy_start_locations[0], 5)

        if not self.proxy_location_reached:
            worker = self.select_build_worker(self.proxy_location)
            await self.do(worker.move(self.proxy_location))
            self.proxy_location_reached = True

        if self.proxy_location_reached and self.can_afford(PYLON) and not self.proxy_pylon_built:
            await self.build(PYLON, near=self.proxy_location)
            self.proxy_pylon_built = True

        if self.units(PYLON).ready.amount >= 1 and not self.proxy_gateways_built:
            await self.build(GATEWAY, near=self.proxy_location)
            await self.build(GATEWAY, near=self.proxy_location)
            self.proxy_gateways_built = True

    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    async def build_pylon(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

run_game(maps.get("AbyssalReefLE"), [
        Bot(Race.Protoss, Proxy2GateBot()),
        Computer(Race.Zerg, Difficulty.Easy)
        ], realtime=True)