Rollback Blueprint
==================

Current rollback mechanism
--------------------------

nlan.py init.run
nlan.py -R deploy

The commands above initialize all the states of the routers on the roster, then deploy the previous states to the routers.

Improved rollback
-----------------

- nlan.py init.run with '-R' option initializes only the modified states.
- nlan.py -R deploy sends the state change request to the modifed states.
- reinforced paramter checks at each config module: check _param before executing commands.

New function to be introduced
-----------------------------

clear() at each config module. The function tries to clear the state even under an unstable condition due to some bug.

An example of unstable conditions:
- an actual config by CLI and its state in OVSDB have some mismatches.


