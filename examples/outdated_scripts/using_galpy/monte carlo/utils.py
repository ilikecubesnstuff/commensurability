"""
Utilities for showcasing examples in modules.
"""
import sys

examples_namespace = {}
_default = None
def example(name = None, aliases = tuple(), default=False):
    def deco(f):
        global _default
        if default:
            _default = f
        if name:
            examples_namespace[name] = f
        else:
            examples_namespace[f.__name__] = f
        for alias in aliases:
            examples_namespace[alias] = f
        return f
    return deco

def resolve_example(default = None):
    if len(sys.argv) == 1:
        default = default or _default
        if default is None:
            raise ValueError('No default example set - you must provide an example name. Type "list" for a list of available names.')
        return default()
    
    name = ' '.join(sys.argv[1:])

    if name == 'list':
        print('Examples available:')
        for example_name in examples_namespace:
            print(f'\t{example_name}')
        return

    for example_name, func in examples_namespace.items():
        if name == example_name:
            return func()
    raise ValueError(f'No example with name "{name}". Type "list" for a list of names.')
main = resolve_example