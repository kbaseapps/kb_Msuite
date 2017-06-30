import os
import shutil
import ast
import sys
import time

from DataFileUtil.DataFileUtilClient import DataFileUtil


def log(message, prefix_newline=False):
    """Logging function, provides a hook to suppress or redirect log messages."""
    print(('\n' if prefix_newline else '') + '{0:.2f}'.format(time.time()) + ': ' + str(message))
    sys.stdout.flush()


class OutputBuilder(object):
    '''
    Constructs the output HTML report and artifacts based on a CheckM lineage_wf
    run.  This includes running any necssary plotting utilities of CheckM.
    '''

    def __init__(self, output_dir, plots_dir, scratch_dir, callback_url):
        self.output_dir = output_dir
        self.plots_dir = plots_dir
        self.scratch = scratch_dir
        self.callback_url = callback_url

        self.DIST_PLOT_EXT = '.ref_dist_plots.png'


    def package_folder(self, folder_path, zip_file_name, zip_file_description):
        ''' Simple utility for packaging a folder and saving to shock '''
        dfu = DataFileUtil(self.callback_url)
        output = dfu.file_to_shock({'file_path': folder_path,
                                    'make_handle': 0,
                                    'pack': 'zip'})
        return {'shock_id': output['shock_id'],
                'name': zip_file_name,
                'description': zip_file_description}


    def build_critical_output(self, critical_out_dir):
        src = self.output_dir
        dest = critical_out_dir

        self._copy_file_ignore_errors('lineage.ms', src, dest)

        os.makedirs(os.path.join(dest, 'storage'))

        self._copy_file_ignore_errors(os.path.join('storage', 'bin_stats.analyze.tsv'), src, dest)
        self._copy_file_ignore_errors(os.path.join('storage', 'bin_stats.tree.tsv'), src, dest)
        self._copy_file_ignore_errors(os.path.join('storage', 'bin_stats_ext.tsv'), src, dest)
        self._copy_file_ignore_errors(os.path.join('storage', 'marker_gene_stats.tsv'), src, dest)
        self._copy_file_ignore_errors(os.path.join('storage', 'tree', 'concatenated.tre'), src, dest)


    def build_html_output_for_lineage_wf(self, html_dir, object_name):
        '''
        Based on the output of CheckM lineage_wf, build an HTML report
        '''

        # move plots we need into the html directory
        plot_name = 'bin_qa_plot.png'
        shutil.copy(os.path.join(self.plots_dir, plot_name), os.path.join(html_dir, plot_name))
        self._copy_ref_dist_plots(self.plots_dir, html_dir)

        # write the html report to file
        html = open(os.path.join(html_dir, 'report.html'), 'w')

        # header
        self._write_html_header(html, object_name)
        html.write('<body>\n')

        # include the single main summary figure
        html.write('<img src="' + plot_name + '" width="90%" />\n')
        html.write('<br><br><br>\n')

        # print out the info table
        self.build_summary_table(html, html_dir)

        html.write('</body>\n</html>\n')
        html.close()

        return self.package_folder(html_dir, 'report.html', 'Assembled report from CheckM')


    def build_summary_table(self, html, html_dir):

        stats_file = os.path.join(self.output_dir, 'storage', 'bin_stats_ext.tsv')
        if not os.path.isfile(stats_file):
            log('Warning! no stats file found (looking at: ' + stats_file + ')')
            return

        bin_stats = []
        with open(stats_file) as lf:
            for line in lf:
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                col = line.split('\t')
                bin_id = col[0]
                data = ast.literal_eval(col[1])
                bin_stats.append({'bid': bin_id, 'data': data})


        fields = [{'id': 'marker lineage', 'display': 'Marker Lineage'},
                  {'id': '# genomes', 'display': '# Genomes'},
                  {'id': '# markers', 'display': '# Markers'},
                  {'id': '# marker sets', 'display': '# Marker Sets'},
                  {'id': '0', 'display': '0'},
                  {'id': '1', 'display': '1'},
                  {'id': '2', 'display': '2'},
                  {'id': '3', 'display': '3'},
                  {'id': '4', 'display': '4'},
                  {'id': '5+', 'display': '5+'},
                  {'id': 'Completeness', 'display': 'Completeness', 'round': 3},
                  {'id': 'Contamination', 'display': 'Contamination', 'round': 3}]

        html.write('<table>\n')
        html.write('  <tr>\n')
        html.write('    <th><b>Bin Name</b></th>\n')
        for f in fields:
            html.write('    <th>' + f['display'] + '</th>\n')
        html.write('  </tr>\n')

        for b in bin_stats:
            html.write('  <tr>\n')
            dist_plot_file = os.path.join(html_dir, str(b['bid']) + self.DIST_PLOT_EXT)
            if os.path.isfile(dist_plot_file):
                self._write_dist_html_page(html_dir, b['bid'])
                html.write('    <td><a href="' + b['bid'] + '.html">' + b['bid'] + '</td>\n')
            else:
                html.write('    <td>' + b['bid'] + '</td>\n')
            for f in fields:
                if f['id'] in b['data']:
                    value = str(b['data'][f['id']])
                    if f.get('round'):
                        value = str(round(b['data'][f['id']], f['round']))
                    html.write('    <td>' + value + '</td>\n')
                else:
                    html.write('    <td></td>\n')
            html.write('  </tr>\n')

        html.write('</table>\n')


    def _write_html_header(self, html, object_name):

        html.write('<html>\n')
        html.write('<head>\n')
        html.write('<title>CheckM Report for ' + object_name + '</title>')

        style = '''
        <style style="text/css">
            a {
                color: #337ab7;
            }

            a:hover {
                color: #23527c;
            }

            table {
                border: 1px solid #bbb;
                border-collapse: collapse;
            }

            th, td {
                text-align: left;
                border: 1px solid #bbb;
                padding: 8px;
            }

            tr:nth-child(odd) {
                background-color: #f9f9f9;
            }

            tr:hover {
                background-color: #f5f5f5;
            }
        </style>\n</head>\n'''

        html.write(style)
        html.write('</head>\n')

    def _copy_file_ignore_errors(self, filename, src_folder, dest_folder):
        src = os.path.join(src_folder, filename)
        dest = os.path.join(dest_folder, filename)
        log('copying ' + src + ' to ' + dest)
        try:
            shutil.copy(src, dest)
        except:
            # TODO: add error message reporting
            log('copy failed')


    def _write_dist_html_page(self, html_dir, bin_id):

        # write the html report to file
        html = open(os.path.join(html_dir, bin_id + '.html'), 'w')

        html.write('<html>\n')
        html.write('<head>\n')
        html.write('<title>CheckM Dist Plots for Bin' + bin_id + '</title>')
        html.write('<style style="text/css">\n a { color: #337ab7; } \n a:hover { color: #23527c; }\n</style>\n')
        html.write('<body>\n')
        html.write('<br><a href="report.html">Back to summary</a><br>\n')
        html.write('<center><h2>Bin: ' + bin_id + '</h2></center>\n')
        html.write('<img src="' + bin_id + self.DIST_PLOT_EXT + '" width="90%" />\n')
        html.write('<br><br><br>\n')
        html.write('</body>\n</html>\n')
        html.close()


    def _copy_ref_dist_plots(self, plots_dir, dest_folder):
        for plotfile in os.listdir(plots_dir):
            plot_file_path = os.path.join(plots_dir, plotfile)
            if os.path.isfile(plot_file_path) and plotfile.endswith(self.DIST_PLOT_EXT):
                try:
                    shutil.copy(os.path.join(plots_dir, plotfile),
                                os.path.join(dest_folder, plotfile))
                except:
                    # TODO: add error message reporting
                    log('copy of ' + plot_file_path + ' to html directory failed')
