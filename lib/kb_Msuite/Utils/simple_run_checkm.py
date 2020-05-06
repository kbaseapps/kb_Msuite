"""
Run checkm's lineage_wf command.
"""
from subprocess import Popen, PIPE, STDOUT


def run_checkm(input_dir, output_dir, log_path, options={}):
    """
    Run the lineage_wf command and return the stdout.
    Arguments:
      input_dir - required - directory of the input bins
      output_dir - required - directory for the output
      log_path - required - file-path for the output log
      options - optional - dictionary of lineage_wf options
    """
    args = ['checkm', 'lineage_wf', input_dir, output_dir]
    for opt, val in list((options or {}).items()):
        args.append(opt)
        if val:
            args.append(str(val))
    print('Running: ' + ' '.join(args))
    proc = Popen(args, stdout=PIPE, stderr=STDOUT)
    with proc.stdout, open(log_path, 'w') as logfile:
        for line in iter(proc.stdout.readline, b''):
            logfile.write(line.decode("utf-8"))
