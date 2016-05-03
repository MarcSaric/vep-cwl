import sys
import subprocess
import logging
import os
import shutil
import hashlib
import gzip

def run_command(cmd, logger=None, shell_var=False):
    '''
    Runs a subprocess
    '''
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode

    if logger is not None:
        logger.info(cmd)
        stdoutdata = stdoutdata.split("\n")
        for line in stdoutdata:
            logger.info(line)

        stderrdata = stderrdata.split("\n")
        for line in stderrdata:
            logger.info(line)

    return exit_code

def setup_logging(level, log_name, log_filename):
    '''
    Sets up a logger
    '''
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    if log_filename is None:
        sh = logging.StreamHandler()
    else:
        sh = logging.FileHandler(log_filename, mode='w')

    sh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(sh)
    return logger

def targz_decompress(logger, filename, cmd_prefix=['tar', '-xzf']):
    '''
    Runs tar -xzf
    '''
    cmd = cmd_prefix + [filename]
    print cmd
    exit_code = run_command(cmd, logger=logger)

    return exit_code

def remove_dir(dirname):
    """ Remove a directory and all it's contents """

    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    else:
        raise Exception("Invalid directory: %s" % dirname)

def get_file_size(filename):
    ''' Gets file size '''
    fstats = os.stat(filename)
    return fstats.st_size

def get_md5(input_file):
    '''Estimates md5 of file '''
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(input_file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def has_variants_check(filename):
    ''' Checks if there are any variants '''
    reader = gzip.open(filename, 'rt') if filename.endswith('.gz') else open(filename, 'r')
    counts = 0
    for line in reader:
        if line.startswith('#'): continue
        elif counts > 0: break
        else: counts += 1

    reader.close()
    return counts > 0
