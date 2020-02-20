import time
import platform
import psutil
import subprocess
from pathlib import Path

PLATFORM = platform.system()


class Systems:

    def __init__(self, hostname, username, is_local, thread_count, tmp_dir, ssh_port):
        self.hostname = hostname
        self.username = username
        self.is_local = is_local
        self.thread_count = thread_count
        self.tmp_dir = tmp_dir
        self.ssh_port = ssh_port
        self.current_thread_count = 0
        self.processes = []
        self.returncodes = []
        self.g4_task_id = []
        self.stdout_stderr_file = ""

    def run_process(self, g4_macro_object, stdout_stderr_buf, work_dir):
        if self.is_local == "True":
            print("Running Testme Locally")
            process = psutil.Popen(['./local_system_execution.sh', self.username, self.hostname, str(self.ssh_port), self.tmp_dir, g4_macro_object.header, work_dir],
                                   stdout=stdout_stderr_buf, stderr=subprocess.STDOUT)
        else:
            process = psutil.Popen(['./remote_system_execution.sh', self.username, self.hostname, str(self.ssh_port), self.tmp_dir, g4_macro_object.header, work_dir],
                                   stdout=stdout_stderr_buf, stderr=subprocess.STDOUT)
        self.current_thread_count = self.current_thread_count + 1
        try:
            process.nice(2)  # Jon : I want to set all the processes evenly so they don't compete against core OS functionality (ssh, cron etc..) slowing things down.
            if PLATFORM != "Darwin":  # Jon : cpu_affinity doesn't exist for the mac, testing on a mac... yup... good story.
                process.cpu_affinity(range(psutil.cpu_count()))
        except:
            print("That didn't go well...")
        self.processes.append(process)
        return process


def write_macro_file(g4_macro_object, work_dir):
    #  Write the individual macro files to ./tmp so that we can transfer them to a different System
    #  or location.  yes I'm just being lazy by doing it this way but whatever..
    # Path(work_dir).mkdir(parents=True, exist_ok=True)   # make a ./tmp dir if one doesn't exist to store the macro files
    g4_macro_filename = work_dir + '/' + g4_macro_object.header + '.mac'
    with open(g4_macro_filename, 'w') as macro_file:
        macro_file.write(g4_macro_object.macro_block)  # Write the macro info to the file


def pop_event_run(active_processes, my_system, g4_macro_object_list, stdout_stderr_buf, work_dir):
    try:
        my_g4_object = g4_macro_object_list.pop(0)  # Pop an item off the queue to run
    except:
        print("The macro QUEUE is empty!")
        return active_processes, 0
    write_macro_file(my_g4_object, work_dir)

    try:
        my_system.run_process(my_g4_object, stdout_stderr_buf, work_dir)  # Actually run the process
    except:
        print("Could not run : %s on %s" % (my_g4_object, my_system.hostname))

    active_processes = active_processes + 1
    print("Starting: %s on %s" % (my_g4_object.header, my_system.hostname))
    return active_processes, my_g4_object


def process_event_loop(systems_class_list, g4_macro_object_list, work_dir):
    Path(work_dir).mkdir(parents=True, exist_ok=True)   # make a ./tmp dir if one doesn't exist to store the macro files
    stdout_stderr_file = work_dir + "/logfile.stdout_stderr"
    # remove_file_if_exists(stdout_stderr_file)
    stdout_stderr_buf = open(stdout_stderr_file, "w")
    active_processes = 0
    for my_system in systems_class_list:
        for i in range(my_system.thread_count):  # Launch initial batch of processes
            active_processes, my_g4_object = pop_event_run(active_processes, my_system, g4_macro_object_list, stdout_stderr_buf, work_dir)

    while active_processes != 0:  # monitor running processes and add more as process queue drains, should figure out a bettery conditional later..
        time.sleep(1)
        for my_system in systems_class_list[:]:
            for running_proc in my_system.processes[:]:
                time.sleep(1)
                if running_proc.poll() is not None:
                    my_system.current_thread_count = my_system.current_thread_count - 1
                    my_system.processes.remove(running_proc)
                    active_processes = active_processes - 1
                    print("%s - Process finished, Return code :  %s, current thread count : %i" % (my_system.hostname, running_proc.poll(), my_system.current_thread_count))
                    active_processes, my_g4_object = pop_event_run(active_processes, my_system, g4_macro_object_list, stdout_stderr_buf, work_dir)
    print("All macros completed.")
