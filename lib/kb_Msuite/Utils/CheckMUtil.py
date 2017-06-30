# -*- coding: utf-8 -*-
import time
import os
import uuid
import subprocess
import sys

from KBaseReport.KBaseReportClient import KBaseReport

from kb_Msuite.Utils.DataStagingUtils import DataStagingUtils
from kb_Msuite.Utils.OutputBuilder import OutputBuilder


def log(message, prefix_newline=False):
    """Logging function, provides a hook to suppress or redirect log messages."""
    print(('\n' if prefix_newline else '') + '{0:.2f}'.format(time.time()) + ': ' + str(message))
    sys.stdout.flush()


class CheckMUtil:

    def __init__(self, config):
        self.config = config
        self.callback_url = config['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.threads = config['threads']
        self.reduced_tree = config['reduced_tree']


    def run_checkM_lineage_wf(self, params):
        '''
        Main entry point for running the lineage_wf as a KBase App
        '''

        # 0) validate basic parameters
        if 'input_ref' not in params:
            raise ValueError('input_ref field was not set in params for run_checkM_lineage_wf')
        if 'workspace_name' not in params:
            raise ValueError('workspace_name field was not set in params for run_checkM_lineage_wf')


        # 1) stage input data
        dsu = DataStagingUtils(self.config)
        staged_input = dsu.stage_input(params['input_ref'], 'fna')
        input_dir = staged_input['input_dir']
        suffix = staged_input['folder_suffix']
        all_seq_fasta_file = staged_input['all_seq_fasta']

        output_dir = os.path.join(self.scratch, 'output_' + suffix)
        plots_dir = os.path.join(self.scratch, 'plot_' + suffix)
        html_dir = os.path.join(self.scratch, 'html_' + suffix)
        tetra_file = os.path.join(self.scratch, 'tetra_' + suffix + '.tsv')

        log('Staged input directory: ' + input_dir)


        # 2) run the lineage workflow
        lineage_wf_options = {'bin_folder': input_dir,
                              'out_folder': output_dir,
                              'thread': self.threads,
                              'reduced_tree': self.reduced_tree
                              }
        self.run_checkM('lineage_wf', lineage_wf_options)


        # 3) make the plots:
        self.build_checkM_lineage_wf_plots(input_dir, output_dir, plots_dir, all_seq_fasta_file, tetra_file)


        # 4) Package results
        outputBuilder = OutputBuilder(output_dir, plots_dir, self.scratch, self.callback_url)
        output_packages = self._build_output_packages(params, outputBuilder, input_dir)


        # 5) build the HTML report
        os.makedirs(html_dir)
        outputBuilder.build_html_output_for_lineage_wf(html_dir, params['input_ref'])
        html_zipped = outputBuilder.package_folder(html_dir, 'report.html', 'Summarized report from CheckM')


        # 6) save report
        report_params = {'message': '',
                         'direct_html_link_index': 0,
                         'html_links': [html_zipped],
                         'file_links': output_packages,
                         'report_object_name': 'kb_checkM_report_' + str(uuid.uuid4()),
                         'workspace_name': params['workspace_name']
                         }

        kr = KBaseReport(self.callback_url)
        report_output = kr.create_extended_report(report_params)

        return {'report_name': report_output['name'],
                'report_ref': report_output['ref']}


    def build_checkM_lineage_wf_plots(self, bin_folder, out_folder, plots_folder, all_seq_fasta_file, tetra_file):

        # first build generic plot for entire dataset
        log('Creating basic QA plot (checkm bin_qa_plot) ...')
        bin_qa_plot_options = {'bin_folder': bin_folder,
                               'out_folder': out_folder,
                               'plots_folder': plots_folder
                               }
        self.run_checkM('bin_qa_plot', bin_qa_plot_options, dropOutput=True)

        # compute tetranucleotide frequencies based on the concatenated fasta file
        log('Computing tetranucleotide distributions...')
        tetra_options = {'seq_file': all_seq_fasta_file,
                         'tetra_file': tetra_file,
                         'thread': self.threads,
                         'quiet': 1
                         }
        self.run_checkM('tetra', tetra_options, dropOutput=True)

        # plot distributions for each bin
        log('Creating distribution plots per bin...')
        dist_plot_options = {'bin_folder': bin_folder,
                             'out_folder': out_folder,
                             'plots_folder': plots_folder,
                             'tetra_file': tetra_file,
                             'dist_value': 95,
                             'quiet': 1
                             }
        self.run_checkM('dist_plot', dist_plot_options, dropOutput=True)


    def run_checkM(self, subcommand, options, dropOutput=False):
        '''
            subcommand is the checkm subcommand (eg lineage_wf, tetra, bin_qa_plot)
            options indicate, depending on the subcommand:
                bin_folder
                out_folder
                plots_folder
                seq_file
                tetra_file

                reduced_tree
                thread
                dist_value
        '''
        command = self._build_command(subcommand, options)
        log('Running: ' + ' '.join(command))

        log_output_file = None
        if dropOutput:
            # necessary because the checkM --quiet flag doesn't work on the tetra subcommand,
            # and that produces a line per contig
            log_output_file = open(os.path.join(self.scratch, subcommand + '.out'), 'w')
            p = subprocess.Popen(command, cwd=self.scratch, shell=False, stdout=log_output_file, stderr=subprocess.STDOUT)
        else:
            p = subprocess.Popen(command, cwd=self.scratch, shell=False)
        exitCode = p.wait()

        if log_output_file:
            log_output_file.close()

        if (exitCode == 0):
            log('Executed command: ' + ' '.join(command) + '\n' +
                'Exit Code: ' + str(exitCode))
        else:
            raise ValueError('Error running command: ' + ' '.join(command) + '\n' +
                             'Exit Code: ' + str(exitCode))


    def _process_universal_options(self, command_list, options):
        if options.get('thread'):
            command_list.append('-t')
            command_list.append(str(options.get('thread')))

        if options.get('quiet') and str(options.get('quiet')) == '1':
            command_list.append('--quiet')


    def _validate_options(self, options,
                          checkBin=False,
                          checkOut=False,
                          checkPlots=False,
                          checkTetraFile=False,
                          subcommand=''):
        # Note: we can, maybe should, add additional checks on the contents of the folders here
        if checkBin and 'bin_folder' not in options:
            raise ValueError('cannot run checkm ' + subcommand + ' without bin_folder option set')
        if checkOut and 'out_folder' not in options:
            raise ValueError('cannot run checkm ' + subcommand + ' without bin_folder option set')
        if checkPlots and 'plots_folder' not in options:
            raise ValueError('cannot run checkm ' + subcommand + ' without plots_folder option set')
        if checkTetraFile and 'tetra_file' not in options:
            raise ValueError('cannot run checkm ' + subcommand + ' without tetra_file option set')


    def _build_command(self, subcommand, options):

        command = ['checkm', subcommand]
        self._process_universal_options(command, options)

        if subcommand == 'lineage_wf':
            self._validate_options(options, checkBin=True, checkOut=True, subcommand='lineage_wf')
            if 'reduced_tree' in options and str(options['reduced_tree']) == '1':
                command.append('--reduced_tree')
            command.append(options['bin_folder'])
            command.append(options['out_folder'])

        elif subcommand == 'bin_qa_plot':
            self._validate_options(options, checkBin=True, checkOut=True, checkPlots=True, subcommand='bin_qa_plot')
            command.append(options['out_folder'])
            command.append(options['bin_folder'])
            command.append(options['plots_folder'])

        elif subcommand == 'tetra':
            self._validate_options(options, checkTetraFile=True, subcommand='tetra')
            if 'seq_file' not in options:
                raise ValueError('cannot run checkm tetra without seq_file option set')
            command.append(options['seq_file'])
            command.append(options['tetra_file'])

        elif subcommand == 'dist_plot':
            self._validate_options(options, checkBin=True, checkOut=True, checkPlots=True, checkTetraFile=True,
                                   subcommand='dist_plot')
            command.append(options['out_folder'])
            command.append(options['bin_folder'])
            command.append(options['plots_folder'])
            command.append(options['tetra_file'])
            if 'dist_value' not in options:
                raise ValueError('cannot run checkm dist_plot without dist_value option set')
            command.append(str(options['dist_value']))

        else:
            raise ValueError('Invalid or unsupported checkM subcommand: ' + str(subcommand))

        return command


    def _build_output_packages(self, params, outputBuilder, input_dir):

        output_packages = []

        if 'save_output_dir' in params and str(params['save_output_dir']) == '1':
            log('packaging full output directory')
            zipped_output_file = outputBuilder.package_folder(outputBuilder.output_dir, 'full_output.zip',
                                                              'Full output of CheckM')
            output_packages.append(zipped_output_file)
        else:
            log('not packaging full output directory, selecting specific files')
            crit_out_dir = os.path.join(self.scratch, 'critical_output_' + os.path.basename(input_dir))
            os.makedirs(crit_out_dir)
            zipped_output_file = outputBuilder.package_folder(outputBuilder.output_dir, 'selected_output.zip',
                                                              'Selected output from the CheckM analysis')
            output_packages.append(zipped_output_file)


        if 'save_plots_dir' in params and str(params['save_plots_dir']) == '1':
            log('packaging output plots directory')
            zipped_output_file = outputBuilder.package_folder(outputBuilder.plots_dir, 'plots.zip',
                                                              'Output plots from CheckM')
            output_packages.append(zipped_output_file)
        else:
            log('not packaging output plots directory')

        return output_packages
