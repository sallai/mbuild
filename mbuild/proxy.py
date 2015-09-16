import mbuild
from lib.moieties.ch3 import CH3

__author__ = 'sallai'

from mbuild.compound import Compound
from mbuild.atom import Atom
from mbuild.bond import Bond
from collections import OrderedDict
from oset import oset as OrderedSet

class AtomProxy(Atom):

    def __getattr__(self, attr):
        return getattr(self.wrapped, attr)

    def __init__(self, atom):
        assert(isinstance(atom, Atom))
        self.wrapped = atom
        self.index = None
        self.parent = None
        self.bonds = set()
        self.referrers = set()

    def proxy_for(self):
        if hasattr(self.wrapped,'wrapped'):
            return self.wrapped.proxy_for()
        else:
            return self.wrapped.__class__

    def __repr__(self):
        return "AtomProxy<{0}>".format(self.wrapped.__repr__())

class CompoundProxy(Compound):

    def __getattr__(self, attr):
        return getattr(self.wrapped, attr)

    def __init__(self, compound):
        assert(isinstance(compound, Compound))
        self.wrapped = compound
        self.parts = OrderedSet()
        self.labels = OrderedDict()
        self.parent = None
        self.referrers = set()

    def proxy_for(self):
        if hasattr(self.wrapped,'wrapped'):
            return self.wrapped.proxy_for()
        else:
            return self.wrapped.__class__


    def __repr__(self):
        return "CompoundProxy<{0}>".format(self.wrapped.__repr__())


def is_compound(what):
    return hasattr(what,'parts')

def is_atom(what):
    return hasattr(what,'name') and hasattr(what, 'pos')

def is_bond(what):
    return hasattr(what,'atom1') and hasattr(what, 'atom2')

def is_particle(what):
    return is_atom(what) or is_compound(what)

def create_proxy(real_thing, memo=None, leaf_classes=None):
    if memo is None:
        memo = OrderedDict()

    if leaf_classes is None:
        leaf_classes = ()

    proxy = _create_proxy_atoms_and_compounds(real_thing, memo, leaf_classes)
    _create_proxy_bonds(real_thing, memo)
    _create_proxy_labels(real_thing, memo)

    return proxy

def _create_proxy_atoms_and_compounds(real_thing, memo, leaf_classes):

    if is_atom(real_thing):
        proxy = AtomProxy(real_thing)
        memo[real_thing] = proxy
        return proxy

    if is_compound(real_thing):
        proxy = CompoundProxy(real_thing)
        memo[real_thing] = proxy

        if isinstance(real_thing, leaf_classes) or ( hasattr(real_thing, 'wrapped') and real_thing.proxy_for() in leaf_classes):
            # we're at a leaf compound, dont recurse
            return proxy
        else:
            # recursively create proxies for parts
            # let's do Atoms and Compounds in this recursion (we'll do bonds and labels later)
            for part in real_thing.parts:
                if is_bond(part):
                    # it is done later
                    continue
                if is_particle(part):
                    # recurse
                    part_proxy = _create_proxy_atoms_and_compounds(part, memo, leaf_classes)
                    proxy.add(part_proxy)

            return proxy

def _create_proxy_bonds(real_thing, memo):
    if is_compound(real_thing):

        # create proxies for Bonds
        for part in real_thing.parts:
            if is_bond(part):
                if part.atom1 in memo and part.atom2 in memo:
                    new_bond = Bond(memo[part.atom1], memo[part.atom2], part.kind)
                    memo[part] = new_bond
                    memo[real_thing].add(new_bond)
            # recurse, even if we're in a leaf node, because there might be bonds in there that point out of the compound
            if is_compound(part):
                _create_proxy_bonds(part, memo)

def _create_proxy_labels(real_thing, memo):
    if is_compound(real_thing):

        # create labels
        for label, part in real_thing.labels.iteritems():
            if isinstance(part, list):
                # TODO support lists with labels
                continue
            if (is_particle(part) or is_bond(part)) and part in memo:
                memo[real_thing].labels[label] = memo[part]

        # recurse
        for part in real_thing.parts:
            if is_compound(part):
                _create_proxy_labels(part, memo)


if __name__ == '__main__':
    from mbuild.examples.ethane.ethane import Ethane
    c = Ethane()
    # c = create_proxy(c)
    p = create_proxy(c, leaf_classes=mbuild.lib.moieties.ch3.CH3)

    print("Top level proxy object: {}".format(p))

    print("Parts of top level proxy object:")
    for part in p.parts:
        print(" {}".format(part))

    print("Atoms of top level proxy object:")
    for atom in p.atoms:
        print(" {}".format(atom))
