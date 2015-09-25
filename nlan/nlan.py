#!/usr/bin/env python

"""
2014/2/6, created  
2014/4/21, merged with nlan_master.py 
2014/5/28, MIME Multipart output

"""
import os, sys 
import paramiko as para
import scp
#from paramiko import AuthenticationException, SSHException
from optparse import OptionParser
from time import sleep
import traceback
from collections import OrderedDict
from multiprocessing import Process, Lock, Pipe, Queue
import time, datetime
from cStringIO import StringIO
import json
import email

import cmdutil, util, argsmodel
import yaml, yamldiff
from env import * 
from errors import NlanException

nlanconf = 'nlan_env.conf'

bar = '=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+'
bar2 = '----------------------------------------------------------------------------'

def _printmsg_request(lock, router, platform):
    with lock:
        rp = "NLAN Request to router:{0},platform:{1}".format(router, platform)
        print bar[:5], rp, bar[5+len(rp):] 


_toyaml = lambda d: yaml.dump(util.decode(d), default_flow_style=False).rstrip('\n') 


# NLAN MAIN FUNCTION
# Note: in case of RPC, set operation = '--rpc'
def main(router='_ALL',operation=None, doc=None, cmd_list=None, loglevel=None, git=False, verbose=False, mime=False, output_stdout=False, rest_output=False):

    rp = "Ping test to all the target routers"
    if verbose:
        print bar[:5], rp, bar[5+len(rp):] 
    (exit, results) = _wait(router, PING_CHECK_WAIT, verbose)
    if exit > 0:
        print ""
        print "Ping test failure! Transaction cancelled."
        raise NlanException("Ping test failure", result=results)

    start_datetime = str(datetime.datetime.now())
    start_utc = time.time()

    if doc and not operation or doc and operation == '--raw':
        doc = ' '.join(doc)
    if not loglevel:
        loglevel = ''
    

    def _ssh_exec_command(ssh, cmd, cmd_args, out):

        i,o,e = ssh.exec_command(cmd)

        o.channel.set_combine_stderr(True) # Combine STDERR 

        if cmd_args:
            i.write(cmd_args)
            i.flush()
            i.channel.shutdown_write()

        result = o.read()
        if result != '': 
            print >>out, result

        return o.channel.recv_exit_status()


    # ssh session per child process
    def _ssh_session(lock, queue, router, host, user, passwd, platform, operation, cmd, cmd_args, verbose, mime=False, output_stdout=False):

        out = StringIO()
        #err = StringIO()
        ssh = None
        
        stdout = None
        finish_utc = None
        response = OrderedDict() 
        response['exit'] = 0

        try:
            ssh = para.SSHClient()
            ssh.set_missing_host_key_policy(para.AutoAddPolicy())
            ssh.connect(host,username=user,password=passwd,timeout=SSH_TIMEOUT)


            if operation != '--scp' and operation != '--scpmod':
                exitcode = _ssh_exec_command(ssh, cmd, cmd_args, out)
            else:
                filelist = []
                if operation == '--scp':
                    s = scp.SCPClient(ssh.get_transport())
                    if verbose:
                        print >>out, "target_dir: " + NLAN_AGENT_DIR
                    for f in cmd: 
                        s.put(f, NLAN_AGENT_DIR)
                        filelist.append(f)
                elif operation == '--scpmod':
                    s = scp.SCPClient(ssh.get_transport())
                    if verbose:
                        print >>out, "target_dir: " + NLAN_AGENT_DIR
                    # scp NLAN modules
                    for moddir in NLAN_MOD_DIRS:
                        ldir = os.path.join(NLAN_SCP_DIR, moddir)
                        rdir = os.path.join(NLAN_AGENT_DIR, moddir)
                        exitcode = _ssh_exec_command(ssh, 'mkdir -p ' + rdir, None, out)
                        for f in os.listdir(ldir):
                            ff = os.path.join(ldir, f) 
                            s.put(ff, rdir)
                            filelist.append(f)
                    # scp NLAN-Agent scripts
                    for f in os.listdir(os.path.join(NLAN_SCP_DIR)):
                        lf = os.path.join(NLAN_SCP_DIR, f)
                        if os.path.isdir(lf):
                            pass
                        else:
                            s.put(lf, NLAN_AGENT_DIR)
                            filelist.append(f)
                    # scp NLAN libs
                    for f in NLAN_LIBS:
                        lf = os.path.join(NLAN_DIR, f)
                        s.put(lf, NLAN_AGENT_DIR)
                        filelist.append(f)
                    # scp NLAN Agent etc files
                    ldir = os.path.join(NLAN_DIR, 'agent/share')
                    rdir = os.path.join(NLAN_AGENT_DIR, 'share')
                    exitcode = _ssh_exec_command(ssh, 'mkdir -p ' + rdir, None, out)
                    for f in os.listdir(ldir):
                        ff = os.path.join(ldir, f) 
                        s.put(ff, rdir)
                        filelist.append(f)

                    # nlan_env.conf generation
                    rdir_nlanconf = os.path.join(NLAN_AGENT_DIR, nlanconf)
                    env = {} 
                    env['router'] = router
                    env['platform'] = platform
                    env['agent_dir'] = NLAN_AGENT_DIR
                    env['schema'] = SCHEMA
                    env['state_order'] = STATE_ORDER
                    env['tables'] = TABLES
                    env['indexes'] = INDEXES
                    env['types'] = TYPES 
                    env['share_dir'] = rdir
                    lf = os.path.join('/tmp', '{}.{}'.format(nlanconf,router)) 
                    with open(lf, 'w') as f:
                        f.seek(0)
                        f.truncate()
                        f.write(str(env))
                    s.put(lf, rdir_nlanconf)
                    filelist.append(nlanconf)
                
                if verbose:
                    print >>out, "files: " + str(filelist)
            
            with lock:
                outv = out.getvalue()
                outvl = len(outv)
                if verbose and (operation == '--scpmod' or operation == '--scp'):
                    rp = "Files copied to router:{0},platform:{1}".format(router, platform)
                    print bar[:5], rp, bar[5+len(rp):] 
                if outvl > 0:
                    print "*** Response from router:{0},platform:{1}".format(router, platform)
                    stdout = email.message_from_string(outv)
                    if mime:
                        print stdout 
                    else:
                        for part in stdout.walk():
                            content_type = part.get_content_type()
                            payload = part.get_payload()
                            content_description = part.get('Content-Description')
                            x_nlan_type = part.get('X-NLAN-Type')
                            if payload:
                                if x_nlan_type == 'logger':
                                    print content_description
                                if content_type == 'application/x-nlan':
                                    try:
                                        d = eval(payload)
                                        if isinstance(d, OrderedDict):
                                            if x_nlan_type == 'nlan_response':
                                                response = d
                                            if x_nlan_type == 'nlan_response' and d['exit'] > 0:
                                                for k, v in d.iteritems():
                                                    print '{}: {}'.format(k,v)
                                            elif verbose or x_nlan_type != 'nlan_response':
                                                print _toyaml(d)
                                            else:
                                                pass  # NLAN Response with exit == 0 and not verbose
                                        else:
                                            if x_nlan_type == 'nlan_response':
                                                raise Exception('Illegal NLAN Response received, {}'.format(str(payload)))
                                            else:
                                                print payload
                                    except:
                                        print payload
                                elif content_type == 'application/json':
                                    d = json.loads(payload, object_hook=util.decode_dict)
                                    print _toyaml(d)
                                elif content_type == 'text/plain':
                                    print payload

        except Exception as e:
            response['exception'] = type(e).__name__
            response['message'] = 'See the traceback message'
            response['exit'] = 1 
            response['traceeback'] = traceback.format_exc()
            with lock:
                rp = "NLAN Request Failure router:{0},platform:{1}".format(router, platform)
                print bar[:5], rp, bar[5+len(rp):] 
                print ('__ Exception __')
                for key in response.keys():
                    print '{}: {}'.format(key, response[key])

        finally:
            finish_utc = time.time()
            result = {}
            if output_stdout:
                result['stdout'] = None
                if stdout:
                    for part in stdout.walk():
                        x_nlan_type = part.get('X-NLAN-Type')
                        if x_nlan_type in ('crud_response', 'rpc_response'):
                            payload = part.get_payload()
                            content_type = part.get_content_type()
                            if payload:
                                if content_type == 'application/x-nlan':
                                    try:
                                        payload = eval(payload)
                                    except:
                                        pass
                                result['stdout'] = payload
                            break
            result['router'] = router
            result['response'] = response
            result['finish_utc'] = finish_utc
            queue.put(result)

            out.close()
            ssh.close()


    routers = []

    ssh_sessions = [] 
    lock = Lock()
    queue = Queue()

    if router == '_ALL':	
        routers = ROSTER.keys()
    else:
        routers.append(router)

    if operation == '--batch':
        for l in cmd_list:

            router = l[0]
            operation = l[1]
            doc = l[2]

            host = ROSTER[router]['host']
            user = ROSTER[router]['user']
            passwd = ROSTER[router]['passwd']	
            platform = ROSTER[router]['platform']

            cmd = NLAN_AGENT + ' ' + operation + ' --envfile ' + os.path.join(NLAN_AGENT_DIR, nlanconf) + ' ' + loglevel
            cmd_args = doc
            cmd_args = '"' + cmd_args + '"'
            if verbose:
                _printmsg_request(lock, router, platform)
                print 'operation: ' + operation 
                print 'dict_args: ' + cmd_args

            ssh_sessions.append(Process(target=_ssh_session, args=(lock, queue, router, host, user, passwd, platform, operation, cmd, cmd_args, verbose, mime, output_stdout)))

    else:
        for router in routers:
            host = ROSTER[router]['host']
            user = ROSTER[router]['user']
            passwd = ROSTER[router]['passwd']	
            platform = ROSTER[router]['platform']
            cmd = ''
            cmd_args = ''
            if operation == '--raw':
                assert(isinstance(doc,str))
                cmd = doc
                if verbose:
                    _printmsg_request(lock, router, platform)
                    print 'operation: ' + operation 
                    print 'command: ' + cmd	
            elif operation == '--scpmod':
                if verbose:
                    _printmsg_request(lock, router, platform)
                    print 'operation: ' + operation 
            elif operation == '--scp':
                assert(isinstance(doc,list))
                cmd = doc
                for f in doc:
                    fp = os.path.join(NLAN_DIR, f)
                    if os.path.isdir(fp):
                        cmd.remove(f)
                if verbose:
                    _printmsg_request(lock, router, platform)
                    print 'operation: ' + operation 
                    print 'files: ' + str(cmd)	
            elif operation == None:
                cmd = NLAN_AGENT + ' ' + doc + ' --envfile ' + os.path.join(NLAN_AGENT_DIR, nlanconf) + ' ' + loglevel
                if verbose:
                    _printmsg_request(lock, router, platform)
                    print 'command: ' + doc 
            else:
                cmd = NLAN_AGENT + ' ' + operation + ' --envfile ' + os.path.join(NLAN_AGENT_DIR, nlanconf) + ' ' + loglevel
                cmd_args = doc
                cmd_args = '"' + cmd_args + '"'
                if verbose:
                    _printmsg_request(lock, router, platform)
                    print 'operation: ' + operation 
                    print 'dict_args: ' + cmd_args

            ssh_sessions.append(Process(target=_ssh_session, args=(lock, queue, router, host, user, passwd, platform, operation, cmd, cmd_args, verbose, mime, output_stdout)))
 
    # Start child processes
    try:
        for l in ssh_sessions:
            l.start()

        while True:
            if len(ssh_sessions) == 0:
                break
            sleep(0.05)
            temp = list(ssh_sessions)
            for l in temp:
                if not l.is_alive():
                    l.terminate()
                    ssh_sessions.remove(l)
    except KeyboardInterrupt:
        print "\nOK. I will terminate the child processes..."
        for l in ssh_sessions:
            pid = str(l[0].pid)
            sub = cmdutil.output_cmd('ps -p', pid, 'h')
            l.terminate()
            l.join()
            print "child process:", sub 
        raise Exception("Operation stopped by Keyboard Interruption") 
    finally:
        exit = 0
        results = [] 
        if not queue.empty():
            if verbose:
                title = "Transaction Summary"
                print bar[:5], title, bar[5+len(title):] 
                print ""
                print "Start Time: {}".format(start_datetime)
                print ""
                print "Router           Result    Elapsed Time"
                print "---------------------------------------"
            for l in ssh_sessions:
                l.terminate()
            while not queue.empty():
                smiley = ':-)'
                result = queue.get() 
                router = result['router']
                response = result['response']
                if response['exit'] > 0:
                    smiley = 'XXX'
                    exit = 1
                if verbose:
                    print "{:17s} {:3s}   {:10.2f}(sec)".format(router, smiley, result['finish_utc'] - start_utc)
                results.append(result)
        if exit > 0:
            raise NlanException("NLAN transaction failure", result=results)
        else:
            return results # A bunch of results from child processes
            

