#!/usr/bin/python3

import os
import signal
import subprocess
import sys
import time

try:
   TIMEOUT_NO_ACTIVITY_SECONDS = int(os.getenv('TIMEOUT_NO_ACTIVITY_SECONDS', 60))
except:
   TIMEOUT_NO_ACTIVITY_SECONDS = 60
   
class MinerException(Exception):
    pass

class TimeoutException(Exception):
    pass
    
def timeout_handler(signum, frame):
    raise TimeoutException("No activity from ethminer for {} seconds".format(TIMEOUT_NO_ACTIVITY_SECONDS))

def execute(cmd):
    signal.signal(signal.SIGALRM, timeout_handler)

    shutdown = False
    last_job_time=time.time()
    while not shutdown:
        proc = subprocess.Popen(cmd,
                                bufsize=0,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True)

        try:
            signal.alarm(TIMEOUT_NO_ACTIVITY_SECONDS)
            for line in iter(proc.stdout.readline, ""):
                line = line.strip()
                job_time_delta=time.time()-last_job_time
                print(line)
                #print("Last job was %f ms ago" % job_time_delta)
                if job_time_delta>120:
                    last_job_time=time.time()
                    raise MinerException('****** Restarting due to not getting new jobs')
                if (line.find('Received new job'))>=0:
                    print("Time since last job: %f ms" % job_time_delta)
                    last_job_time=time.time()
                if line.startswith('Could not resolve host'):
                    raise MinerException('****** Restarting due to DNS error')
                if line.startswith('CUDA error'):
                    raise MinerException('****** Restarting due to CUDA error')
                signal.alarm(TIMEOUT_NO_ACTIVITY_SECONDS)
        except (MinerException, TimeoutException) as e:
            print('\n\n', str(e), '\n\n')
        except KeyboardInterrupt:
            shutdown = True

        signal.alarm(0)

        proc.send_signal(signal.SIGINT)
        proc.stdout.close()

        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            print("ping didn't shutdown within 15 seconds")
            proc.kill()


if __name__ == "__main__":
    execute(sys.argv[1:])
