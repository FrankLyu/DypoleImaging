# coding=utf-8
# =============================================================================

import sys
import time
import threading

start = time.perf_counter()

def do_something(seconds):
    print(f"start {seconds} sleep")
    time.sleep(seconds)
    print("Done sleeping")

threads = []

for i in range(10):
    t = threading.Thread(target = do_something, args=[i])
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()
# t1 = threading.Thread(target = do_something) # No parentethis, not executed there
# t2 = threading.Thread(target = do_something)

# t1.start()
# t2.start()

# t1.join() # make sure it is done
# t2.join()

finish = time.perf_counter()

#t2.join()

print(f'Finished in {round(finish - start, 2)} seconds')

#x = threading.Thread(target=thread_function, args=(index,))