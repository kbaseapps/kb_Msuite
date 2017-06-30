# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import json

from pprint import pprint

from kb_Msuite.Utils.CheckMUtil import CheckMUtil
from kb_Msuite.Utils.DataStagingUtils import DataStagingUtils
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
    VERSION = "1.1.0"
    GIT_URL = "git@github.com:kbaseapps/kb_Msuite"
    GIT_COMMIT_HASH = "8e65e17fb7ef3a95e0f9a5b861b3391c78c6ec36"

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
           to a value between 0 and 100 thread -  number of threads
           reduced_tree - if set to 1, run checkM with the reduced_tree flag,
           which will keep memory limited to less than 16gb quiet - pass the
           --quite parameter to checkM, but doesn't seem to work for all
           subcommands) -> structure: parameter "subcommand" of String,
           parameter "bin_folder" of String, parameter "out_folder" of
           String, parameter "plots_folder" of String, parameter "seq_file"
           of String, parameter "tetra_file" of String, parameter
           "dist_value" of Long, parameter "thread" of Long, parameter
           "reduced_tree" of type "boolean" (A boolean - 0 for false, 1 for
           true. @range (0, 1)), parameter "quiet" of type "boolean" (A
           boolean - 0 for false, 1 for true. @range (0, 1))
        """
        # ctx is the context object
        #BEGIN run_checkM
        print('--->\nRunning kb_Msuite.run_checkM\nparams:')
        print(json.dumps(params, indent=1))

        for key, value in params.iteritems():
            if isinstance(value, basestring):
                params[key] = value.strip()

        if 'subcommand' not in params:
            raise ValueError('"subcommand" parameter field must be specified ' +
                             '(to one of lineage_wf, tetra, bin_qa_plot, dist_plot, etc)')

        checkM_runner = CheckMUtil(self.config)
        checkM_runner.run_checkM(params['subcommand'], params)

        #END run_checkM
        pass

    def run_checkM_lineage_wf(self, ctx, params):
        """
        :param params: instance of type "CheckMLineageWfParams" (input_ref -
           reference to the input Assembly or BinnedContigs data (could be
           expanded to include Genome objects as well)) -> structure:
           parameter "input_ref" of String, parameter "workspace_name" of
           String, parameter "save_output_dir" of type "boolean" (A boolean -
           0 for false, 1 for true. @range (0, 1)), parameter
           "save_plots_dir" of type "boolean" (A boolean - 0 for false, 1 for
           true. @range (0, 1))
        :returns: instance of type "CheckMLineageWfResult" -> structure:
           parameter "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN run_checkM_lineage_wf
        print('--->\nRunning kb_Msuite.run_checkM_lineage_wf\nparams:')
        print(json.dumps(params, indent=1))

        cmu = CheckMUtil(self.config)
        result = cmu.run_checkM_lineage_wf(params)

        #END run_checkM_lineage_wf

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method run_checkM_lineage_wf return value ' +
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
