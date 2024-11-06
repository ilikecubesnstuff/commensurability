import astropy.coordinates as c
import astropy.units as u

from commensurability.utils import make_quantity, collapse_coords


class TestMakeQuantity:

    def test_dimensionless_value(self):
        assert make_quantity(1, u.kpc) == 1 * u.kpc
    
    def test_dimensionful_value(self):
        assert make_quantity(1 * u.kpc, u.kpc) == 1 * u.kpc
    
    def test_dimensionless_collection(self):
        assert all(make_quantity([1, 2, 3], u.kpc) == [1, 2, 3] * u.kpc)

    def test_dimensionful_collection(self):
        assert all(make_quantity([1, 2, 3] * u.kpc, u.kpc) == [1, 2, 3] * u.kpc)


class TestCollapseCoords:

    def test_single_coord(self):
        coord = c.SkyCoord(x=1 * u.kpc, y=2 * u.kpc, z=3 * u.kpc, v_x=4 * u.km/u.s, v_y=5 * u.km/u.s, v_z=6 * u.km/u.s, frame="galactocentric", representation_type="cartesian")
        assert collapse_coords(coord) == coord
    
    def test_multiple_coords(self):
        coords = [
            c.SkyCoord(x=1 * u.kpc, y=2 * u.kpc, z=3 * u.kpc, v_x=4 * u.km/u.s, v_y=5 * u.km/u.s, v_z=6 * u.km/u.s, frame="galactocentric", representation_type="cartesian"),
            c.SkyCoord(x=7 * u.kpc, y=8 * u.kpc, z=9 * u.kpc, v_x=10 * u.km/u.s, v_y=11 * u.km/u.s, v_z=12 * u.km/u.s, frame="galactocentric", representation_type="cartesian")
        ]
        result = collapse_coords(coords)
        assert all(result.x == [1, 7] * u.kpc)
        assert all(result.y == [2, 8] * u.kpc)
        assert all(result.z == [3, 9] * u.kpc)
        assert all(result.v_x == [4, 10] * u.km/u.s)
        assert all(result.v_y == [5, 11] * u.km/u.s)
        assert all(result.v_z == [6, 12] * u.km/u.s)
    
    def test_coord_collection(self):
        coords = c.SkyCoord(
            x=[1, 7] * u.kpc,
            y=[2, 8] * u.kpc,
            z=[3, 9] * u.kpc,
            v_x=[4, 10] * u.km/u.s,
            v_y=[5, 11] * u.km/u.s,
            v_z=[6, 12] * u.km/u.s,
            frame="galactocentric",
            representation_type="cartesian"
        )
        assert all(collapse_coords(coords) == coords)
