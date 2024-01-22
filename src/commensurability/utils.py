import astropy.units as u


def make_quantity(obj, unit: u.Unit):
    if isinstance(obj, u.Quantity):
        return obj
    return obj * unit
