.. PyCube documentation master file, created by
   sphinx-quickstart on Mon Mar 23 10:59:14 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyCube documentation
====================

**PyCube** is a collection of utilities that allow to convert the data contained
in ``.cubex`` files produced by ``Score-P`` into data structures that can be 
interacted with through Python libraries (e.g., Pandas).

It is basically a bynch of functions that use ``cube_dump`` and parses its 
output (see the `Cube Command line tools guide in html 
<https://apps.fz-juelich.de/scalasca/releases/cube/4.4/docs/tools-guide/html/>`_ 
and its `PDF version 
<https://apps.fz-juelich.de/scalasca/releases/cube/4.4/docs/CubeToolsGuide.pdf>`_).


Contents
++++++++++++++++++

.. toctree::
   :maxdepth: 2

   merger
   calltree
   cube_file_utils
   metrics



Indices and tables
++++++++++++++++++

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
