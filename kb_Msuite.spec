/*
A KBase module: kb_Msuite
This SDK module is developed to wrap the open source package CheckM which consists of a set of tools
for assessing the quality of genomes recovered from isolates, single cells, or metagenomes.
CheckM consists of a series of commands in order to support a number of different analyses and workflows.

References:
CheckM in github: http://ecogenomics.github.io/CheckM/
CheckM docs: https://github.com/Ecogenomics/CheckM/wiki

Parks DH, Imelfort M, Skennerton CT, Hugenholtz P, Tyson GW. 2015. CheckM: assessing the quality of microbial genomes recovered from isolates, single cells, and metagenomes. Genome Research, 25: 1043–1055.
*/

module kb_Msuite {
    /*
    A boolean - 0 for false, 1 for true.
        @range (0, 1)
    */
    typedef int boolean;

    typedef string FASTA_format; /*".fna"*/

    /*
        Runs CheckM as a command line local function.

        subcommand - specify the subcommand to run; supported options are lineage_wf, tetra, bin_qa_plot, dist_plot

        bin_folder - folder with fasta files representing each contig (must end in .fna)
        out_folder - folder to store output
        plots_folder - folder to save plots to

        seq_file - the full concatenated FASTA file (must end in .fna) of all contigs in your bins, used
                   just for running the tetra command
        tetra_File - specify the output/input tetra nucleotide frequency file (generated with the tetra command)

        dist_value - when running dist_plot, set this to a value between 0 and 100

        thread -  number of threads
        reduced_tree - if set to 1, run checkM with the reduced_tree flag, which will keep memory limited to less than 16gb (otherwise needs 40+ GB, which NJS worker nodes do have)
        quiet - pass the --quite parameter to checkM, but doesn't seem to work for all subcommands
    */
    typedef structure {
        string subcommand;

        string bin_folder;
        string out_folder;
        string plots_folder;

        string seq_file;
        string tetra_file;

        int dist_value;

        int thread;
        boolean reduced_tree;
        boolean quiet;
    } CheckMInputParams;



    funcdef run_checkM(CheckMInputParams params)
        returns () authentication required;



    /*
        input_ref - reference to the input Assembly, AssemblySet, Genome, GenomeSet, or BinnedContigs data
    */
    typedef structure {
        string input_ref;
        string workspace_name;

        boolean reduced_tree;
        boolean save_output_dir;
        boolean save_plots_dir;
    } CheckMLineageWfParams;

    typedef structure {
        string report_name;
        string report_ref;
    } CheckMLineageWfResult;

    funcdef run_checkM_lineage_wf(CheckMLineageWfParams params)
        returns (CheckMLineageWfResult result) authentication required;


    /**
     * Parameters for lineage_wf, which runs as a "local method".
     *
     * Required arguments:
     *   bin_dir - required - Path to the directory where your bins are located
     *   out_dir - required - Path to a directory where we will write output files
     *   log_path - required - Path to a file that will be written to with all log output from
     *     stdout and stderr while running `checkm lineage_wf`.
     *   options - optional - A mapping of options to pass to lineage_wf. See the README.md
     *     in the kb_Msuite repo for a list of all of these. For options that have no value, simply
     *     pass an empty string.
     */
    typedef structure {
      string bin_dir;
      string out_dir;
      string log_path;
      mapping <string, string> options;
    } LineageWfParams;

    /**
     * Output results of running the lineage_wf local method.
     * This returns nothing. Check the contents of log_path and out_dir which were passed as
     * parameters to see the output of running this function.
     */
    typedef structure {
    } LineageWfResult;


    /**
     * A "local method" for calling lineage_wf directly.
     */
    funcdef lineage_wf(LineageWfParams params)
        returns (LineageWfResult result) authentication required;


};