def _wait(router, timeout, verbose):

    import subprocess, time

    # child process
    def _ping(router, host, timeout, devnull, queue):

        start = time.time()
        okcheck = True
        if timeout < 0:
            timeout = abs(timeout)
            okcheck = False 
        while True:
            command = 'ping -c 1 -W 1 ' + host
            command = command.split()
            exitcode = subprocess.call(command, stdout=devnull)
            if okcheck and exitcode == 0 or not okcheck and exitcode > 0:
                queue.put((router, host, True))
                break
            if time.time() - start > timeout:
                queue.put((router, host, False))
                break

    hosts = {} 
    exit = 0

    if router == '_ALL':
        for router in ROSTER.keys():
            hosts[router] = ROSTER[router]['host']
    else:
        hosts[router] = ROSTER[router]['host']
     
    if verbose:
        print "Router           Host           Ping"
        print "------------------------------------"
    children = []
    results = [] 
    try:
        with open(os.devnull, 'w') as devnull:
            queue = Queue()
            for router, host in hosts.iteritems():
                child = Process(target=_ping, args=(router, host, timeout, devnull, queue))
                child.start()
                children.append(child)

            while True:
                if len(children) == 0:
                    break
                sleep(0.5)
                temp = list(children)
                for l in temp:
                    if not l.is_alive():
                        l.terminate()
                        children.remove(l)
                while not queue.empty():
                    q = queue.get()
                    router = q[0]
                    host = q[1]
                    result = q[2]
                    if timeout > 0 and result or timeout < 0 and not result:
                        if verbose:
                            print '{:17s}{:15s}OK'.format(router, host)
                    elif timeout > 0 and not result or timeout < 0 and result:
                        if verbose:
                            print '{:17s}{:15s}NG'.format(router, host)
                    if result:
                        results.append({'message': 'Ping test OK', 'router':router, 'host':host, 'exit': 0})
                    else:
                        results.append({'message': 'Ping test failure', 'router':router, 'host':host, 'exit': 1})
                    if not result and exit == 0:
                        exit = 1
    except KeyboardInterrupt:
        print "\nOK. I will terminate the subprocesses..."
        for l in children:
            pid = str(l.pid)
            sub = cmdutil.output_cmd('ps -p', pid, 'h')
            l.terminate()
            l.join()
            print "child process:", sub 
    finally:
        return (exit, results)


