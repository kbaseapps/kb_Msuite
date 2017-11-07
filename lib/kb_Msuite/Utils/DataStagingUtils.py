import os
import time
import glob
import subprocess

from Workspace.WorkspaceClient import Workspace
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from MetagenomeUtils.MetagenomeUtilsClient import MetagenomeUtils


class DataStagingUtils(object):

    def __init__(self, config):
        self.scratch = os.path.abspath(config['scratch'])
        self.ws_url = config['workspace-url']
        self.callback_url = config['SDK_CALLBACK_URL']


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
        # generate a folder in scratch to hold the input
        suffix = str(int(time.time() * 1000))
        input_dir = os.path.join(self.scratch, 'bins_' + suffix)
        all_seq_fasta = os.path.join(self.scratch, 'all_sequences_' + suffix + '.' + fasta_file_extension)


        # 2) based on type, download the files
        ws = Workspace(self.ws_url)
        input_info = ws.get_object_info3({'objects': [{'ref': input_ref}]})['infos'][0]
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
        obj_name = input_info[1]
        type_name = input_info[2].split('-')[0]

        # Standard Single Assembly
        if type_name in ['KBaseGenomeAnnotations.Assembly', 'KBaseGenomes.ContigSet']:
            au = AssemblyUtil(self.callback_url)
            os.makedirs(input_dir)
            filename = os.path.join(input_dir, obj_name + '.' + fasta_file_extension)
            au.get_assembly_as_fasta({'ref': input_ref, 'filename': filename})
            if not os.path.isfile(filename):
                raise ValueError('Error generating fasta file from an Assembly or ContigSet with AssemblyUtil')
            # make sure fasta file isn't empty
            if self.count_fasta_seq_len(filename) == 0:
                raise ValueError('Assembly or ContigSet is empty in filename: '+str(filename))
            pass

        # AssemblySet
        elif type_name == 'KBaseSets.AssemblySet':
            raise ValueError('Cannot yet stage fasta file input directory from KBaseSets.AssemblySet')

        # Binned Contigs
        elif type_name == 'KBaseMetagenomes.BinnedContigs':
            # download the bins as fasta and set the input folder name
            au = MetagenomeUtils(self.callback_url)
            bin_file_dir = au.binned_contigs_to_file({'input_ref': input_ref, 'save_to_shock': 0})['bin_file_directory']
            os.rename(bin_file_dir, input_dir)
            # make sure fasta file isn't empty
            self.set_fasta_file_extensions(input_dir, fasta_file_extension)
            for (dirpath, dirnames, filenames) in os.walk(input_dir):
                for fasta_file in filenames:
                    fasta_path = os.path.join (input_dir,fasta_file)
                    if self.count_fasta_seq_len(fasta_path) == 0:
                        raise ValueError('Binned Assembly is empty for fasta_path: '+str(fasta_path))
                break

        # Genome
        elif type_name == 'KBaseGenomes.Genome':
            raise ValueError('Cannot yet stage fasta file input directory from KBaseGenomes.Genome')

        # GenomeSet
        elif type_name == 'KBaseSearch.GenomeSet':
            raise ValueError('Cannot yet stage fasta file input directory from KBaseSearch.GenomeSet')

        else:
            raise ValueError('Cannot stage fasta file input directory from type: ' + type_name)


        # create summary fasta file with all bins
        self.cat_fasta_files(input_dir, fasta_file_extension, all_seq_fasta)

        return {'input_dir': input_dir, 'folder_suffix': suffix, 'all_seq_fasta': all_seq_fasta}


    def count_fasta_seq_len(self, fasta_path):
        '''
        counts the number of non-header, non-whitespace characters in a FASTA file
        '''
        seq_len = 0
        with open (fasta_path, 'r', 0) as fasta_handle:
            for line in fasta_handle:
                line = line.strip()
                if line.startswith('>'):
                    continue
                line = line.replace(' ','')
                seq_len += len(line)
        return seq_len


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
