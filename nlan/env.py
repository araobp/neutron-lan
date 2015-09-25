# 2014/4/14
# NLAN Environment 

import os
import yaml
import nlan_schema

### NLAN-Master-related env ####################################### 

# NLAN Master Home Directory (local)
NLAN_DIR = '/root/neutron-lan/nlan'

# NLAN etc directory (local)
NLAN_ETC = '/root/neutron-lan/etc'

# NLAN rpc modules (local)
NLAN_RPC_DIR = os.path.join(NLAN_DIR, 'agent/rpc')

# NLAN default state file
NLAN_STATE = 'state.yaml'

# Directory of NLAN agent scripts including NLAN modules (local)
NLAN_SCP_DIR = os.path.join(NLAN_DIR, 'agent') 

# roster file (local)
ROSTER_YAML = os.path.join(NLAN_ETC,'roster.yaml')
_roster = {}
with open(ROSTER_YAML, 'r') as f:
    _roster = yaml.load(f.read())
ROSTER = _roster

# Git repo (local)
GIT_DIR = '/root/neutron-lan/etc/.git' 
WORK_TREE = NLAN_ETC 
GIT_OPTIONS = '--git-dir {} --work-tree {}'.format(GIT_DIR, WORK_TREE)


### NLAN-Agent-related env ####################################### 

# NLAN Agent Home Directory (remote)
NLAN_AGENT_DIR = '/opt/nlan'

# NLAN agent script file (local)
NLAN_AGENT = os.path.join(NLAN_AGENT_DIR,'nlan_agent.py')

# NLAN libraries shared by both NLAN Master(local) and NLAN Agent(remote)
NLAN_LIBS = ['cmdutil.py', 'errors.py', 'argsmodel.py', 'patterns.py']

# NLAN module directories (python packages)
NLAN_MOD_DIRS = ['rpc', 'config']


### NLAN-schema-related env ####################################### 

# NLAN schema file in YAML (local)
#NLAN_SCHEMA = os.path.join(NLAN_DIR, 'agent/share/nlan.schema_0.0.3.yaml')
NLAN_SCHEMA = os.path.join(NLAN_DIR, 'agent/share/nlan.schema_0.0.6.yaml')

# Target OVSDB schema, merged with NLAN_SCHEMA
SCHEMA = 'ovsdb_nlan.schema'

_state_order, _tables, _indexes, _types = nlan_schema.analyze_schema(NLAN_SCHEMA)
# NLAN state order (rule: lower states depend on upper states)
STATE_ORDER = _state_order 
# NLAN tables
TABLES = _tables
# List indexes for NLAN "dvsdvr" state 
INDEXES = _indexes 
# NLAN state parameter types
TYPES = _types 


### Others ####################################### 

# nlan.py SSH connect timeout (in seconds)
SSH_TIMEOUT = 10.0

# nlan.py PING check wait time (in seconds)
PING_CHECK_WAIT = 10

