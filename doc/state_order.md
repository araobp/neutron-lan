Ordering NLAN states and parameters
===================================
2014/4/23

Rule 1
------
* Downward operations for add/update, and upward operations for delete.
* State order is imperative, while Param order is declarative.
* State order is defined in the NLAN schema in YAML.

YAML state file
<pre>
router1:                   add/update       delete
    state 1:                   |              ^
       param 1-1: value 1-1    |              |
       param 1-2: value 1-2    |              |
             :                 |              |
    state 2:                   | Downward     | Upward
       param 2-1: value 2-1    | operations   | operations
       param 2-2: value 2-2    |              |
             :                 |              |
    state 3:                   |              |
       param 3-1: value 3-1    |              |
       param 3-2: value 3-2    |              |
             :                 |              |
router 2:                      |              |
             :                 V              |
</pre>

For add/update operations,
1, 1-1 => 1, 1-2 => 2, 2-1 => 2, 2-2 => 3, 3-1 => 3, 3-2 ...
  
For delete operations,
3, 3-2 => 3, 3-1 => 2, 2-2 => 2, 2-1 => 1, 1-2 => 1, 1-1 ...

yamldiff.py generates the operations following the rule.


Rule 2
------
Placeholders implicitly define dependencies among states/params, and a template engine such as "dvsdvr.py" fills out those placeholders with those dependencies in mind.

In other words, the algorithm in the template engine defines the dependencies.

YAML state file
<pre>
router1:                   add/update       delete
    state 1:                   |              ^
       param 1-1: value 1-1    |              |
       param 1-2: value 1-2    |              |
             :                 |              |
    state 2:                   | Downward     | Upward
       param 2-1: value 2-1    | operations   | operations
       param 2-2: plhd  a      |              |
             :                 |              |
    state 3:                   |              |
       param 3-1: value 3-1    |              |
       param 3-2: plhd b       |              |
             :                 |              |
router 2:                      |              |
    state 2:                   |              |
        param 1-1: value 1-1   |              |
             :                 V              |
</pre>

For example, "plhd b" as a placeholder is dependent on router 2's value 2-1, and another placeholder "plhd a" is dependent on router 1's value 1-1.

