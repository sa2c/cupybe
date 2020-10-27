# CUPyBE

This is a repository of python modules and function that can be used to 
extract and organise data contained in `.cubex` files, produced, e.g., by 
[Score-P](https://www.vi-hps.org/projects/score-p/).

CUPyBE at the moment uses the command line tools from cubelib (see, e.g., 
[Cube 4 downloads on scalasca.org](https://www.scalasca.org/scalasca/software/cube-4.x/download.html))
to  extract information from `.cubex` files. 
The documentation is hosted on [readthedocs.io](https://cupybe.readthedocs.io/en/latest/index.html).

For a solution that uses directly `tarfile` and `xml.etree.ElementTree` without needing CubeLib, see [Marshall Ward's cubex project](https://github.com/marshallward/cubex), 

## Dependencies
* Python >= 3.6. For packages, see `Pipfile`.
* Tested with CubeLib 4.4.4, Python (3.6.10 | 3.7.7 | 3.8.2 )

## Notes
* The script `/test/runtests.sh` can be used to conveniently run the few tests
  available at the moment.
* In order for the tests to work, the environment variable `PYTHONPATH` needs 
  to include the `src` directory that contains all the libraries (`runtests.sh`
  does that).
  It also require the program `cube_dump` to be installed and in the `$PATH`.
* The project is not completed. While the main functionalities have been 
  implemented, the organisation of them into functions might not be optimal.

## TODO
* System tree:
  The system tree should be easy to implement extending the same machinery
  used for the call tree.

* Expand the possibilities for metric conversions (if asking `cube_dump` 
  directly for the inclusive metrics is not enough).

## License
CUPyBE is licensed according to the 3-clause license.
