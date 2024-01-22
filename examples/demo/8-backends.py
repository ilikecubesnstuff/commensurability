# pretend there exists a new galactic dynamics library 'pydgeon'
# this is how to write a new backend for it (to some approximation)


from pidgey.base import Backend


class PydgeonBackend(Backend):
    def __imports__():
        import pydgeon

    def _extract_points_from_orbit(self, orbit):
        return orbit.get_points()

    def _compute_orbit(self, coord, *, pot, t_array, **kwargs):
        orbit = self.pydgeon.create_simulation(pot=pot, ic=coord)
        orbit.integrate(t_array, **kwargs)
        return orbit

    def _compute_orbits(self, coords, *, pot, t_array, **kwargs):
        orbits = self.pydgeon.create_simulation(pot=pot, ic=coords)
        orbits.integrate(t_array, **kwargs)
        return orbits

    def _precompute_namespace_hook(self, namespace):
        # helper method to populate keyword arguments in above
        ...


# this file will run, and throw an error at runtime only when this backend is initialized
# backend = PydgeonBackend()


# this kind of "import extension" behavior is isolated to its own metaclass
from iext import ExtendImports


# toy example with packages that don't exist
class Chef(ExtendImports):
    def __imports__():
        import grocer
        import kitchen

    async def pesto_pasta(self):
        pasta, pesto, parmesan = await self.grocer.request("pasta", "pesto", "parmesan")

        stove = self.kitcken.get_stove()
        kettle = self.kitchen.kettle(water=True)
        stove.add(kettle)
        kettle.add(pasta)
        await pasta.until_cooked()

        pan = self.kitchen.pan()
        pan.add(kettle.drain())
        pan.add(pesto)
        pan.add(parmesan)
        await pan.toss(minutes=3)

        plate = self.kitchen.plate()
        plate.add(pan.remove_all())
        return plate