if __name__=='__main__':

    logo = """
       _  ____   ___   _  __  
      / |/ / /  / _ | / |/ /  
     /    / /__/ __ |/    /   
    /_/|_/____/_/ |_/_/|_/ MASTER 

    """

    usage = logo + "usage: %prog [options] [arg]..."
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--target", help="target router", action="store", type="string", dest="target")
    parser.add_option("-c", "--scp", help="copy scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy NLAN Agent and NLAN modules to remote routers", action="store_true", default=False)
    parser.add_option("-a", "--add", help="(CRUD) add NLAN states", action="store_true", default=False)
    parser.add_option("-g", "--get", help="(CRUD) get NLAN states", action="store_true", default=False)
    parser.add_option("-u", "--update", help="(CRUD) update NLAN states", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="(CRUD) delete NLAN states", action="store_true", default=False)
    parser.add_option("-s", "--schema", help="(CRUD) print schema", action="store_true", default=False) 
    parser.add_option("-r", "--raw", help="run a raw shell command on remote routers", action="store_true", default=False)
    parser.add_option("-w", "--wait", help="wait until all the routers become accessible (a value < 0 is for NG check, --target also applies)", action="store", type="int", dest="time")
    parser.add_option("-I", "--info", help="set log level to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set log level to DEBUG", action="store_true", default=False)
    parser.add_option("-G", "--git", help="use local Git repo", action="store_true", default=False)
    parser.add_option("-R", "--rollback", help="rollback to the last Git commit", action="store_true", default=False)
    parser.add_option("-M", "--mime", help="MIME Mulitpart output", action="store_true", default=False)
    parser.add_option("-v", "--verbose", help="verbose output", action="store_true", default=False)

    (options, args) = parser.parse_args()

    option = None
    git = -1 
    target = None
    verbose = False
    mime = False
    crud = False

    if options.add:
        option = '--add'
        crud = True
    elif options.get:
        option = '--get'
        crud = True
    elif options.update:
        option = '--update'
        crud = True
    elif options.delete:
        option = '--delete'
        crud = True
    elif options.scp:
        option = '--scp'
    elif options.scpmod:
        option = '--scpmod'
    elif options.raw:
        option = '--raw'
    elif options.git:
        git = 0 
    elif options.rollback:
        git = 1

    loglevel = None
    if options.info:
        loglevel = '--info'
    elif options.debug:
        loglevel = '--debug'

    if options.verbose:
        verbose = True

    if options.mime:
        mime = True

    router = '_ALL'
    if options.target:
        router = options.target

    # Default state file
    if not crud and not option and len(args) == 1 and args[0] == 'deploy':
        args[0] = NLAN_STATE

    try: # Execution
        if options.time: # --wait
            timeout = options.time
            _wait(router, timeout, verbose)
        elif not crud and option: # --scp, --scpmod, --raw
            main(router=router, operation=option, doc=args, loglevel=loglevel, git=git, verbose=verbose, mime=mime)
        elif options.schema:
            if len(args) == 1:
                print argsmodel.schema_help(args[0])
            else:
                print argsmodel.schema_help(None)
        elif not crud and not option and len(args) > 0 and args[0].endswith('yaml'): # Batch operation
            for v in args:
                if v.endswith('yaml'):
                    if os.path.exists(os.path.join(NLAN_ETC, v)):
                        cmd_list = yamldiff.crud_diff(v, git=git)
                        if len(cmd_list) != 0:
                            main(router=router, operation='--batch', cmd_list=cmd_list, loglevel=loglevel, verbose=verbose, mime=mime)
                            if git == 0:
                                cmdutil.check_cmd('git', GIT_OPTIONS, 'add', v)
                                cmdutil.check_cmd('git', GIT_OPTIONS, 'commit -m updated')
        elif not crud and not option and len(args) > 0: # NLAN rpc module execution
            main(router=router, doc=args, loglevel=loglevel, verbose=verbose, mime=mime)
        elif crud and len(args) > 0: # CRUD operation
            operation = option.lstrip('-') 
            doc = str(argsmodel.parse_args(operation, args[0], *args[1:]))
            main(router=router, operation=option, doc=doc, loglevel=loglevel, verbose=verbose, mime=mime)
        else:
            parser.print_usage()
    except NlanException as e:
        sys.exit(1)
    except:
            traceback.print_exc()
            sys.exit(1)

