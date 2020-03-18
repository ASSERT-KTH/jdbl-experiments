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


token = None
if 'GITHUB_OAUTH' in os.environ and len(os.environ['GITHUB_OAUTH']) > 0:
    token = os.environ['GITHUB_OAUTH']

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
    output = "%d/%d Finished in %s still %s to go" % (len(finished), len(tasks), timedelta(seconds=int(now-start)), reming_time)
    print(output)

class Task():
    def __init__(self, library, client, version):
        self.library = library
        self.client = client
        self.version = version
        self.status = ""

    def run(self):
        lib_name = os.path.basename(self.library['repo_name'])
        client_name = os.path.basename(self.client['repo_name'])
        # print("Run %s %s" % (self.library['repo_name'], self.client['repo_name']))
        log_file = os.path.join(OUTPUT, 'executions', '%s_%s.log' % (lib_name, client_name))
        cmd = 'docker run -e GITHUB_OAUTH="%s" -v %s:/results --rm jdbl -d https://github.com/%s.git -c https://github.com/%s.git -v %s > %s 2>&1' % (token, OUTPUT, self.library['repo_name'], self.client['repo_name'], self.version, log_file)
        try:
            p = subprocess.call(cmd, shell=True, timeout=timeout)
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
        self.pool = ThreadPool(8)

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
            if len(clients) < 4:
                continue
            for client in clients:
                client_name = os.path.basename(client['repo_name'])
                tasks.append(Task(lib, client, version))


finished = []
running = []

def taskDoneCallback(task):
    finished.append(task)
    pass

random.shuffle(tasks)
worker = RunnerWorker(tasks, taskDoneCallback)
worker.start()
while worker.is_alive():
    render()
    time.sleep(1)