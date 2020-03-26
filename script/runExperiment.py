#!/usr/bin/env python3

import os
import json
import subprocess
from queue import Queue
from threading import Thread
import time
from datetime import timedelta
import signal
import sys
import random
import argparse

token = None
if 'GITHUB_OAUTH' in os.environ and len(os.environ['GITHUB_OAUTH']) > 0:
    token = os.environ['GITHUB_OAUTH']

parser = argparse.ArgumentParser()
parser.add_argument('--all', dest='all', action='store_true', help="Run the experiment on all the libs and clients")
args = parser.parse_args()

PATH_file = os.path.join(os.path.dirname(__file__), 'considered_cases.json')
if args.all:
    PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dependants', 'single_module_java_projects_with_5_stars.json')

OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))

timeout = 60 * 60 # 1h

def get_terminal_size():
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    ### Use get(key[, default]) instead of a try/catch
    # try:
    #    cr = (env['LINES'], env['COLUMNS'])
    # except:
    #    cr = (25, 80)
    return int(cr[1]), int(cr[0]) - 1


def clean_terminal():
    (width, height) = get_terminal_size()

    for i in range(1, height + 1):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
start = time.time()
def render():
    (width, height) = get_terminal_size()
    clean_terminal()
    now = time.time()
    if len(finished) > 0:
        average_time_per_run = (now-start)/len(finished)
    else:
        average_time_per_run = 0
    reming_time = timedelta(seconds=int((len(tasks) - len(finished)) * average_time_per_run))
    output = "%d/%d Finished in %s still %s to go\n" % (len(finished), len(tasks), timedelta(seconds=int(now-start)), reming_time)

    output += "Running: \n"
    line_number = 1
    now = time.time()
    for t in running:
        if t.start is not None:
            diff = now - t.start
        else:
            diff = 0
        dt = timedelta(seconds=int(diff))
        output += "\t %d. %s (%s) with %s in %s\n" % (line_number, t.library['repo_name'], t.version, t.client['repo_name'], dt)
        line_number += 1
    print(output)

class Task():
    def __init__(self, library, client, version):
        self.library = library
        self.client = client
        self.version = version
        self.status = ""
        self.start = None

    def run(self):
        self.start = time.time()
        lib_name = os.path.basename(self.library['repo_name'])
        client_name = os.path.basename(self.client['repo_name'])
        # print("Run %s %s" % (self.library['repo_name'], self.client['repo_name']))
        log_file = os.path.join(OUTPUT, 'executions', '%s_%s.log' % (self.library['repo_name'], self.client['repo_name']))
        cmd = 'docker run -e GITHUB_OAUTH="%s" -v %s:/results --rm jdbl -d https://github.com/%s.git -c https://github.com/%s.git -v %s' % (token, OUTPUT, self.library['repo_name'], self.client['repo_name'], self.version)
        with open(log_file) as fd:
            try:
                p = subprocess.call(cmd, shell=True, timeout=timeout, stdout=fd, stderr=fd)
                pass
            except KeyboardInterrupt:
                self.status = "Kill"
                # p.send_signal(signal.SIGINT)
            except Exception as e:
                self.status = str(e)

class RunnerWorker(Thread):
    def __init__(self, tasks, callback):
        Thread.__init__(self)
        self.callback = callback
        self.daemon = True
        self.tasks = tasks
        self.pool = ThreadPool(6)

    def run(self):
        for task in self.tasks:
            task.status = "WAITING"
            self.pool.add_task(task, self.callback)

        self.pool.wait_completion()


class Worker(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            (task, callback) = self.tasks.get()
            running.append(task)
            task.status = "STARTED"
            try:
                task.run()
            except Exception as e:
                task.status = "ERROR"
            finally:
                if callback is not None:
                    callback(task)
                self.tasks.task_done()


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        self.workers = []
        for _ in range(num_threads):
            self.workers.append(Worker(self.tasks))

    def add_task(self, task, callback):
        """Add a task to the queue"""
        if task.client is not None and task.library is not None:
            self.tasks.put((task, callback))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()



tasks = []
with open(PATH_file) as fd:
    libraries = json.load(fd)
    for id in libraries:
        lib = libraries[id]
        lib_name = os.path.basename(lib['repo_name'])
        versions = lib['clients']
        for version in versions:
            clients = versions[version]
            for client in clients:
                client_name = os.path.basename(client['repo_name'])
                if 'groupId' not in lib or 'groupId' not in client:
                    continue
                path_client_debloat = os.path.join('results', lib['groupId'] + ':' + lib['artifactId'], version, 'clients', client['groupId'] + ':' + client['artifactId'], 'debloat', 'test-results')
                if not os.path.exists(path_client_debloat):
                    tasks.append(Task(lib, client, version))


finished = []
running = []

def taskDoneCallback(task):
    finished.append(task)
    running.remove(task)
    pass

random.shuffle(tasks)
worker = RunnerWorker(tasks, taskDoneCallback)
worker.start()
while worker.is_alive():
    render()
    time.sleep(1)