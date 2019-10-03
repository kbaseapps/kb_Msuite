# -*- coding: utf-8 -*-
import time
import os
import uuid
import subprocess
import sys
import re
import ast
import json
from decimal import Decimal

from installed_clients.KBaseReportClient import KBaseReport

from kb_Msuite.Utils.DataStagingUtils import DataStagingUtils
from kb_Msuite.Utils.OutputBuilder import OutputBuilder


def log(message, prefix_newline=False):
    """Logging function, provides a hook to suppress or redirect log messages."""
    print(('\n' if prefix_newline else '') + '{0:.2f}'.format(time.time()) + ': ' + str(message))
    sys.stdout.flush()


class CheckMUtil:

    def __init__(self, config, ctx):
        self.config = config
        self.ctx = ctx
        self.callback_url = config['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.threads = config['threads']

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
        self.fasta_extension = 'fna'
        self.binned_contigs_builder_fasta_extension = 'fasta'
        dsu = DataStagingUtils(self.config, self.ctx)
        staged_input = dsu.stage_input(params['input_ref'], self.fasta_extension)
        input_dir = staged_input['input_dir']
        suffix = staged_input['folder_suffix']
        all_seq_fasta_file = staged_input['all_seq_fasta']

        filtered_bins_dir = os.path.join(self.scratch, 'filtered_bins_' + suffix)
        output_dir = os.path.join(self.scratch, 'output_' + suffix)
        plots_dir = os.path.join(self.scratch, 'plot_' + suffix)
        html_dir = os.path.join(self.scratch, 'html_' + suffix)
        tetra_file = os.path.join(self.scratch, 'tetra_' + suffix + '.tsv')

        log('Staged input directory: ' + input_dir)

        # 2) run the lineage workflow
        lineage_wf_options = {'bin_folder': input_dir,
                              'out_folder': output_dir,
                              'threads': self.threads
                              }
        if ('reduced_tree' in params and params['reduced_tree'] is not None and
           int(params['reduced_tree'])) == 1:
            lineage_wf_options['reduced_tree'] = params['reduced_tree']

        self.run_checkM('lineage_wf', lineage_wf_options)

        # 3) optionally filter bins by quality scores and save object
        created_objects = None
        removed_bins = None
        outputBuilder = OutputBuilder(output_dir, plots_dir, self.scratch, self.callback_url)
        if dsu.get_data_obj_type (params['input_ref']) == 'KBaseMetagenomes.BinnedContigs' \
           and params.get('output_filtered_binnedcontigs_obj_name'):

            filtered_obj_info = self._filter_binned_contigs (params, 
                                                             dsu, 
                                                             outputBuilder, 
                                                             input_dir, 
                                                             output_dir, 
                                                             filtered_bins_dir)
            if filtered_obj_info == None:
                log("No Bins passed QC filters.  Not saving filtered BinnedContig object")
            else:
                removed_bins = filtered_obj_info['removed_bin_IDs']
                created_objects = [{'ref': filtered_obj_info['filtered_obj_ref'],
                                    'description': 'HQ BinnedContigs '+filtered_obj_info['filtered_obj_name']}]
            
        # 4) make the plots:
        self.build_checkM_lineage_wf_plots(input_dir, output_dir, plots_dir,
                                           all_seq_fasta_file, tetra_file)

        # 5) Package results
        output_packages = self._build_output_packages(params, outputBuilder, input_dir)

        # 6) build the HTML report
        os.makedirs(html_dir)
        html_files = outputBuilder.build_html_output_for_lineage_wf(html_dir, params['input_ref'], removed_bins=removed_bins)
        html_zipped = outputBuilder.package_folder(html_dir, 
                                                   html_files[0],
                                                   'Summarized report from CheckM')

        # 7) save report
        report_params = {'message': '',
                         'direct_html_link_index': 0,
                         'html_links': [html_zipped],
                         'file_links': output_packages,
                         'report_object_name': 'kb_checkM_report_' + str(uuid.uuid4()),
                         'workspace_name': params['workspace_name']
                         }
        if created_objects:
            report_params['objects_created'] = created_objects

        kr = KBaseReport(self.callback_url)
        report_output = kr.create_extended_report(report_params)

        return {'report_name': report_output['name'],
                'report_ref': report_output['ref']}

    def build_checkM_lineage_wf_plots(self, bin_folder, out_folder, plots_folder,
                                      all_seq_fasta_file, tetra_file):

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
                         'threads': self.threads,
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
                threads
                dist_value
        '''
        command = self._build_command(subcommand, options)
        log('Running: ' + ' '.join(command))

        log_output_file = None
        if dropOutput:
            # necessary because the checkM --quiet flag doesn't work on the tetra subcommand,
            # and that produces a line per contig
            log_output_file = open(os.path.join(self.scratch, subcommand + '.out'), 'w')
            p = subprocess.Popen(command, cwd=self.scratch, shell=False,
                                 stdout=log_output_file, stderr=subprocess.STDOUT)
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
        if options.get('threads'):
            command_list.append('-t')
            command_list.append(str(options.get('threads')))

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
            self._validate_options(options, checkBin=True, checkOut=True, checkPlots=True,
                                   subcommand='bin_qa_plot')
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
            self._validate_options(options, checkBin=True, checkOut=True, checkPlots=True,
                                   checkTetraFile=True, subcommand='dist_plot')
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

    def _filter_binned_contigs(self, 
                               params,
                               dataStagingUtils,
                               outputBuilder, 
                               input_dir, 
                               output_dir, 
                               filtered_bins_dir):
        filtered_binned_contig_obj_name = None
        filtered_binned_contig_obj_ref  = None
        if not params.get('output_filtered_binnedcontigs_obj_name'):
            return None

        # prep fs stuff and get bin IDs
        if not os.path.exists(filtered_bins_dir):
            os.makedirs(filtered_bins_dir)
        bin_stats_ext_file = os.path.join(output_dir, 'storage', 'bin_stats_ext.tsv')
        bin_fasta_files_by_bin_ID = dataStagingUtils.get_bin_fasta_files(input_dir, self.fasta_extension)
        bin_IDs = []
        for bin_ID in sorted(bin_fasta_files_by_bin_ID.keys()):
            bin_IDs.append(bin_ID)
            log("Contigs Fasta file found for Bin ID: "+bin_ID)

        # read CheckM stats to get completeness and contamination scores
        bin_stats_obj = dict()
        QC_scores = dict()
        retained_bin_IDs = dict()
        removed_bin_IDs = dict()
        with open (bin_stats_ext_file, 'r') as bin_stats_ext_handle:
            for bin_stats_line in bin_stats_ext_handle:
                bin_stats_line.rstrip()
                [full_bin_ID, bin_stats_json_str] = bin_stats_line.split("\t")
                bin_ID = re.sub('^[^\.]+\.', '', full_bin_ID.replace(self.fasta_extension,''))

                bin_stats_json_str = json.dumps(ast.literal_eval(bin_stats_json_str))
                bin_stats_obj[bin_ID] = json.loads(bin_stats_json_str, parse_float=Decimal)
        for bin_ID in bin_IDs:
            if bin_ID not in bin_stats_obj:
                raise ValueError ("Bin ID "+bin_ID+" not found in bin stats")

            QC_scores[bin_ID] = dict()
            QC_scores[bin_ID]['completeness'] = float(bin_stats_obj[bin_ID]['Completeness'])
            QC_scores[bin_ID]['contamination'] = float(bin_stats_obj[bin_ID]['Contamination'])
            log("Bin "+bin_ID+" CheckM COMPLETENESS:  "+str(QC_scores[bin_ID]['completeness']))
            log("Bin "+bin_ID+" CheckM CONTAMINATION: "+str(QC_scores[bin_ID]['contamination']))

        # copy filtered bin scaffold files to filtered dir
        some_bins_are_HQ = False
        test_completeness = False
        test_contamination = False
        if params.get('completeness_perc') \
           and float(params.get('completeness_perc')) > 0.0:
            test_completeness = True
            completeness_thresh = float(params.get('completeness_perc'))
        if params.get('contamination_perc') \
           and float(params.get('contamination_perc')) < 100.0:
            test_contamination = True
            contamination_thresh = float(params.get('contamination_perc'))
        
        bin_basename = 'Bin'
        for bin_ID in bin_IDs:
            bin_is_HQ = True
            this_comp = QC_scores[bin_ID]['completeness']
            this_cont = QC_scores[bin_ID]['contamination']
            if test_completeness and this_comp < completeness_thresh:
                bin_is_HQ = False
                log("Bin "+bin_ID+" Completeness of "+str(this_comp)+" below thresh "+str(completeness_thresh))
            if test_contamination and this_cont > contamination_thresh:
                bin_is_HQ = False
                log("Bin "+bin_ID+" Contamination of "+str(this_cont)+" above thresh "+str(contamination_thresh))
            
            if not bin_is_HQ:
                log("Bin "+bin_ID+" didn't pass QC filters.  Skipping.")
            else:
                log("Bin "+bin_ID+" passed QC filters.  Adding to new BinnedContigs")
                some_bins_are_HQ = True
                retained_bin_IDs[bin_ID] = True
                src_path = bin_fasta_files_by_bin_ID[bin_ID]
                dst_path = os.path.join(filtered_bins_dir, bin_basename+'.'+str(bin_ID)+'.'+self.binned_contigs_builder_fasta_extension)
                outputBuilder._copy_file_new_name_ignore_errors (src_path, dst_path)
        for bin_ID in bin_IDs:
            if bin_ID not in retained_bin_IDs:
                removed_bin_IDs[bin_ID] = True

        # create BinnedContig object from filtered bins
        if not some_bins_are_HQ:
            return None
        assembly_ref = dataStagingUtils.read_assembly_ref_from_binnedcontigs(params['input_ref'])
        bin_summary_path = dataStagingUtils.build_bin_summary_file_from_binnedcontigs_obj (params['input_ref'], filtered_bins_dir, bin_basename, self.binned_contigs_builder_fasta_extension)
        new_binned_contigs_info = outputBuilder.save_binned_contigs (params, assembly_ref, filtered_bins_dir)

        return { 'filtered_obj_name': new_binned_contigs_info['obj_name'],
                 'filtered_obj_ref': new_binned_contigs_info['obj_ref'],
                 'retained_bin_IDs': retained_bin_IDs,
                 'removed_bin_IDs': removed_bin_IDs
             }


    def _build_output_packages(self, params, outputBuilder, input_dir):
        output_packages = []


        # create bin report summary TSV table text file
        log('creating TSV summary table text file')
        tab_text_dir = os.path.join(outputBuilder.output_dir, 'tab_text')
        tab_text_file = 'CheckM_summary_table.tsv'
        tab_text_files = outputBuilder.build_summary_tsv_file(tab_text_dir, tab_text_file)
        tab_text_zipped = outputBuilder.package_folder(tab_text_dir, 
                                                       tab_text_file+'.zip',
                                                       'TSV Summary Table from CheckM')
        output_packages.append(tab_text_zipped)


        # if 'save_output_dir' in params and str(params['save_output_dir']) == '1':
        if True:
            log('packaging full output directory')
            zipped_output_file = outputBuilder.package_folder(outputBuilder.output_dir,
                                                              'full_output.zip',
                                                              'Full output of CheckM')
            output_packages.append(zipped_output_file)
        else:  # ADD LATER?
            log('not packaging full output directory, selecting specific files')
            crit_out_dir = os.path.join(self.scratch, 'critical_output_' + os.path.basename(
                                                                                    input_dir))
            os.makedirs(crit_out_dir)
            zipped_output_file = outputBuilder.package_folder(outputBuilder.output_dir,
                                                              'selected_output.zip',
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
