import os
import time
import subprocess

from sniffer.api import select_runnable, file_validator, runnable
try:
    from pync import Notifier
except ImportError:
    notify = None
else:
    notify = Notifier.notify


watch_paths = ['gdm/', 'tests/']
show_coverage = True


@select_runnable('python_tests')
@file_validator
def py_files(filename):
    return all((filename.endswith('.py'),
               not os.path.basename(filename).startswith('.')))


@runnable
def python_tests(*args):

    group = int(time.time())  # unique per run

    for count, (command, title) in enumerate((
        (('make', 'check'), "Static Analysis"),
        (('make', 'test-unit'), "Unit Tests"),
        (('make', 'test-all'), "Integration Tests"),
        (('make', 'doc'), None),
    ), start=1):

        print("")
        print("$ %s" % ' '.join(command))
        failure = subprocess.call(command)

        if failure:
            if notify and title:
                mark = "❌" * count
                notify(mark + " [FAIL] " + mark, title=title, group=group)
            return False
        else:
            if notify and title:
                mark = "✅" * count
                notify(mark + " [PASS] " + mark, title=title, group=group)

    global show_coverage
    if show_coverage:
        subprocess.call(['make', 'read-coverage'])
    show_coverage = False

    return True