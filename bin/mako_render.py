import sys
from mako.template import Template 

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        print Template(text=f.read()).render()

