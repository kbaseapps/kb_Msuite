# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import shutil

from os import environ
from configparser import ConfigParser

from pprint import pprint  # noqa: F401

from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.MetagenomeUtilsClient import MetagenomeUtils
from installed_clients.SetAPIServiceClient import SetAPI
from installed_clients.WorkspaceClient import Workspace

from kb_Msuite.kb_MsuiteImpl import kb_Msuite
from kb_Msuite.kb_MsuiteServer import MethodContext
from kb_Msuite.authclient import KBaseAuth as _KBaseAuth

from kb_Msuite.Utils.CheckMUtil import CheckMUtil
from kb_Msuite.Utils.DataStagingUtils import DataStagingUtils
from kb_Msuite.Utils.OutputBuilder import OutputBuilder


TEST_DATA = {
    'assembly_list': [
        {
            'attr': 'assembly_virus_ref',
            'name': 'Virus.Assembly.1KB',
            'path': 'GCF_002817975.1_ASM281797v1_genomic.fna',
        }, {
            'attr': 'assembly_a_ref',
            'name': 'Assembly.A.176KB',
            'path': 'GCF_001274515.1_ASM127451v1_genomic.fna',
        }, {
            'attr': 'assembly_b_ref',
            'name': 'Assembly.B.654KB',
            'path': 'GCF_005237295.1_ASM523729v1_genomic.fna',
        }, {
            'path': 'assembly.fasta',
            'name': 'Test.Assembly',
            'attr': 'assembly_OK_ref',
        }, {
            # contig that breaks checkm v1.0.7 reduced_tree (works on v1.0.8)
            'path': 'offending_contig_67815-67907.fa',
            'name': 'Dodgy_Contig.Assembly',
            'attr': 'assembly_dodgy_ref',
        },
    ],
    'assemblyset_list': [],
    'genome_list': [
        {
            'path': 'GCF_002817975.1_ASM281797v1_genomic.gbff',
            'name': 'Virus.Genome.4KB',
            'attr': 'genome_virus_ref',
        }, {
            'path': 'GCF_001274515.1_ASM127451v1_genomic.gbff',
            'name': 'Genome.A.469KB',
            'attr': 'genome_a_ref',
        }, {
            'path': 'GCF_005237295.1_ASM523729v1_genomic.gbff',
            'name': 'Genome.B.1_6MB',
            'attr': 'genome_b_ref',
        }, {
            'path': 'GCF_000022285.1_ASM2228v1_genomic.gbff',
            'name': 'Genome.C.3_4MB',
            'attr': 'genome_c_ref',
        }, {
            'path': 'GCF_001439985.1_wTPRE_1.0_genomic.gbff',
            'name': 'Genome.D.2_5MB',
            'attr': 'genome_d_ref',
        },
    ],
    'genomeset_list': [],
    'binned_contigs_list': [
        {
            'path': 'binned_contigs',
            'name': 'Binned_Contigs',
            'attr': 'binned_contigs_ref',
            'assembly': 'assembly_OK_ref',
        }, {
            'path': 'binned_contigs_empty',
            'name': 'Binned_Contigs_Empty',
            'attr': 'binned_contigs_empty_ref',
            'assembly': 'assembly_OK_ref',
        },
    ],
}


class CoreCheckMTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        test_time_stamp = int(time.time() * 1000)

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
        cls.ctx.update({
            'token': token,
            'user_id': user_id,
            'provenance': [{
                'service': 'kb_Msuite',
                'method': 'please_never_use_it_in_production',
                'method_params': []
            }],
            'authenticated': 1
        })
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kb_Msuite(cls.cfg)
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.scratch = cls.cfg['scratch']
        cls.appdir = cls.cfg['appdir']

        cls.test_data_dir = os.path.join(cls.scratch, 'test_data')

        exists = os.path.exists(cls.test_data_dir)
        print('test data dir exists: ' + str(exists))
        os.makedirs(cls.test_data_dir, exist_ok=True)

        cls.suffix = test_time_stamp
        cls.checkm_runner = CheckMUtil(cls.cfg, cls.ctx)

        cls.wsName = "test_kb_Msuite_" + str(cls.suffix)
        cls.ws_info = cls.wsClient.create_workspace({'workspace': cls.wsName})

        cls.au = AssemblyUtil(os.environ['SDK_CALLBACK_URL'])
        cls.gfu = GenomeFileUtil(os.environ['SDK_CALLBACK_URL'], service_ver='dev')
        cls.mu = MetagenomeUtils(os.environ['SDK_CALLBACK_URL'])
        cls.setAPI = SetAPI(url=cls.cfg['srv-wiz-url'], token=cls.ctx['token'])
        cls.kr = KBaseReport(os.environ['SDK_CALLBACK_URL'])

        cls.data_loaded = False
        # prepare WS data
        # cls.prepare_data()

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

    def getConfig(self):
        return self.__class__.serviceImpl.config

    def _prep_assembly(self, assembly):
        '''
        input: dict of assembly data in the form
        {
            'path': '/path/to/assembly/file.fna',
            'name': 'Cool_Assembly_Name',
            'attr': 'assembly_blah_ref', # name of the attribute to populate
        }

        '''
        if hasattr(self, assembly['attr']):
            return

        assembly_file_path = os.path.join(self.test_data_dir, "assemblies", assembly['path'])
        if not os.path.exists(assembly_file_path):
            shutil.copy(os.path.join("data", "assemblies", assembly['path']), assembly_file_path)

        saved_assembly = self.au.save_assembly_from_fasta({
            'file': {'path': assembly_file_path},
            'workspace_name': self.ws_info[1],
            'assembly_name': assembly['name'],
        })
        setattr(self, assembly['attr'], saved_assembly)
        print({
            'Saved Assembly': saved_assembly,
            assembly['attr']: getattr(self, assembly['attr']),
        })

    def setUp(self):
        print("Running prepare data")
        self.prepare_data()
        print("Done")

    def _prep_assemblyset(self, assemblyset):
        '''
        input: dict of assemblyset data in the form:
        {
            'name': 'Cool_AssemblySet_Name',
            'items': [{}]
            'attr': 'assemblyset_blah_ref',
        }

        '''
        if hasattr(self, assemblyset['attr']):
            return
        saved_assembly_set = self.setAPI.save_assembly_set_v1({
            'workspace_name': self.ws_info[1],
            'output_object_name': assemblyset['name'],
            'data': {
                'description': 'test assembly set',
                'items': assemblyset['items'],
            },
        })
        setattr(self, assemblyset['attr'], saved_assembly_set['set_ref'])
        print({
            'Saved AssemblySet': saved_assembly_set,
            assemblyset['attr']: getattr(self, assemblyset['attr']),
        })
        TEST_DATA['assemblyset_list'].append(assemblyset)

    def prep_assemblies(self):
        ''' prepare the assemblies and assembly set '''

        assembly_list = TEST_DATA['assembly_list'][3:]

        # just load the test assembly and the dodgy contig assembly
        for assembly in assembly_list:
            self._prep_assembly(assembly)

        assemblyset_list = [
            {   # assembly set composed of the two assemblies above
                'name': 'Test_Assembly_Set',
                'attr': 'assembly_set_ref',
                'items': [
                    {
                        'ref':   getattr(self, a['attr']),
                        'label': a['name'],
                    }
                    for a in assembly_list
                ],
            },
        ]

        for assemblyset in assemblyset_list:
            self._prep_assemblyset(assemblyset)

        return True

    def _prep_binned_contig(self, bc):

        if hasattr(self, bc['attr']):
            return

        binned_contigs_path = os.path.join(self.test_data_dir, bc['path'])
        if not os.path.exists(binned_contigs_path) or not os.path.exists(
            os.path.join(binned_contigs_path, 'bin.summary')
        ):
            shutil.rmtree(binned_contigs_path, ignore_errors=True)
            shutil.copytree(os.path.join("data", bc['path']), binned_contigs_path)

        saved_object = self.mu.file_to_binned_contigs({
            'file_directory': binned_contigs_path,
            'workspace_name': self.ws_info[1],
            'assembly_ref': getattr(self, bc['assembly']),
            'binned_contig_name': bc['name'],
        })

        setattr(self, bc['attr'], saved_object['binned_contig_obj_ref'])
        print({
            'Saved BinnedContigs': saved_object,
            bc['attr']: getattr(self, bc['attr'])
        })

    def prep_binned_contigs(self):

        # make sure we have assemblies loaded
        for assembly in TEST_DATA['assembly_list'][3:]:
            if not hasattr(self, assembly['attr']):
                self.prep_assemblies()
                break

        # some binned contigs
        binned_contigs_list = TEST_DATA['binned_contigs_list']
        for binned_contig in binned_contigs_list:
            self._prep_binned_contig(binned_contig)

        return True

    def _prep_genome(self, genome):

        if hasattr(self, genome['attr']):
            return

        genome_file_path = os.path.join(self.test_data_dir, genome['path'])
        if not os.path.exists(genome_file_path):
            shutil.copy(os.path.join("data", "genomes", genome['path']), genome_file_path)

        genome_data = self.gfu.genbank_to_genome({
            'file': {'path': genome_file_path},
            'workspace_name': self.ws_info[1],
            'genome_name': genome['name'],
            'generate_ids_if_needed': 1,
        })
        setattr(self, genome['attr'], genome_data['genome_ref'])
        print({
            'Saved Genome': genome_data,
            genome['attr']: getattr(self, genome['attr']),
        })

    def _prep_genomeset(self, genomeset):

        if hasattr(self, genomeset['attr']):
            return

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I,
         WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = list(range(11))  # object_info tuple

        obj_info = self.wsClient.save_objects({
            'workspace': self.ws_info[1],
            'objects': [{
                'type': 'KBaseSearch.GenomeSet',
                'data': {
                    'description': 'genomeSet for testing',
                    'elements': genomeset['items'],
                },
                'name': genomeset['name'],
                'meta': {},
                'provenance': [{
                    'service': 'kb_Msuite',
                    'method':  'test_CheckM'
                }]
            }]
        })[0]
        reference = "/".join([str(obj_info[prop]) for prop in [WSID_I, OBJID_I, VERSION_I]])

        setattr(self, genomeset['attr'], reference)
        print({
            'Saved Genomeset': obj_info,
            genomeset['attr']: getattr(self, genomeset['attr'])
        })

        TEST_DATA['genomeset_list'].append(genomeset)

    def prep_genomes(self):

        ''' add a couple of genomes and create a genome set '''

        genome_list = TEST_DATA['genome_list'][3:]

        # upload a few genomes
        for genome in genome_list:
            self._prep_genome(genome)

        genomeset_list = [
            {
                # create a genomeSet from the genome_list
                'name': 'Small_GenomeSet',
                'attr': 'genome_set_small_ref',
                'items': {
                    genome['name']: {
                        'ref': getattr(self, genome['attr'])
                    } for genome in genome_list
                },
            },
        ]

        for genomeset in genomeset_list:
            self._prep_genomeset(genomeset)

        return True

    def run_and_check_report(self, params, expected=None, with_filters=False):
        '''
        Run 'run_checkM_lineage_wf' with or without filters, and check the resultant KBaseReport
        using check_report()

        Args:

          params        - dictionary of input params
          expected      - dictionary representing the expected structure of the KBaseReport object
          with_filters  - whether or not to use the 'withFilter' version of the workflow

        '''

        if (with_filters):
            result = self.getImpl().run_checkM_lineage_wf_withFilter(self.getContext(), params)[0]
        else:
            result = self.getImpl().run_checkM_lineage_wf(self.getContext(), params)[0]

        return self.check_report(result, expected)

    def check_report(self, result, expected):
        '''
        Test utility to check a KBaseReport object
        Args:

          result    - result returned by running KBaseReport.get_extended_report
                      { 'report_name': blahblahblah, 'report_ref': reference }

          expected  - dictionary representing the expected structure of the report
                      any keys omitted from the dictionary are assumed to be the report default
                      (None or an empty list)
        '''
        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)

        # make sure the report was created and includes the HTML report and download links
        got_object = self.getWsClient().get_objects2({
            'objects': [{'ref': result['report_ref']}]
        })
        rep = got_object['data'][0]['data']
        print({'report data': rep})

        report_data = {
            'text_message': None,
            'file_links': [],
            'html_links': [],
            'warnings': [],
            'direct_html': None,
            'direct_html_link_index': None,
            'objects_created': [],
            'html_window_height': None,
            'summary_window_height': None,
        }
        report_data.update(expected)

        for key in expected.keys():
            with self.subTest('checking ' + key):
                if key == 'file_links' or key == 'html_links':
                    self.check_report_links(rep, key, report_data)
                elif key == 'objects_created' and expected['objects_created']:
                    # 'objects_created': [{'description': 'HQ BinnedContigs filter.BinnedContigs', 'ref': '50054/17/1'}]
                    self.assertTrue(len(rep['objects_created']) == 1)
                    obj = rep['objects_created'][0]
                    self.assertTrue(len(obj.keys()) == 2)
                    self.assertEqual(obj['description'], 'HQ BinnedContigs filter.BinnedContigs')
                    self.assertRegex(obj['ref'], r'\d+/\d+/\d+')
                else:
                    self.assertEqual(rep[key], report_data[key])

        return True

    def check_report_links(self, report_obj, type, expected):
        """
        Test utility: check the file upload results for an extended report
        Args:
          report_obj    - result dictionary from running KBaseReport.create_extended_report
          type          - one of "html_links" or "file_links"
          file_names    - names of the files for us to check against
        """
        file_links = report_obj[type]
        self.assertEqual(len(file_links), len(expected[type]))
        # Test that all the filenames listed in the report object map correctly
        saved_names = set([str(f['name']) for f in file_links])
        self.assertEqual(saved_names, set(expected[type]))
        return True

    def prepare_data(self):
        if not self.data_loaded:
            self.assertTrue(self.prep_binned_contigs())
            self.assertTrue(self.prep_genomes())
            self.data_loaded = True
        return True

    def test_00_prep_data(self):

        # prepare the test data
        self.assertTrue(self.prepare_data())

    # Test 1: single assembly
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_single_assembly")
    def test_checkM_lineage_wf_full_app_single_assembly(self):
        method_name = 'test_checkM_lineage_wf_full_app_single_assembly'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on a single assembly
        assembly = TEST_DATA['assembly_list'][3]

        input_ref = getattr(self, assembly['attr'])
        params = {
            'dir_name': assembly['attr'],
            'workspace_name': self.ws_info[1],
            'input_ref': input_ref,
            'reduced_tree': 0,
            'save_output_dir': 1,
            'save_plots_dir': 1,
            'threads': 4
        }
        expected_results = {
            'direct_html_link_index': 0,
            'file_links': ['CheckM_summary_table.tsv.zip', 'plots.zip', 'full_output.zip'],
            'html_links': [
                'CheckM_Plot.html'
            ],
        }
        self.run_and_check_report(params, expected_results)

    # Test 2: Regression test (CheckM <= v1.0.7) for single problem assembly
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_single_problem_assembly")
    def test_checkM_lineage_wf_full_app_single_problem_assembly(self):
        method_name = 'test_checkM_lineage_wf_full_app_single_problem_assembly'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on a single assembly
        # regression test for contig that breaks checkm v1.0.7 reduced_tree
        # (works on v1.0.8)
        # input_ref = self.assembly_offending_ref1
        assembly = TEST_DATA['assembly_list'][4]

        input_ref = getattr(self, assembly['attr'])
        params = {
            'dir_name': assembly['attr'],
            'workspace_name': self.ws_info[1],
            'input_ref': input_ref,
            'reduced_tree': 1,  # this must be 1 to regression test with --reduced_tree
            'save_output_dir': 1,
            'save_plots_dir': 1,
            'threads': 4
        }
        expected_results = {
            'direct_html_link_index': 0,
            'file_links': ['CheckM_summary_table.tsv.zip', 'plots.zip', 'full_output.zip'],
            'html_links': [
                'CheckM_Plot.html'
            ],
        }
        self.run_and_check_report(params, expected_results)

    # Test 3: binned contigs
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_binned_contigs")
    def test_checkM_lineage_wf_full_app_binned_contigs(self):
        method_name = 'test_checkM_lineage_wf_full_app_binned_contigs'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on BinnedContigs
        # Even with the reduced_tree option, this will take a long time and crash if your
        # machine has less than ~16gb memory
        # input_ref = self.binned_contigs_ref1
        binned_contigs = TEST_DATA['binned_contigs_list'][0]

        input_ref = getattr(self, binned_contigs['attr'])
        params = {
            'dir_name': binned_contigs['attr'],
            'workspace_name': self.ws_info[1],
            'input_ref': input_ref,
            'reduced_tree': 1,
            'save_output_dir': 1,
            'save_plots_dir': 1,
            'threads': 4
        }
        expected_results = {
            'direct_html_link_index': 0,
            'file_links': ['CheckM_summary_table.tsv.zip', 'plots.zip', 'full_output.zip'],
            'html_links': [
                'CheckM_Plot.html'
            ],
        }
        self.run_and_check_report(params, expected_results)

    # Test 4: Regression test for empty binned contigs object
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_binned_contigs_EMPTY")
    def test_checkM_lineage_wf_full_app_binned_contigs_EMPTY(self):
        method_name = 'test_checkM_lineage_wf_full_app_binned_contigs_EMPTY'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on EMPTY BinnedContigs
        # input_ref = self.binned_contigs_ref1_empty
        binned_contigs = TEST_DATA['binned_contigs_list'][1]

        input_ref = getattr(self, binned_contigs['attr'])
        params = {
            'dir_name': binned_contigs['attr'],
            'workspace_name': self.ws_info[1],
            'reduced_tree': 1,
            'input_ref': input_ref
        }
        with self.assertRaises(ValueError) as exception_context:
            self.getImpl().run_checkM_lineage_wf(self.getContext(), params)
        self.assertTrue('Binned Assembly is empty' in str(exception_context.exception))

    # Test 5: Assembly Set
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_assemblySet")
    def test_checkM_lineage_wf_full_app_assemblySet(self):
        method_name = 'test_checkM_lineage_wf_full_app_assemblySet'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on an assembly set
        # input_ref = self.assemblySet_ref1
        assemblyset = TEST_DATA['assemblyset_list'][0]

        input_ref = getattr(self, assemblyset['attr'])
        params = {
            'dir_name': assemblyset['attr'],
            'workspace_name': self.ws_info[1],
            'input_ref': input_ref,
            'reduced_tree': 1,
            'save_output_dir': 1,
            'save_plots_dir': 1,
            'threads': 4
        }
        expected_results = {
            'direct_html_link_index': 0,
            'file_links': ['CheckM_summary_table.tsv.zip', 'plots.zip', 'full_output.zip'],
            'html_links': [
                'CheckM_Plot.html'
            ],
        }
        self.run_and_check_report(params, expected_results)

    # Test 6: Single Genome
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_single_genome")
    def test_checkM_lineage_wf_full_app_single_genome(self):
        method_name = 'test_checkM_lineage_wf_full_app_single_genome'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on a single genome
        # input_ref = self.genome_refs[0]
        genome = TEST_DATA['genome_list'][3]

        input_ref = getattr(self, genome['attr'])
        params = {
            'dir_name': genome['attr'],
            'workspace_name': self.ws_info[1],
            'input_ref': input_ref,
            'reduced_tree': 1,
            'save_output_dir': 1,
            'save_plots_dir': 1,
            'threads': 4
        }
        expected_results = {
            'direct_html_link_index': 0,
            'file_links': ['CheckM_summary_table.tsv.zip', 'plots.zip', 'full_output.zip'],
            'html_links': [
                'CheckM_Plot.html'
            ],
        }
        self.run_and_check_report(params, expected_results)

    # Test 7: Genome Set
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_genomeSet")
    def test_checkM_lineage_wf_full_app_genomeSet(self):
        method_name = 'test_checkM_lineage_wf_full_app_genomeSet'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on a genome set
        # self.genomeSet_ref1
        genomeset = TEST_DATA['genomeset_list'][0]

        input_ref = getattr(self, genomeset['attr'])
        params = {
            'workspace_name': self.ws_info[1],
            'input_ref': input_ref,
            'reduced_tree': 1,
            'save_output_dir': 1,
            'save_plots_dir': 1,
            'threads': 4
        }
        expected_results = {
            'direct_html_link_index': 0,
            'file_links': ['CheckM_summary_table.tsv.zip', 'plots.zip', 'full_output.zip'],
            'html_links': [
                'CheckM_Plot.html'
            ],
        }
        self.run_and_check_report(params, expected_results)

    # Test 8: Data staging (intended data not checked into git repo: SKIP)
    #
    # Uncomment to skip this test
    # @unittest.skip("skipped test_data_staging")
    # missing test data for this custom test
    def test_data_staging(self):

        # test stage assembly
        dsu = DataStagingUtils(self.cfg, self.ctx)
        assembly = TEST_DATA['assembly_list'][3]
        staged_input = dsu.stage_input(getattr(self, assembly['attr']), 'strange_fasta_extension')
        pprint(staged_input)

        self.assertTrue(os.path.isdir(staged_input['input_dir']))
        self.assertTrue(os.path.isfile(staged_input['all_seq_fasta']))
        self.assertIn('folder_suffix', staged_input)

        self.assertTrue(os.path.isfile(os.path.join(staged_input['input_dir'],
                                                    assembly['name'] + '.strange_fasta_extension')))

        # test stage binned contigs
        bc = TEST_DATA['binned_contigs_list'][0]
        staged_input2 = dsu.stage_input(getattr(self, bc['attr']), 'fna')
        pprint(staged_input2)

        self.assertTrue(os.path.isdir(staged_input2['input_dir']))
        self.assertTrue(os.path.isfile(staged_input2['all_seq_fasta']))
        self.assertIn('folder_suffix', staged_input2)

        self.assertTrue(os.path.isfile(os.path.join(staged_input2['input_dir'],
                                                    'out_header.001.fna')))
        self.assertTrue(os.path.isfile(os.path.join(staged_input2['input_dir'],
                                                    'out_header.002.fna')))
        self.assertTrue(os.path.isfile(os.path.join(staged_input2['input_dir'],
                                                    'out_header.003.fna')))

    # Test 9: Plotting (intended data not checked into git repo: SKIP)
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_output_plotting")
    # missing test data for this custom test
    def test_output_plotting(self):

        cmu = CheckMUtil(self.cfg, self.ctx)
        plots_dir = os.path.join(self.scratch, 'plots_1')
        html_dir = os.path.join(self.scratch, 'html_1')
        tetra_file = os.path.join(self.scratch, 'tetra_1.tsv')

        cmu.build_checkM_lineage_wf_plots(self.input_dir, self.output_dir, plots_dir,
                                          self.all_seq_fasta, tetra_file)
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
        self.assertEqual(res['name'], 'CheckM_Plot.html')

    # Test 10: tetra wiring (intended data not checked into git repo: SKIP)
    #
    # Uncomment to skip this test
    @unittest.skip("skipped test_checkM_local_function_wiring")
    # missing test data for this custom test
    def test_checkM_local_function_wiring(self):

        # run checkM lineage_wf app on a single assembly
        tetra_file = os.path.join(self.scratch, 'tetra_test.tsv')
        params = {
            'subcommand': 'tetra',
            'seq_file': self.all_seq_fasta,
            'tetra_file': tetra_file,
        }
        self.getImpl().run_checkM(self.getContext(), params)
        os.path.isfile(tetra_file)

    # Test 11: filter binned contigs to HQ binned contigs
    #
    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_checkM_lineage_wf_full_app_filter_binned_contigs")
    def test_checkM_lineage_wf_withFilter_binned_contigs(self):
        method_name = 'test_checkM_lineage_wf_withFilter_binned_contigs'
        print ("\n=================================================================")
        print ("RUNNING "+method_name+"()")
        print ("=================================================================\n")

        # run checkM lineage_wf app on BinnedContigs, with filters!
        # Even with the reduced_tree option, this will take a long time and crash if your
        # machine has less than ~16gb memory
        binned_contigs = TEST_DATA['binned_contigs_list'][0]

        input_ref = getattr(self, binned_contigs['attr'])
        params = {
            'dir_name': 'binned_contigs_filter',
            'workspace_name': self.ws_info[1],
            'input_ref': input_ref,
            'reduced_tree': 1,
            'save_output_dir': 1,
            'save_plots_dir': 1,
            'completeness_perc': 95.0,
            'contamination_perc': 1.5,
            'output_filtered_binnedcontigs_obj_name': 'filter.BinnedContigs',
            'threads': 4
        }
        expected_results = {
            'direct_html_link_index': 0,
            'file_links': ['CheckM_summary_table.tsv.zip', 'plots.zip', 'full_output.zip'],
            'html_links': [
                'CheckM_Plot.html'
            ],
            'objects_created': 1,
        }
        self.run_and_check_report(params, expected_results, True)


    def setup_local_method_data(self):
        base_dir = os.path.dirname(__file__)
        test_data_dir = os.path.join(base_dir, 'data', 'example-bins')
        scratch_input_dir = os.path.join(self.scratch, 'lineage_wf_input_dir')
        scratch_output_dir = os.path.join(
            self.scratch, 'lineage_wf_output_dir' + '_' + str(self.suffix)
        )
        shutil.copytree(test_data_dir, scratch_input_dir)
        if not os.path.exists(scratch_output_dir):
            os.mkdir(scratch_output_dir)
        log_path = os.path.join(self.scratch, 'lineage_wf.log')
        return scratch_input_dir, scratch_output_dir, log_path

    # Uncomment to skip this test
    # HIDE @unittest.skip("skipped test_local_method()")
    def test_local_method(self):
        """
        Test a successful run of the .lineage_wf local method
        This just does some very basic testing to make sure the executable runs.
        """

        input_dir, output_dir, log_path = self.setup_local_method_data()
        self.getImpl().lineage_wf(self.getContext(), {
            'input_dir': input_dir,
            'output_dir': output_dir,
            'log_path': log_path,
            'options': {
                '-x': 'fasta',
                '--reduced_tree': ''
            }
        })
        out_contents = sorted(os.listdir(output_dir))
        # self.assertEqual(out_contents, ['storage', 'lineage.ms', 'bins'])
        self.assertEqual(out_contents, ['bins', 'checkm.log', 'lineage.ms', 'storage'])
        self.assertTrue(os.path.exists(log_path))
        # Remove test data
        os.remove(log_path)
        shutil.rmtree(input_dir)
        shutil.rmtree(output_dir)
