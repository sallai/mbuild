__author__ = 'sallai'

from mbuild.compound import Compound
from mbuild.atom import Atom
from mbuild.bond import Bond
from collections import OrderedDict
from oset import oset as OrderedSet

class AtomProxy(Atom):

    def __getattr__(self, attr):
        return self.atom.__dict__[attr]

    def __init__(self, atom):
        self.atom = atom
        self.index = None
        self.parent = None
        self.bonds = set()
        self.referrers = set()

    def __repr__(self):
        return "AtomProxy<{0}>".format(self.atom.__repr__())

class CompoundProxy(Compound):

    def __getattr__(self, attr):
        return self.compound.__dict__[attr]

    def __init__(self, compound):
        assert(isinstance(compound, Compound))
        self.compound = compound
        self.parts = OrderedSet()
        self.labels = OrderedDict()
        self.parent = None
        self.referrers = set()

    def __repr__(self):
        return "CompoundProxy<{0}>".format(self.compound.__repr__())


def is_compound(what):
    return hasattr(what,'parts')

def is_atom(what):
    return hasattr(what,'name') and hasattr(what, 'pos')

def is_bond(what):
    return hasattr(what,'atom1') and hasattr(what, 'atom2')

def is_particle(what):
    return is_atom(what) or is_compound(what)

def create_proxy(real_thing, memo=None):
    if memo is None:
        memo = OrderedDict()

    proxy = _create_proxy_atoms_and_compounds(real_thing, memo)
    create_proxy_bonds(real_thing, memo)
    create_proxy_labels(real_thing, memo)

    return proxy

def _create_proxy_atoms_and_compounds(real_thing, memo):

    if is_atom(real_thing):
        proxy = AtomProxy(real_thing)
        memo[real_thing] = proxy
        return proxy

    if is_compound(real_thing):
        proxy = CompoundProxy(real_thing)
        memo[real_thing] = proxy

        # create proxies for Atoms and Compounds first
        for part in real_thing.parts:
            if is_bond(part):
                # it is done later
                continue
            if is_particle(part):
                # recurse
                part_proxy = _create_proxy_atoms_and_compounds(part, memo)
                proxy.add(part_proxy)

        return proxy

def create_proxy_bonds(real_thing, memo):
    if is_compound(real_thing):
        proxy = memo[real_thing]

        # create proxies for Bonds
        for part in real_thing.parts:
            if is_bond(part):
                new_bond = Bond(memo[part.atom1], memo[part.atom2], part.kind)
                memo[part] = new_bond
                proxy.add(new_bond)
            # recurse
            if is_compound(part):
                create_proxy_bonds(part, memo)

def create_proxy_labels(real_thing, memo):
    if is_compound(real_thing):
        proxy = memo[real_thing]

        # create labels
        for label, part in real_thing.labels.iteritems():
            if isinstance(part, list):
                # TODO support lists with labels
                continue
            if isinstance(part, Bond):
                proxy.labels[label] = memo[part]

        # recurse
        for part in real_thing.parts:
            if is_compound(part):
                create_proxy_labels(part, memo)


if __name__ == '__main__':
    from mbuild.examples.ethane.ethane import Ethane
    c = Ethane()
    p = create_proxy(c)

    print("Top level proxy object: {}".format(p))

    print("Parts of top level proxy object:")
    for part in p.parts:
        print(" {}".format(part))

    print("Atoms of top level proxy object:")
    for atom in p.atoms:
        print(" {}".format(atom))
