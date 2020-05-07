# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import json
from kb_Msuite.Utils.CheckMUtil import CheckMUtil
from kb_Msuite.Utils.simple_run_checkm import run_checkm
#END_HEADER


class kb_Msuite:
    '''
    Module Name:
    kb_Msuite

    Module Description:
    A KBase module: kb_Msuite
This SDK module is developed to wrap the open source package CheckM which consists of a set of tools
for assessing the quality of genomes recovered from isolates, single cells, or metagenomes.
CheckM consists of a series of commands in order to support a number of different analyses and workflows.

References:
CheckM in github: http://ecogenomics.github.io/CheckM/
CheckM docs: https://github.com/Ecogenomics/CheckM/wiki

Parks DH, Imelfort M, Skennerton CT, Hugenholtz P, Tyson GW. 2015. CheckM: assessing the quality of microbial genomes recovered from isolates, single cells, and metagenomes. Genome Research, 25: 1043–1055.
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "1.4.0"
    GIT_URL = "https://github.com/kbaseapps/kb_Msuite"
    GIT_COMMIT_HASH = "d0b7da86da423aa43bb33139d35cff996de19e4f"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.config['SDK_CALLBACK_URL'] = os.environ['SDK_CALLBACK_URL']
        self.config['KB_AUTH_TOKEN'] = os.environ['KB_AUTH_TOKEN']
        #END_CONSTRUCTOR
        pass


    def run_checkM(self, ctx, params):
        """
        :param params: instance of type "CheckMInputParams" (Runs CheckM as a
           command line local function. subcommand - specify the subcommand
           to run; supported options are lineage_wf, tetra, bin_qa_plot,
           dist_plot bin_folder - folder with fasta files representing each
           contig (must end in .fna) out_folder - folder to store output
           plots_folder - folder to save plots to seq_file - the full
           concatenated FASTA file (must end in .fna) of all contigs in your
           bins, used just for running the tetra command tetra_File - specify
           the output/input tetra nucleotide frequency file (generated with
           the tetra command) dist_value - when running dist_plot, set this
           to a value between 0 and 100 threads -  number of threads
           reduced_tree - if set to 1, run checkM with the reduced_tree flag,
           which will keep memory limited to less than 16gb (otherwise needs
           40+ GB, which NJS worker nodes do have) quiet - pass the --quiet
           parameter to checkM, but doesn't seem to work for all subcommands)
           -> structure: parameter "subcommand" of String, parameter
           "bin_folder" of String, parameter "out_folder" of String,
           parameter "plots_folder" of String, parameter "seq_file" of
           String, parameter "tetra_file" of String, parameter "dist_value"
           of Long, parameter "threads" of Long, parameter "reduced_tree" of
           type "boolean" (A boolean - 0 for false, 1 for true. @range (0,
           1)), parameter "quiet" of type "boolean" (A boolean - 0 for false,
           1 for true. @range (0, 1))
        """
        # ctx is the context object
        #BEGIN run_checkM
        print('--->\nRunning kb_Msuite.run_checkM\nparams:')
        print(json.dumps(params, indent=1))

        for key, value in list(params.items()):
            if isinstance(value, str):
                params[key] = value.strip()

        if 'subcommand' not in params:
            raise ValueError('"subcommand" parameter field must be specified ' +
                             '(to one of lineage_wf, tetra, bin_qa_plot, dist_plot, etc)')

        checkM_runner = CheckMUtil(self.config, ctx)
        checkM_runner.run_checkM(params['subcommand'], params)

        #END run_checkM
        pass

    def run_checkM_lineage_wf(self, ctx, params):
        """
        :param params: instance of type "CheckMLineageWfParams" (input_ref -
           reference to the input Assembly, AssemblySet, Genome, GenomeSet,
           or BinnedContigs data) -> structure: parameter "input_ref" of
           String, parameter "workspace_name" of String, parameter
           "reduced_tree" of type "boolean" (A boolean - 0 for false, 1 for
           true. @range (0, 1)), parameter "save_output_dir" of type
           "boolean" (A boolean - 0 for false, 1 for true. @range (0, 1)),
           parameter "save_plots_dir" of type "boolean" (A boolean - 0 for
           false, 1 for true. @range (0, 1)), parameter "threads" of Long
        :returns: instance of type "CheckMLineageWfResult" -> structure:
           parameter "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN run_checkM_lineage_wf
        print('--->\nRunning kb_Msuite.run_checkM_lineage_wf\nparams:')
        print(json.dumps(params, indent=1))

        cmu = CheckMUtil(self.config, ctx)
        result = cmu.run_checkM_lineage_wf(params)

        #END run_checkM_lineage_wf

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method run_checkM_lineage_wf return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def run_checkM_lineage_wf_withFilter(self, ctx, params):
        """
        :param params: instance of type "CheckMLineageWf_withFilter_Params"
           (input_ref - reference to the input BinnedContigs data) ->
           structure: parameter "input_ref" of String, parameter
           "workspace_name" of String, parameter "reduced_tree" of type
           "boolean" (A boolean - 0 for false, 1 for true. @range (0, 1)),
           parameter "save_output_dir" of type "boolean" (A boolean - 0 for
           false, 1 for true. @range (0, 1)), parameter "save_plots_dir" of
           type "boolean" (A boolean - 0 for false, 1 for true. @range (0,
           1)), parameter "threads" of Long, parameter "completeness_perc" of
           Double, parameter "contamination_perc" of Double, parameter
           "output_filtered_binnedcontigs_obj_name" of String
        :returns: instance of type "CheckMLineageWf_withFilter_Result" ->
           structure: parameter "report_name" of String, parameter
           "report_ref" of String, parameter "binned_contig_obj_ref" of type
           "obj_ref" (An X/Y/Z style reference e.g. "WS_ID/OBJ_ID/VER")
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN run_checkM_lineage_wf_withFilter
        print('--->\nRunning kb_Msuite.run_checkM_lineage_wf_withFilter\nparams:')
        print(json.dumps(params, indent=1))

        cmu = CheckMUtil(self.config, ctx)
        result = cmu.run_checkM_lineage_wf(params)

        #END run_checkM_lineage_wf_withFilter

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method run_checkM_lineage_wf_withFilter return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]

    def lineage_wf(self, ctx, params):
        """
        A "local method" for calling lineage_wf directly.
        :param params: instance of type "LineageWfParams" (* * Parameters for
           lineage_wf, which runs as a "local method". * * Required
           arguments: *   bin_dir - required - Path to the directory where
           your bins are located *   out_dir - required - Path to a directory
           where we will write output files *   log_path - required - Path to
           a file that will be written to with all log output from *
           stdout and stderr while running `checkm lineage_wf`. *   options -
           optional - A mapping of options to pass to lineage_wf. See the
           README.md *     in the kb_Msuite repo for a list of all of these.
           For options that have no value, simply *     pass an empty
           string.) -> structure: parameter "bin_dir" of String, parameter
           "out_dir" of String, parameter "log_path" of String, parameter
           "options" of mapping from String to String
        :returns: instance of type "LineageWfResult" (* * Output results of
           running the lineage_wf local method. * This returns nothing. Check
           the contents of log_path and out_dir which were passed as *
           parameters to see the output of running this function.) ->
           structure:
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN lineage_wf
        assert params['log_path'], 'You must provide the path for a log file ("log_path")'
        assert params['input_dir'], 'You must provide an input directory ("input_dir")'
        assert params['output_dir'], 'You must provide an output directory ("output_dir")'
        assert os.path.isdir(params['input_dir']), 'The input directory does not exist'
        assert os.path.isdir(params['output_dir']), 'The output directory does not exist'
        assert os.listdir(params['output_dir']) == [], 'The output directory must be empty'
        in_dir = params['input_dir']
        out_dir = params['output_dir']
        log_path = params['log_path']
        run_checkm(in_dir, out_dir, log_path, params.get('options'))
        result = {}
        #END lineage_wf

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method lineage_wf return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
