Scenario Runner
===============

nlans.py is a NLAN scenario runner. 

       [nlans.py] ---> [nlan.py] --- CRUD Operations ---> [nlan_agent.py]
           ^
           |
        ------------
      / Scenario  /--
     /  (YAML)   / /
    ------------  /
     ------------

Scenario Language
-----------------

All the scenarios are written in YAML with the following commands:
- comment
- do
- sleep
- nlan

nlan has the following arguments:
- router
- options
- args
- assert
- assertRaises

"assert" and "assertRaises" are mainly for integration testing.

