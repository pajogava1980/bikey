import multiprocessing as mp
import threading
import numpy as np
import datetime
import os
import argparse


def parse_cli_args(host = '127.0.0.1', port = 65432, directory = os.getcwd(),
                   max_connections = 10):
    """
    Parses server options from the command line with given defaults.

    Arguments:
    host -- The default host interface of the server.
    port -- The default port of the server.
    directory -- The default server directory.
    max_connections -- The default maximum number of simultaneous connections.
    """
    parser = argparse.ArgumentParser(
        description='Start a RL environment server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-H', '--host',
                        help = 'the host on which the server can be reached',
                        default = host)
    parser.add_argument('-p', '--port',
                        help = 'the port on which the server will listen',
                        default = port,
                        type = int)
    parser.add_argument('-d', '--directory',
                        help = 'the directory where the server will \
                                    store any files',
                        default = directory)
    parser.add_argument('-c', '--max_connections',
                        help = 'the maximum number of simultaneous connections',
                        default = max_connections,
                        type = int)

    args = parser.parse_args()

    return args.host, args.port, args.directory, args.max_connections


def display_connections(connections):
    """
    Prints all provided connections.

    Arguments:
    connections -- A list of (address, thread) tuples.
    """
    print('\n' + '-' * 40 + '\n')
    if len(connections) > 0:
        print("Current connections:")
        for i, (address, thread) in enumerate(connections):
            print(f"Connection {i} :: address {address}")
    else:
        print("Currently not connected to any clients")
    print('\n' + '-' * 40 + '\n')


def setup_name_queue(server_dir):
    """
    Creates a fixed size queue that will store possible working directories.

    Returns:
    A three-tuple containing
    - the thread that generates names of working directories
    - a threading.Event instance which allows you to stop the working directory
        generation thread
    - a multiprocessing.Queue instance from which processes can take a working
        directory for their environment, if needed
    """
    name_queue = mp.Queue(maxsize=5)
    stop_event = threading.Event()

    thread = threading.Thread(target=provide_names,
                              args=(server_dir, name_queue, stop_event))

    thread.start()

    return thread, stop_event, name_queue


def provide_names(base_dir, queue, stop_event):
    """
    Keeps adding names to the queue until stop_event is set.

    The names are formatted as follows:
    base_dir/hour.minute-day.month.year-0001, with the date and time
    representing the moment the server started running. This format allows for
    ten thousand directories per server active server, but this still means
    it is not a feasible option for running an environment server without
    stopping.

    The provided queue should have a maximum size, or the thread in which
    this function is called will keep adding subdirectories forever.

    Arguments:
    base_dir -- The directory where the working directories will be located
    queue -- A multiprocessing.Queue instance with a given maximum size
    stop_event -- The event that tells this function to stop producing names
    """
    time_string = datetime.datetime.today().strftime('%H.%M-%d.%m.%Y')
    base = os.path.join(base_dir, time_string + '-')
    counter = 1

    while not stop_event.is_set():
        # keep providing available directory names while thread is alive
        name = base + f'{counter:04}'
        queue.put(name)
        # print(f"Put {name} on the queue")
        counter += 1


def numpyify(message):
    """
    Transforms specified 'action' into a numpy array.

    At this point the numpy array is stored in its .tolist() form.

    Arguments:
    message -- The message stored in a python dictionary
    """
    if 'data' in message and 'action' in message['data']:
        message['data']['action'] = \
            np.array(message['data']['action'])


def denumpyify(message):
    """
    Transforms 'observation' numpy array into list form.

    Replaces the 'observation' with its array.tolist() form.

    Arguments:
    message -- The message stored in a python dictionary
    """
    if 'data' in message and 'observation' in message['data']:
        message['data']['observation'] = \
            message['data']['observation'].tolist()
