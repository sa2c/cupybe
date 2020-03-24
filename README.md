# PyCUBE

This is a repository of python modules and function that can be used to 
extract and organise data contained in '.cubex' files.

The documentation is hosted on [readthedocs.io](https://pycubelib.readthedocs.io/en/latest/index.html).

## Notes
* The script `/test/runtests.sh` can be used to conveniently run the few tests
  available at the moment.
* In order for the tests to work, the environment variable `PYTHONPATH` needs 
  to include the `src` directory that contains all the libraries (`runtests.sh`
  does that).
  It also require the program `cube_dump` to be installed and in the `$PATH`.
* The project is not completed. While the main functionalities have been 
  implemented, the organisation of them into functions might not be optimal.
* The library has been tested/needs cubelib 4.4.4.

## TODO
* System tree:
  The system tree should be easy to implement extending the same machinery
  used for the call tree.

* Expand the possibilities for metric conversions (if asking `cube_dump` 
  directly for the inclusive metrics is not enough).

