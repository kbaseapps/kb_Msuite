# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from Workspace.WorkspaceClient import Workspace as workspaceService

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from MetagenomeUtils.MetagenomeUtilsClient import MetagenomeUtils

from kb_Msuite.kb_MsuiteImpl import kb_Msuite
from kb_Msuite.kb_MsuiteServer import MethodContext
from kb_Msuite.authclient import KBaseAuth as _KBaseAuth

from kb_Msuite.Utils.CheckMUtil import CheckMUtil
from kb_Msuite.Utils.DataStagingUtils import DataStagingUtils
from kb_Msuite.Utils.OutputBuilder import OutputBuilder


class CoreCheckMTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_Msuite'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_Msuite',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_Msuite(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.checkm_runner = CheckMUtil(cls.cfg)

        suffix = int(time.time() * 1000)
        cls.wsName = "test_kb_Msuite_" + str(suffix)
        cls.ws_info = cls.wsClient.create_workspace({'workspace': cls.wsName})
        cls.au = AssemblyUtil(os.environ['SDK_CALLBACK_URL'])
        cls.mu = MetagenomeUtils(os.environ['SDK_CALLBACK_URL'])

        # stage an input and output directory
        cls.input_dir = os.path.join(cls.scratch, 'input_1')
        cls.output_dir = os.path.join(cls.scratch, 'output_1')
        cls.all_seq_fasta = os.path.join(cls.scratch, 'all_seq.fna')
        shutil.copytree(os.path.join('data', 'example_out', 'input'), cls.input_dir)
        shutil.copytree(os.path.join('data', 'example_out', 'output'), cls.output_dir)
        shutil.copy(os.path.join('data', 'example_out', 'all_seq.fna'), cls.all_seq_fasta)

        # prepare WS data
        cls.prepare_data()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace ' + cls.wsName + ' was deleted')
        pass

    def getWsClient(self):
        return self.__class__.wsClient

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx


    @classmethod
    def prepare_data(cls):
        test_directory_name = 'test_kb_Msuite'
        cls.test_directory_path = os.path.join(cls.scratch, test_directory_name)
        os.makedirs(cls.test_directory_path)

        # first build the example Assembly
        cls.assembly_filename = 'assembly.fasta'
        cls.assembly_fasta_file_path = os.path.join(cls.scratch, cls.assembly_filename)
        shutil.copy(os.path.join("data", cls.assembly_filename), cls.assembly_fasta_file_path)
        assembly_params = {'file': {'path': cls.assembly_fasta_file_path},
                           'workspace_name': cls.ws_info[1],
                           'assembly_name': 'MyMetagenomeAssembly'
                           }
        cls.assembly_ref1 = cls.au.save_assembly_from_fasta(assembly_params)
        pprint('Saved Assembly: ' + cls.assembly_ref1)

        # next save the bins
        cls.binned_contigs_dir_name = 'binned_contigs'
        cls.binned_contigs_dir_path = os.path.join(cls.scratch, cls.binned_contigs_dir_name)
        shutil.copytree(os.path.join("data", cls.binned_contigs_dir_name), cls.binned_contigs_dir_path)

        binned_contigs_params = {'file_directory': cls.binned_contigs_dir_path,
                                 'workspace_name': cls.ws_info[1],
                                 'assembly_ref': cls.assembly_ref1,
                                 'binned_contig_name': 'MyBins'
                                 }
        cls.binned_contigs_ref1 = cls.mu.file_to_binned_contigs(binned_contigs_params)['binned_contig_obj_ref']
        pprint('Saved BinnedContigs: ' + cls.binned_contigs_ref1)


    # Uncomment to skip this test
    # @unittest.skip("skipped test_checkM_lineage_wf_full_app")
    def test_checkM_lineage_wf_full_app(self):

        # run checkM lineage_wf app on a single assembly
        params = {
            'workspace_name': self.ws_info[1],
            'input_ref': self.assembly_ref1,
            'save_output_dir': 0,
            'save_plots_dir': 1
        }
        result = self.getImpl().run_checkM_lineage_wf(self.getContext(), params)[0]

        pprint('End to end test result:')
        pprint(result)

        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        rep = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']

        self.assertEquals(rep['direct_html_link_index'], 0)
        self.assertEquals(len(rep['file_links']), 2)
        self.assertEquals(len(rep['html_links']), 1)
        self.assertEquals(rep['html_links'][0]['name'], 'report.html')


        # Even with the reduced_tree option, this will take a long time and crash if your
        # machine has less than ~16gb memory

        # run checkM lineage_wf app on BinnedContigs
        # params = {
        #     'workspace_name': self.ws_info[1],
        #     'input_ref': self.binned_contigs_ref1
        # }
        # result = self.getImpl().run_checkM_lineage_wf(self.getContext(), params)
        # print('RESULT:')
        # pprint(result)

    # Uncomment to skip this test
    # @unittest.skip("skipped test_data_staging")
    def test_data_staging(self):

        # test stage assembly
        dsu = DataStagingUtils(self.cfg)
        staged_input = dsu.stage_input(self.assembly_ref1, 'strange_fasta_extension')
        pprint(staged_input)

        self.assertTrue(os.path.isdir(staged_input['input_dir']))
        self.assertTrue(os.path.isfile(staged_input['all_seq_fasta']))
        self.assertIn('folder_suffix', staged_input)

        self.assertTrue(os.path.isfile(os.path.join(staged_input['input_dir'],
                                                    'MyMetagenomeAssembly.strange_fasta_extension')))

        # test stage binned contigs
        staged_input2 = dsu.stage_input(self.binned_contigs_ref1, 'fna')
        pprint(staged_input2)

        self.assertTrue(os.path.isdir(staged_input2['input_dir']))
        self.assertTrue(os.path.isfile(staged_input2['all_seq_fasta']))
        self.assertIn('folder_suffix', staged_input2)

        self.assertTrue(os.path.isfile(os.path.join(staged_input2['input_dir'], 'out_header.001.fna')))
        self.assertTrue(os.path.isfile(os.path.join(staged_input2['input_dir'], 'out_header.002.fna')))
        self.assertTrue(os.path.isfile(os.path.join(staged_input2['input_dir'], 'out_header.003.fna')))


    # Uncomment to skip this test
    # @unittest.skip("skipped test_output_plotting")
    def test_output_plotting(self):

        cmu = CheckMUtil(self.cfg)
        plots_dir = os.path.join(self.scratch, 'plots_1')
        html_dir = os.path.join(self.scratch, 'html_1')
        tetra_file = os.path.join(self.scratch, 'tetra_1.tsv')

        cmu.build_checkM_lineage_wf_plots(self.input_dir, self.output_dir, plots_dir, self.all_seq_fasta, tetra_file)
        self.assertTrue(os.path.isdir(plots_dir))
        self.assertTrue(os.path.isfile(os.path.join(plots_dir, 'bin_qa_plot.png')))
        self.assertTrue(os.path.isfile(os.path.join(plots_dir, 'NewBins.001.ref_dist_plots.png')))
        self.assertTrue(os.path.isfile(os.path.join(plots_dir, 'NewBins.002.ref_dist_plots.png')))
        self.assertTrue(os.path.isfile(tetra_file))

        ob = OutputBuilder(self.output_dir, plots_dir, self.scratch, self.callback_url)
        os.makedirs(html_dir)
        res = ob.build_html_output_for_lineage_wf(html_dir, 'MyCheckMOutput')
        self.assertIn('shock_id', res)
        self.assertIn('name', res)
        self.assertIn('description', res)
        self.assertEqual(res['name'], 'report.html')


    # Uncomment to skip this test
    # @unittest.skip("skipped test_output_plotting")
    def test_checkM_local_function_wiring(self):

        # run checkM lineage_wf app on a single assembly
        tetra_file = os.path.join(self.scratch, 'tetra_test.tsv')
        params = {
            'subcommand': 'tetra',
            'seq_file': self.all_seq_fasta,
            'tetra_file': tetra_file
        }
        self.getImpl().run_checkM(self.getContext(), params)
        os.path.isfile(tetra_file)
