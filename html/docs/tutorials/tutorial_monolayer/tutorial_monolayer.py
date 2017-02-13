
# coding: utf-8

# Monolayer: Complex hierarchies, patterns, tiling and writing to files
# ---------------------------------------------------------------
# 
# __Note__: mBuild expects all distance units to be in nanometers.
# 
# In this example, we'll cover assembling more complex hierarchies of components using patterns, tiling and how to output systems to files. To illustrate these concepts, let's build an alkane monolayer on a crystalline substrate.
# 
# First, let's build our monomers and functionalized them with a silane group which we can then attach to the substrate. The `Alkane` example uses the `polymer` tool to combine `CH2` and `CH3` repeat units. You also have the option to cap the front and back of the chain or to leave a `CH2` group with a dangling port. The `Silane` compound is a Si(OH)<sub>2</sub> group with two ports facing out from the central Si. Lastly, we combine `alkane` with `silane` and add a label to `AlkylSilane` which points to, `silane['down']`. This allows us to reference it later using `AlkylSilane['down']` rather than `AlkylSilane['silane']['down']`.
# 
# __Note:__ In `Compounds` with multiple `Ports`, by convention, we try to label every `Port` successively as 'up', 'down', 'left', 'right', 'front', 'back' which should roughly correspond to their relative orientations. This is a bit tricky to enforce because the system is so flexible so use your best judgement and try to be consistent! The more components we collect in our library with the same labeling conventions, the easier it becomes to build ever more complex structures.

# In[1]:

import mbuild as mb

from mbuild.examples import Alkane
from mbuild.lib.moieties import Silane


class AlkylSilane(mb.Compound):
    """A silane functionalized alkane chain with one Port. """
    def __init__(self, chain_length):
        super(AlkylSilane, self).__init__()

        alkane = Alkane(chain_length, cap_end=False)
        self.add(alkane, 'alkane')
        silane = Silane()
        self.add(silane, 'silane')
        mb.equivalence_transform(self['alkane'], self['alkane']['down'], self['silane']['up'])

        # Hoist silane port to AlkylSilane level.
        self.add(silane['down'], 'down', containment=False)


# In[2]:

AlkylSilane(5).visualize()


# Now let's create a substrate to which we can later attach our monomers:

# In[3]:

import mbuild as mb
from mbuild.lib.surfaces import Betacristobalite

surface = Betacristobalite()
tiled_surface = mb.TiledCompound(surface, n_tiles=(2, 1, 1))


# Here we've imported a beta-cristobalite surface from our component library. The `TiledCompound` tool allows you replicate any `Compound` in the x-, y-
# and z-directions by any number of times - 2, 1 and 1 for our case.
# 
# Next, let's create our monomer and a hydrogen atom that we'll place on unoccupied surface sites:

# In[4]:

from mbuild.lib.atoms import H
alkylsilane = AlkylSilane(chain_length=10)
hydrogen = H()


# Then we need to tell mBuild how to arrange the chains on the surface. This is accomplished with the "pattern" tools. Every pattern is just a collection of points. There are all kinds of patterns like spherical, 2D, regular, irregular etc. When you use the `apply_pattern` command, you effectively superimpose the pattern onto the host compound, mBuild figures out what the closest ports are to the pattern points and then attaches copies of the guest onto the binding sites identified by the pattern:
# 

# In[5]:

pattern = mb.Grid2DPattern(8, 8)  # Evenly spaced, 2D grid of points.

# Attach chains to specified binding sites. Other sites get a hydrogen.
chains, hydrogens = pattern.apply_to_compound(host=tiled_surface, guest=alkylsilane, backfill=hydrogen)


# Also note the `backfill` optional argument which allows you to place a different compound on any unused ports. In this case we want to backfill with hydrogen atoms on every port without a chain.
# 
# 
# And that's it! Check out `examples.alkane_monolayer` for the fully wrapped class.

# In[6]:

monolayer = mb.Compound([tiled_surface, chains, hydrogens])
monolayer.visualize() # Warning: may be slow in IPython notebooks


# In[ ]:

# Save as .mol2 file
monolayer.save('monolayer.mol2')


# In[ ]:



