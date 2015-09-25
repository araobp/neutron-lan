#
# cmdutil.py: command execution utilities. 
# Usage example: python cmd.py 'ls -l' 'check_output'
# Refer to Python documentation: http://docs.python.org/2/library/subprocess.html
#
# 2014/1/29

import subprocess

CalledProcessError = subprocess.CalledProcessError

		
def _cmd(check, persist, *args):

    cmd_args = []
    args = list(args)
    for l in args:
        for ll in l.split():
            cmd_args.append(ll)
    return _cmd2(check=check, persist=persist, args=cmd_args)


# If type(args) is list, use this function.
def _cmd2(check, persist, args):
   
    logger = None
    init = False
    try:
        if 'logger' in __n__:
            logger = __n__['logger']
        if 'init' in __n__ and __n__['init'] == 'start':
            init = True
    except:
        pass

    argstring = ' '.join(args)
    logstr = 'cmd: ' + argstring 

    if persist:
        if init:
            logstr = logstr + ' [SKIPPED...]'
            if logger:
                logger.debug(logstr)
            return

    out = None
    returncode = 0
    def log():
        if logger:
            if out:
                logger.debug('{}\n{}'.format(logstr, out))
            else:
                logger.debug(logstr)
    
    try:
        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except CalledProcessError as e:
        if check == 'call':
            returncode = e.returncode 
        else:
            log()
            raise CmdError(argstring, e.returncode, out)
    except Exception as e:
        if check == 'call':
            returncode = e.returncode 
        else:
            log()
            raise CmdError(argstring, 1)

    log()

    if check == 'call':
        return returncode
    elif check == 'check_call':
        return 0
    else:
        return out


class CmdError(Exception):

    def __init__(self, command, returncode, out=None):

        self.message = "Command execution error" 
        self.command = command
        self.returncode = returncode
        self.out = out

    def __str__(self):

        message = ''
        return self.message

# If you can ignore error condition, use this function.
def cmd(*args):
	return _cmd('call', False, *args)

def cmd2(args):
        return _cmd2('call', False, args)

def cmdp(*args):
	return _cmd('call', True, *args)

def cmd2p(args):
        return _cmd2('call', True, args)

# If you want the program to stop in case of error, use this function.	
def check_cmd(*args):
	return _cmd('check_call', False, *args)

def check_cmd2(args):
        return _cmd2('check_call', False, args)

def check_cmdp(*args):
	return _cmd('check_call', True, *args)

def check_cmd2p(args):
        return _cmd2('check_call', True, args)

# If you want to get command output, use this function.
def output_cmd(*args):
	return _cmd('check_output', False, *args)

def output_cmd2(args):
        return _cmd2('check_output', False, args)
	
def output_cmdp(*args):
	return _cmd('check_output', True, *args)

def output_cmd2p(args):
        return _cmd2('check_output', True, args)


if __name__ == "__main__":

    import sys
    import unittest
    import __builtin__

    class TestSequenceFunctions(unittest.TestCase):

        def setUp(self):
            pass

        def testCmd(self):
            self.assertEqual(cmd('uname -r'),0)
            self.assertEqual(cmd('uname', '-r'),0)
            self.assertEqual(cmd('uname -R'),1)
            self.assertEqual(cmd('uname', '-R'),1)

        def testCmd2(self):
            self.assertEqual(cmd2(['uname', '-r']),0)
            self.assertEqual(cmd2(['uname', '-R']),1)

        def testCheckCmd(self):
            self.assertEqual(check_cmd('uname -r'),0)
            self.assertEqual(check_cmd('uname', '-r'),0)
            with self.assertRaises(CmdError):
                check_cmd('uname -R')

        def testCheckCmd2(self):
            self.assertEqual(check_cmd2(['uname', '-r']),0)
            with self.assertRaises(CmdError):
                check_cmd2(['uname', '-R'])

        def testOutputCmd(self):
            self.assertIsInstance(output_cmd('uname -r'),str)
            self.assertIsInstance(output_cmd('uname', '-r'),str)
            with self.assertRaises(CmdError):
                output_cmd('uname -R')

        def testOutputCmd2(self):
            self.assertIsInstance(output_cmd2(['uname', '-r']),str)
            with self.assertRaises(CmdError):
                output_cmd2(['uname', '-R'])
       
        def cmdpPrep(self):
            if '__n__' in __builtin__.__dict__:
                del __builtin__.__dict__['__n__']
            self.cmdp_output = 0
            self.outputcmdp_output = 0
            self.checkcmdp_output = str

        def testCmdp(self):
            self.cmdpPrep()
            self.assertEqual(cmdp('uname -r'),self.cmdp_output)

        def testOutputCmdp(self):
            self.cmdpPrep()
            self.assertEqual(check_cmdp('uname -r'),self.outputcmdp_output)

        def testOutputCmdp(self):
            self.cmdpPrep()
            self.assertIsInstance(output_cmdp('uname -r'),self.checkcmdp_output)
        
        def cmdpPrep2(self):
            if '__n__' not in __builtin__.__dict__:
                __builtin__.__dict__['__n__'] = {}
            __n__['init'] = 'start'
            self.cmdp_output = None 
            self.outputcmdp_output = None 
            self.checkcmdp_output = None 
        
        def testCmdp2(self):
            self.cmdpPrep2()
            self.assertEqual(cmdp('uname -r'),self.cmdp_output)

        def testOutputCmdp2(self):
            self.cmdpPrep2()
            self.assertEqual(check_cmdp('uname -r'),self.outputcmdp_output)

        def testOutputCmdp2(self):
            self.cmdpPrep2()
            self.assertEqual(output_cmdp('uname -r'),self.checkcmdp_output)

        def tearDown(self):
            pass 

    unittest.main(verbosity=2)

