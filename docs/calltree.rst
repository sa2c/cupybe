``calltree``
============
.. automodule:: calltree
.. currentmodule:: calltree
.. _call-tree-node:
.. autoclass:: CallTreeNode
.. autofunction:: get_call_tree
.. autofunction:: calltree_to_df


Printing and fancy recursive stuff
++++++++++++++++++++++++++++++++++

The ``calltree_to_string`` function is a versatile function that can be used
to get an ASCII representation of the call tree. It can also be used to print 
a "payload", which is anything that can be indexed with ``Cnode ID``/s.
The tree can be cut at any level. 

A possible use case is to print an inclusive metric next to a graphical 
representation of the call tree, limited to a certain depth.

.. autofunction:: calltree_to_string


.. autofunction:: iterate_on_call_tree
