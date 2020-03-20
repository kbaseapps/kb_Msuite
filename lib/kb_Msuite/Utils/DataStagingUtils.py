import os
import time
import glob
import re
import subprocess

from installed_clients.WorkspaceClient import Workspace
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.SetAPIServiceClient import SetAPI
from installed_clients.MetagenomeUtilsClient import MetagenomeUtils


class DataStagingUtils(object):

    def __init__(self, config, ctx):
        self.ctx = ctx
        self.scratch = os.path.abspath(config['scratch'])
        self.ws_url = config['workspace-url']
        self.serviceWizardURL = config['srv-wiz-url']
        self.callbackURL = config['SDK_CALLBACK_URL']
        if not os.path.exists(self.scratch):
            os.makedirs(self.scratch)


    def stage_input(self, input_ref, fasta_file_extension):
        '''
        Stage input based on an input data reference for CheckM

        input_ref can be a reference to an Assembly, BinnedContigs, or (not yet implemented) a Genome

        This method creates a directory in the scratch area with the set of Fasta files, names
        will have the fasta_file_extension parameter tacked on.

            ex:

            staged_input = stage_input('124/15/1', 'fna')

            staged_input
            {"input_dir": '...'}
        '''
        # config
        #SERVICE_VER = 'dev'
        SERVICE_VER = 'release'
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        ws = Workspace(self.ws_url)

        # 1) generate a folder in scratch to hold the input
        suffix = str(int(time.time() * 1000))
        input_dir = os.path.join(self.scratch, 'bins_' + suffix)
        all_seq_fasta = os.path.join(self.scratch, 'all_sequences_' + suffix + '.' + fasta_file_extension)
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)


        # 2) based on type, download the files
        obj_name = self.get_data_obj_name (input_ref)
        type_name = self.get_data_obj_type (input_ref)

        # auClient
        try:
            auClient = AssemblyUtil(self.callbackURL, token=self.ctx['token'], service_ver=SERVICE_VER)
        except Exception as e:
            raise ValueError('Unable to instantiate auClient with callbackURL: '+ self.callbackURL +' ERROR: ' + str(e))

        # setAPI_Client
        try:
            #setAPI_Client = SetAPI (url=self.callbackURL, token=self.ctx['token'])  # for SDK local.  local doesn't work for SetAPI
            setAPI_Client = SetAPI (url=self.serviceWizardURL, token=self.ctx['token'])  # for dynamic service
        except Exception as e:
            raise ValueError('Unable to instantiate setAPI_Client with serviceWizardURL: '+ self.serviceWizardURL +' ERROR: ' + str(e))

        # mguClient
        try:
            mguClient = MetagenomeUtils(self.callbackURL, token=self.ctx['token'], service_ver=SERVICE_VER)
        except Exception as e:
            raise ValueError('Unable to instantiate mguClient with callbackURL: '+ self.callbackURL +' ERROR: ' + str(e))


        # Standard Single Assembly
        #
        if type_name in ['KBaseGenomeAnnotations.Assembly', 'KBaseGenomes.ContigSet']:
            # create file data
            filename = os.path.join(input_dir, obj_name + '.' + fasta_file_extension)
            auClient.get_assembly_as_fasta({'ref': input_ref, 'filename': filename})
            if not os.path.isfile(filename):
                raise ValueError('Error generating fasta file from an Assembly or ContigSet with AssemblyUtil')
            # make sure fasta file isn't empty
            min_fasta_len = 1
            if not self.fasta_seq_len_at_least(filename, min_fasta_len):
                raise ValueError('Assembly or ContigSet is empty in filename: '+str(filename))

        # AssemblySet
        #
        elif type_name == 'KBaseSets.AssemblySet':

            # read assemblySet
            try:
                assemblySet_obj = setAPI_Client.get_assembly_set_v1 ({'ref':input_ref, 'include_item_info':1})
            except Exception as e:
                raise ValueError('Unable to get object from workspace: (' + input_ref +')' + str(e))
            assembly_refs = []
            assembly_names = []
            for assembly_item in assemblySet_obj['data']['items']:
                this_assembly_ref = assembly_item['ref']
                # assembly obj info
                try:
                    this_assembly_info = ws.get_object_info_new ({'objects':[{'ref':this_assembly_ref}]})[0]
                    this_assembly_name = this_assembly_info[NAME_I]
                except Exception as e:
                    raise ValueError('Unable to get object from workspace: (' + this_assembly_ref +'): ' + str(e))
                assembly_refs.append(this_assembly_ref)
                assembly_names.append(this_assembly_name)

            # create file data (name for file is what's reported in results)
            for ass_i,assembly_ref in enumerate(assembly_refs):
                this_name = assembly_names[ass_i]
                filename = os.path.join(input_dir, this_name + '.' + fasta_file_extension)
                auClient.get_assembly_as_fasta({'ref': assembly_ref, 'filename': filename})
                if not os.path.isfile(filename):
                    raise ValueError('Error generating fasta file from an Assembly or ContigSet with AssemblyUtil')
                # make sure fasta file isn't empty
                min_fasta_len = 1
                if not self.fasta_seq_len_at_least(filename, min_fasta_len):
                    raise ValueError('Assembly or ContigSet is empty in filename: '+str(filename))

        # Binned Contigs
        #
        elif type_name == 'KBaseMetagenomes.BinnedContigs':

            # download the bins as fasta and set the input folder name
            bin_file_dir = mguClient.binned_contigs_to_file({'input_ref': input_ref, 'save_to_shock': 0})['bin_file_directory']
            os.rename(bin_file_dir, input_dir)
            # make sure fasta file isn't empty
            self.set_fasta_file_extensions(input_dir, fasta_file_extension)
            for (dirpath, dirnames, filenames) in os.walk(input_dir):
                for fasta_file in filenames:
                    fasta_path = os.path.join (input_dir,fasta_file)
                    min_fasta_len = 1
                    if not self.fasta_seq_len_at_least(fasta_path, min_fasta_len):
                        raise ValueError('Binned Assembly is empty for fasta_path: '+str(fasta_path))
                break

        # Genome and GenomeSet
        #
        elif type_name == 'KBaseGenomes.Genome' or type_name == 'KBaseSearch.GenomeSet':
            genome_obj_names = []
            genome_sci_names = []
            genome_assembly_refs = []

            if type_name == 'KBaseGenomes.Genome':
                genomeSet_refs = [input_ref]
            else:  # get genomeSet_refs from GenomeSet object
                genomeSet_refs = []
                try:
                    genomeSet_object = ws.get_objects2({'objects':[{'ref':input_ref}]})['data'][0]['data']
                except Exception as e:
                    raise ValueError('Unable to fetch '+str(input_ref)+' object from workspace: ' + str(e))
                    #to get the full stack trace: traceback.format_exc()

                # iterate through genomeSet members
                for genome_id in genomeSet_object['elements'].keys():
                    if 'ref' not in genomeSet_object['elements'][genome_id] or \
                       genomeSet_object['elements'][genome_id]['ref'] == None or \
                       genomeSet_object['elements'][genome_id]['ref'] == '':
                        raise ValueError('genome_ref not found for genome_id: '+str(genome_id)+' in genomeSet: '+str(input_ref))
                    else:
                        genomeSet_refs.append(genomeSet_object['elements'][genome_id]['ref'])

            # genome obj data
            for i,this_input_ref in enumerate(genomeSet_refs):
                try:
                    objects = ws.get_objects2({'objects':[{'ref':this_input_ref}]})['data']
                    genome_obj = objects[0]['data']
                    genome_obj_info = objects[0]['info']
                    genome_obj_names.append(genome_obj_info[NAME_I])
                    genome_sci_names.append(genome_obj['scientific_name'])
                except:
                    raise ValueError ("unable to fetch genome: "+this_input_ref)

                # Get genome_assembly_ref
                if ('contigset_ref' not in genome_obj or genome_obj['contigset_ref'] == None) \
                   and ('assembly_ref' not in genome_obj or genome_obj['assembly_ref'] == None):
                    msg = "Genome "+genome_obj_names[i]+" (ref:"+input_ref+") "+genome_sci_names[i]+" MISSING BOTH contigset_ref AND assembly_ref.  Cannot process.  Exiting."
                    raise ValueError (msg)
                    continue
                elif 'assembly_ref' in genome_obj and genome_obj['assembly_ref'] != None:
                    msg = "Genome "+genome_obj_names[i]+" (ref:"+input_ref+") "+genome_sci_names[i]+" USING assembly_ref: "+str(genome_obj['assembly_ref'])
                    print (msg)
                    genome_assembly_refs.append(genome_obj['assembly_ref'])
                elif 'contigset_ref' in genome_obj and genome_obj['contigset_ref'] != None:
                    msg = "Genome "+genome_obj_names[i]+" (ref:"+input_ref+") "+genome_sci_names[i]+" USING contigset_ref: "+str(genome_obj['contigset_ref'])
                    print (msg)
                    genome_assembly_refs.append(genome_obj['contigset_ref'])

            # create file data (name for file is what's reported in results)
            for ass_i,assembly_ref in enumerate(genome_assembly_refs):
                this_name = genome_obj_names[ass_i]
                filename = os.path.join(input_dir, this_name + '.' + fasta_file_extension)
                auClient.get_assembly_as_fasta({'ref': assembly_ref, 'filename': filename})
                if not os.path.isfile(filename):
                    raise ValueError('Error generating fasta file from an Assembly or ContigSet with AssemblyUtil')
                # make sure fasta file isn't empty
                min_fasta_len = 1
                if not self.fasta_seq_len_at_least(filename, min_fasta_len):
                    raise ValueError('Assembly or ContigSet is empty in filename: '+str(filename))

        # Unknown type slipped through
        #
        else:
            raise ValueError('Cannot stage fasta file input directory from type: ' + type_name)


        # create summary fasta file with all bins
        self.cat_fasta_files(input_dir, fasta_file_extension, all_seq_fasta)

        return {'input_dir': input_dir, 'folder_suffix': suffix, 'all_seq_fasta': all_seq_fasta}


    def fasta_seq_len_at_least(self, fasta_path, min_fasta_len=1):
        '''
        counts the number of non-header, non-whitespace characters in a FASTA file
        '''
        seq_len = 0
        with open (fasta_path, 'r') as fasta_handle:
            for line in fasta_handle:
                line = line.strip()
                if line.startswith('>'):
                    continue
                line = line.replace(' ','')
                seq_len += len(line)
                if seq_len >= min_fasta_len:
                    return True
        return False


    def set_fasta_file_extensions(self, folder, new_extension):
        '''
        Renames all detected fasta files in folder to the specified extension.
        fasta files are detected based on its existing extension, which must be one of:
            ['.fasta', '.fas', '.fa', '.fsa', '.seq', '.fna', '.ffn', '.faa', '.frn']

        Note that this is probably not well behaved if the operation will rename to a
        file that already exists
        '''
        extensions = ['.fasta', '.fas', '.fa', '.fsa', '.seq', '.fna', '.ffn', '.faa', '.frn']

        for file in os.listdir(folder):
            if not os.path.isfile(os.path.join(folder, file)):
                continue
            filename, file_extension = os.path.splitext(file)
            if file_extension in extensions:
                os.rename(os.path.join(folder, file),
                          os.path.join(folder, filename + '.' + new_extension))


    def cat_fasta_files(self, folder, extension, output_fasta_file):
        '''
        Given a folder of fasta files with the specified extension, cat them together
        using 'cat' into the target new_fasta_file
        '''
        files = glob.glob(os.path.join(folder, '*.' + extension))
        cat_cmd = ['cat'] + files
        fasta_file_handle = open(output_fasta_file, 'w')
        p = subprocess.Popen(cat_cmd, cwd=self.scratch, stdout=fasta_file_handle, shell=False)
        exitCode = p.wait()
        fasta_file_handle.close()

        if exitCode != 0:
            raise ValueError('Error running command: ' + ' '.join(cat_cmd) + '\n' +
                             'Exit Code: ' + str(exitCode))

    def get_bin_fasta_files(self, input_dir, fasta_extension):
        bin_fasta_files = dict()
        for (dirpath, dirnames, filenames) in os.walk(input_dir):
            # DEBUG
            #print ("DIRPATH: "+dirpath)
            #print ("DIRNAMES: "+", ".join(dirnames))
            #print ("FILENAMES: "+", ".join(filenames))
            for filename in filenames:
                if not os.path.isfile(os.path.join(input_dir, filename)):
                    continue
                if filename.endswith('.'+fasta_extension):
                    fasta_file = filename
                    bin_ID = re.sub('^[^\.]+\.', '', fasta_file.replace('.'+fasta_extension,''))
                    fasta_path = os.path.join (input_dir,fasta_file)
                    bin_fasta_files[bin_ID] = fasta_path
                    #bin_fasta_files[bin_ID] = fasta_file
                    #print ("ACCEPTED: "+bin_ID+" FILE:"+fasta_file)  # DEBUG

        return bin_fasta_files

    def get_data_obj_type_by_name(self, input_ref, remove_module=False):
        # 0 obj_id objid - the numerical id of the object.
        # 1 obj_name name - the name of the object.
        # 2 type_string type - the type of the object.
        # 3 timestamp save_date - the save date of the object.
        # 4 obj_ver ver - the version of the object.
        # 5 username saved_by - the user that saved or copied the object.
        # 6 ws_id wsid - the workspace containing the object.
        # 7 ws_name workspace - the workspace containing the object.
        # 8 string chsum - the md5 checksum of the object.
        # 9 int size - the size of the object in bytes.
        # 10 usermeta meta - arbitrary user-supplied metadata about
        #     the object.
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        ws = Workspace(self.ws_url)
        input_info = ws.get_object_info3({'objects': [{'ref': input_ref}]})['infos'][0]
        obj_name = input_info[NAME_I]
        type_name = input_info[TYPE_I].split('-')[0]
        if remove_module:
            type_name = type_name.split('.')[1]
        return { obj_name: type_name }

    def get_data_obj_name(self, input_ref):
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        ws = Workspace(self.ws_url)
        input_info = ws.get_object_info3({'objects': [{'ref': input_ref}]})['infos'][0]
        obj_name = input_info[NAME_I]
        #type_name = input_info[TYPE_I].split('-')[0]
        return obj_name

    def get_data_obj_type(self, input_ref, remove_module=False):
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        ws = Workspace(self.ws_url)
        input_info = ws.get_object_info3({'objects': [{'ref': input_ref}]})['infos'][0]
        #obj_name = input_info[NAME_I]
        type_name = input_info[TYPE_I].split('-')[0]
        if remove_module:
            type_name = type_name.split('.')[1]
        return type_name

    def read_assembly_ref_from_binnedcontigs(self, input_ref):
        ws = Workspace(self.ws_url)
        try:
            binned_contig_obj = ws.get_objects2({'objects':[{'ref':input_ref}]})['data'][0]['data']
        except Exception as e:
            raise ValueError('Unable to fetch '+str(input_ref)+' object from workspace: ' + str(e))
            #to get the full stack trace: traceback.format_exc()

        return binned_contig_obj['assembly_ref']

    def build_bin_summary_file_from_binnedcontigs_obj(self, input_ref, bin_dir, bin_basename, fasta_extension):

        # read bin info from obj
        ws = Workspace(self.ws_url)
        try:
            binned_contig_obj = ws.get_objects2({'objects':[{'ref':input_ref}]})['data'][0]['data']
        except Exception as e:
            raise ValueError('Unable to fetch '+str(input_ref)+' object from workspace: ' + str(e))
            #to get the full stack trace: traceback.format_exc()
        bin_summary_info = dict()

        # bid in object is full name of contig fasta file.  want just the number
        for bin_item in binned_contig_obj['bins']:
            #print ("BIN_ITEM[bid]: "+bin_item['bid'])  # DEBUG
            bin_ID = re.sub ('^[^\.]+\.', '', bin_item['bid'].replace('.'+fasta_extension,''))

            #print ("BIN_ID: "+bin_ID)  # DEBUG
            bin_summary_info[bin_ID] = { 'n_contigs': bin_item['n_contigs'],
                                         'gc': round (100.0 * float(bin_item['gc']), 1),
                                         'sum_contig_len': bin_item['sum_contig_len'],
                                         'cov': round (100.0 * float(bin_item['cov']), 1)
                                     }
        # write summary file for just those bins present in bin_dir
        header_line = ['Bin name', 'Completeness', 'Genome size', 'GC content']
        bin_fasta_files_by_bin_ID = self.get_bin_fasta_files(bin_dir, fasta_extension)
        bin_IDs = []
        for bin_ID in sorted(bin_fasta_files_by_bin_ID.keys()):
            bin_ID = re.sub('^[^\.]+\.', '', bin_ID.replace('.'+fasta_extension,''))
            bin_IDs.append(bin_ID)
        summary_file_path = os.path.join (bin_dir, bin_basename+'.'+'summary')

        print ("writing filtered binned contigs summary file "+summary_file_path)
        with open (summary_file_path, 'w') as summary_file_handle:
            print ("\t".join(header_line))
            summary_file_handle.write("\t".join(header_line)+"\n")
            for bin_ID in bin_IDs:
                #print ("EXAMINING BIN SUMMARY INFO FOR BIN_ID: "+bin_ID)  # DEBUG
                bin_summary_info_line = [ bin_basename+'.'+str(bin_ID)+'.'+fasta_extension,
                                          str(bin_summary_info[bin_ID]['cov'])+'%',
                                          str(bin_summary_info[bin_ID]['sum_contig_len']),
                                          str(bin_summary_info[bin_ID]['gc'])
                                      ]
                print ("\t".join(bin_summary_info_line))
                summary_file_handle.write("\t".join(bin_summary_info_line)+"\n")

        return summary_file_path
