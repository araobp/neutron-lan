from ovsdb import OvsdbRow

def getrow(*args):
    table = args[0]
    index = None
    if len(args) > 1:
        v = args[2]
        try:
            v = eval(v)
            if isinstance(v, int):
                index = (args[1], eval(args[2]))
        except:
            index = (args[1], args[2])
    row = OvsdbRow(table, index)
    return row.getrow()

