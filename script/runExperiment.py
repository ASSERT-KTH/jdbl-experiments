#!/usr/bin/env python3

import os
import json
import subprocess
from queue import Queue
from threading import Thread
import time
import signal
import sys

token = None
if 'GITHUB_OAUTH' in os.environ and len(os.environ['GITHUB_OAUTH']) > 0:
    token = os.environ['GITHUB_OAUTH']

PATH_file = os.path.join(os.path.dirname(__file__), '..', 'dependants', 'single_module_java_projects_with_5_stars.json')
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))

timeout = 60 * 60 # 1h

class Task():
    def __init__(self, library, client, version):
        self.library = library
        self.client = client
        self.version = version
        self.status = ""

    def run(self):
        lib_name = os.path.basename(self.library['repo_name'])
        client_name = os.path.basename(self.client['repo_name'])
        print("Run %s %s" % (self.library['repo_name'], self.client['repo_name']))
        cmd = 'docker run -e GITHUB_OAUTH="%s" -v %s:/results -it --rm jdbl -d https://github.com/%s.git -c https://github.com/%s.git -v %s' % (token, OUTPUT, self.library['repo_name'], self.client['repo_name'], self.version)
        with open(os.path.join(OUTPUT, 'executions', '%s_%s.log' % (lib_name, client_name)), 'w') as fd:
            try:
                p = subprocess.call(cmd, shell=True, stderr=fd, stdout=fd, universal_newlines=True, timeout=timeout)
            except KeyboardInterrupt:
                p.send_signal(signal.SIGINT)
            except Exception as e:
                print(e)
                pass

class RunnerWorker(Thread):
    def __init__(self, tasks, callback):
        Thread.__init__(self)
        self.callback = callback
        self.daemon = True
        self.tasks = tasks
        self.pool = ThreadPool(12)

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
                print(e)
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
        if "commons" not in id:
            continue
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

def taskDoneCallback(task):
    pass

worker = RunnerWorker(tasks, taskDoneCallback)
worker.start()
while worker.is_alive():
    time.sleep(1)