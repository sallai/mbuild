
# coding: utf-8

# Ethane: Reading from files, Ports and coordinate transforms
# -----------------------------------------------------------
# 
# __Note__: mBuild expects all distance units to be in nanometers.
# 
# In this example, we'll cover reading molecular components from files, introduce the concept of `Ports` and start using some coordinate transforms.
# 
# As you probably noticed while creating your methane mocule in the last tutorial, manually adding `Particles` and `Bonds` to a `Compound` is a bit cumbersome. The easiest way to create small, reusable components, such as methyls, amines or monomers, is to hand draw them using software like [Avogadro](http://avogadro.cc/wiki/Main_Page) and export them as either a .pdb or .mol2 file (the file should contain connectivity information).
# 
# Let's start by reading a methyl group from a `.pdb` file:

# In[1]:

import mbuild as mb

class CH3(mb.Compound):
    def __init__(self):
        super(CH3, self).__init__()

        mb.load('ch3.pdb', compound=self)


# Now let's use our first coordinate transform to center the methyl at its carbon atom:

# In[2]:

import mbuild as mb

class CH3(mb.Compound):
    def __init__(self):
        super(CH3, self).__init__()

        mb.load('ch3.pdb', compound=self)
        mb.translate(self, -self[0].pos)  # Move carbon to origin.


# Now we have a methyl group loaded up and centered. In order to connect `Compounds` in mBuild, we make use of a special type of `Compound`: the `Port`. A `Port` is a `Compound` with two sets of four "ghost" `Particles`. In addition ``Ports`` have an `anchor` attribute which typically points to a `Compound` that the `Port` should be associated with. In our methyl group, the `Port` should be anchored to the carbon atom so that we
# can now form bonds to this carbon:

# In[3]:

import mbuild as mb

class CH3(mb.Compound):
    def __init__(self):
        super(CH3, self).__init__()

        mb.load('ch3.pdb', compound=self)
        mb.translate(self, -self[0].pos)  # Move carbon to origin.

        port = mb.Port(anchor=self[0])
        self.add(port, label='up')
        # Place the port at approximately have a C-C bond length.
        mb.translate(self['up'], [0, -0.07, 0])  


# By default, `Ports` are never output from the mBuild structure. However, it can be useful to look at a molecule with the `Ports` to check your work as you go:

# In[4]:

CH3().visualize(show_ports=True)


# When two `Ports` are connected, they are forced to overlap in space and their parent `Compounds` are rotated and translated by the same amount. 
# 
# __Note:__ If we tried to connect two of our methyls right now using only one set of four ghost particles, not only would the `Ports` overlap perfectly, but the carbons and hydrogens would also perfectly overlap - the 4 ghost atoms in the both `Port` are arranged identically with respect to the other atoms. 
# 
# Forcing the port in <-CH3 to overlap with <-CH3 would just look like <-CH3
# 
# To solve this problem, every port contains a second set of 4 ghost atoms pointing in the opposite direction. When two `Compounds` are connected, the port that places the anchor atoms the farthest away from each other is chosen automatically to prevent this overlap scenario. 
# 
# When <->CH3 and <->CH3 are forced to overlap, the CH3<->CH3 is automatically chosen.
# 
# Now the fun part: stick 'em together to create an ethane:

# In[5]:

import mbuild as mb

class Ethane(mb.Compound):
    def __init__(self):
        super(Ethane, self).__init__()

        self.add(CH3(), "methyl1")
        self.add(CH3(), "methyl2")
        mb.equivalence_transform(compound=self['methyl1'], 
                                 from_positions=self['methyl1']['up'], 
                                 to_positions=self['methyl2']['up'])


# In[6]:

ethane = Ethane()
ethane.visualize()


# In[7]:

ethane.visualize(show_ports=True)


# Above, the `equivalence_transform()` function takes a `Compound` and then rotates and translates it such that two other `Compounds` overlap. Typically, as in
# this case, those two other `Compounds` are `Ports` - in our case, `methyl1['up']` and `methyl2['up']`.

# In[8]:

# Save to .mol2
ethane.save('ethane.mol2')


# In[ ]:



