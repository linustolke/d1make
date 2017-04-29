# d1make
A simple make-based first level makefile distributed compilation.

This requires:
* 

# How it works

Processes ur run like this:

```
d1make.py 
    +-----------------ssh-------------------- d1make-server.py
    \                                              .    \
      make                                       /        make
        \                                      .            \
         d1make-client.py                    /                compile
            |                              .
            \----------ssh------d1make-client.py --remote
```

An explained sequence of events
1. `d1make.py` - Opens up sessions, configure PATH and other tool settings and starts `d1make-server.py`.
1. This can be repeated several times, once for each host to use.
1. When `d1make-server.py` processes starts, it opens a FIFO to receive requests and reports that FIFO back together with load information.
1. `d1make.py` reads the `makefile` and replaces locations where make is called with calls to `d1make-client.py`.
1. `d1make.py` starts `make` on the modified `makefile`.
1. When `d1make-client.py` is started by `make`, it contacts `d1make.py` using a FIFO and gets information on what host to contact and the location of the `d1make-server.py` FIFO on that host.
1. `d1make-client.py` starts an ssh session to that host, running `d1make-client.py --remote` on the remote side.
1. `d1make-client.py --remote` orders `d1make-server.py` to start the `make` command and deliver stderr, stdout and exit code using FIFOs.
1. The `make` executes and terminates. The termination is reported back to `d1make-client.py --remote` by `d1make-server.py` closing the FIFOs.
1. The `d1make-client.py --remote` exits with the exit code from make in turn causing the ssh to exit and `d1make-client.py` exits as a consequence.
1. The `make` can then continue with the next line in the recipe or the next possible goal as the job is finished.

## This requires:
* That you have a fairly large project to compile (using `make`)
* That you have a set of hosts available to use for compilation. The hosts are approximately the same in processing capacity, memory, disc access speed etc.
* That the hosts available to build on all have the same user ids, file systems, and tools (including the d1make-tool) installed.
* That you can contact the hosts using ssh.
* That the compile rules of the project is structured in one `makefile` on the top dispatching to many `makefile`s just one level down.
* That most of the compilation is done one level down without very much arbitration and rules in the top `makefile`.

## How it is intended to be used:
1. You set up the list of hosts to contact in the environment variable `D1MAKE_HOSTS`.  
   Make sure that you can connect to all of them using ssh without password.
1. You set up the configuration of tools used in the variable `D1MAKE_SERVER_SETUP`. The contents of this variable will be inserted just before starting `d1make-server.py` so if it is a command (as opposed to just a line of environment variable settings), end with semicolon (;).
1. You set up the environment variable `D1MAKE_CLIENT_MAKEARGS` with parameters passed to `make` on the client side (typically -j and/or -l) to control how many simultaneous compilations one of the makes shall run. You could probably find the optimal values for this by running a sequence of test compilations with different values on one of these hosts to find out what settings are best.
1. You start `d1make.py` with a goal and the -j (--jobs) flag specifying the amount of `d1make-clientl.py` jobs you will run. If each of the hosts specified in `D1MAKE_HOSTS` are two-CPU hosts, you should probably choose the amount of jobs between 2 * #hosts and 4 * #hosts.

## Some notes on the consequences of the implementaton
* The distribution of jobs will be at random taking into account the last reported load on the each of the hosts and the amount of recently dispatched job to each of them. This means that if some other user runs a job on one of the hosts, this host will be less likely to be used until the other user's jobs is complete and the load starts to drop.
* The output from the compilations is buffered somewhere in the chain `d1make-client.py` - ssh - `d1make-client.py --remote` - `d1make-server.py` - `make` so there is a risk that the outputs from all make commands are mixed or only arrives when the make terminates. The mixing of the output should not come as a surprise if you are used to compile with the -j flag (without the -Orecurse flag).
* The ssh connection between `d1make-client.py` and `d1make-client.py --remote` uses the same ssh connection as the one between `d1make.py` and `d1make-server.py` using the ssh ctl_path mechanism. If you don't use an ssh compatible with openssh in this respect, it will not work.
  
  