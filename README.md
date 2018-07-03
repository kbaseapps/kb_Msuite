
# kb_Msuite
---

A [KBase](https://kbase.us) module that wraps CheckM (http://ecogenomics.github.io/CheckM/)

Nice TODO:
 - expose reduced_tree option as advanced parameter?
 - advanced parameter for also creating EPS or other plots
 - advanced parameters for adjusting the plots
 - advanced parameter for setting the dist_value for bin plots


## Local method with kb_Msuite.lineage_wf

You can run checkm's lineage_wf as a local (direct) method from another app:

In the shell:

```sh
kb-sdk install kb_Msuite
```

In python:

```py
from kb_Msuite.kb_MsuiteClient import kb_Msuite

checkm = kb_Msuite(callback_url)

checkm.lineage_wf({
  'input_dir': os.path.join(self.scratch, 'input_bins'),
  'output_dir: os.path.join(self.scratch, 'output_data'),
  'log_file': os.path.join(self.scratch, 'lineage_wf.log'),
  'options': {
    '-x': 'fasta'
  }
})
```

The parameters to this method are:

* `input_dir` - required - Directory of the input bins
* `output_dir` - required - Directory to save the output
* `log_path` - required - File path of the log file to save all the output from running checkm
* `options` - optional - A dictionary of flags and options to run

`options` is a dictionary of flags that correspond to the flags from `checkm lineage_wf`:

```
optional arguments:
  -h, --help            show this help message and exit
  -r, --reduced_tree    use reduced tree (requires <16GB of memory) for determining lineage of each bin
  --ali                 generate HMMER alignment file for each bin
  --nt                  generate nucleotide gene sequences for each bin
  -g, --genes           bins contain genes as amino acids instead of nucleotide contigs
  -u, --unique UNIQUE   minimum number of unique phylogenetic markers required to use lineage-specific marker set (default: 10)
  -m, --multi MULTI     maximum number of multi-copy phylogenetic markers before defaulting to domain-level marker set (default: 10)
  --force_domain        use domain-level sets for all bins
  --no_refinement       do not perform lineage-specific marker set refinement
  --individual_markers  treat marker as independent (i.e., ignore co-located set structure)
  --skip_adj_correction
                        do not exclude adjacent marker genes when estimating contamination
  --skip_pseudogene_correction
                        skip identification and filtering of pseudogenes
  --aai_strain AAI_STRAIN
                        AAI threshold used to identify strain heterogeneity (default: 0.9)
  -a, --alignment_file ALIGNMENT_FILE
                        produce file showing alignment of multi-copy genes and their AAI identity
  --ignore_thresholds   ignore model-specific score thresholds
  -e, --e_value E_VALUE
                        e-value cut off (default: 1e-10)
  -l, --length LENGTH   percent overlap between target and query (default: 0.7)
  -f, --file FILE       print results to file (default: stdout)
  --tab_table           print tab-separated values table
  -x, --extension EXTENSION
                        extension of bins (other files in folder are ignored) (default: fna)
  -t, --threads THREADS
                        number of threads (default: 1)
  --pplacer_threads PPLACER_THREADS
                        number of threads used by pplacer (memory usage increases linearly with additional threads) (default: 1)
  -q, --quiet           suppress console output
  --tmpdir TMPDIR       specify an alternative directory for temporary files
```

For any options that have a value, set the value in the dictionary. For any flags that do not take
values, set an empty string in the dictionary.

For example, if you want to run a command like:

```sh
checkm lineage_wf input_dir output_dir -x fasta --reduced_tree
```

Then you would call the method like this:

```py
checkm.lineage_wf({
  'input_dir': input_dir,
  'output_dir': output_dir,
  'log_file': log_file_path,
  options: {
    '-x': 'fasta',
    '--reduced_tree': ''
  }
})
```

Notice that we have set the `--reduced_tree` option to an empty string as it takes no value.
