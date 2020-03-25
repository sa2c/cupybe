.. PyCube documentation master file, created by
   sphinx-quickstart on Mon Mar 23 10:59:14 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyCube documentation
====================

**PyCube** is a collection of utilities that allow to convert the data contained
in ``.cubex`` files produced by ``Score-P`` into data structures that can be 
interacted with through Python libraries (e.g., Pandas).

It is basically a bunch of functions that use ``cube_dump`` and parse its 
output (see the `Cube Command line tools guide in html 
<https://apps.fz-juelich.de/scalasca/releases/cube/4.4/docs/tools-guide/html/>`_ 
and its `PDF version 
<https://apps.fz-juelich.de/scalasca/releases/cube/4.4/docs/CubeToolsGuide.pdf>`_).
For this reason, in order for **PyCube** to work it is necessary to have 
``cubelib`` installed.

Main ideas
++++++++++

The two most important functions to use are possibly 
:ref:`process_cubex <process-cubex>` and
:ref:`process_multi <process-multi>`, which are used to parse a single (or many)
``.cubex`` files at once, yielding data that is mostly stored into 
``pandas.DataFrame``\s. In addition to that, the calltree is also stored 
in a recursive fashion using :ref:`CallTreeNode <call-tree-node>` objects. 

Notes
+++++

* The "system tree" is not dealt with at the moment.  This means that data can 
  be indexed only using ``Thread ID``\s instead of a somewhat more 
  sophisticated way using nodes and MPI ranks.  
  Only the "call tree" is implemented.  
  
* The inclusive/exclusive conversions are not fully implemented. For those 
  metrics that are "Inclusive convertible", the conversion from exclusive to
  inclusive along the call tree have been implemented. 
  Anyway it is possible to ask ``cube_dump`` for the inclusive metrics if one 
  likes.
  
Modules
+++++++

.. toctree::
   :maxdepth: 2

   merger
   calltree
   cube_file_utils
   metrics
   calltree_conversions
   index_conversions


Indices and tables
++++++++++++++++++

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
