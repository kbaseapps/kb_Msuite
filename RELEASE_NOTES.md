### Version 1.4.1
__Changes__
- changed defaults in Filter App to Completeness 90% / Contamination 5%
- fixed unit tests which were failing on assembly copy
- added Github Actions unit testing

### Version 1.4.0
__Changes__
- updated kbase module paths in lib to installed_clients
- updated CheckM to v1.0.18
- updated KBase Docker base image to sdkbase2:python and added Cython lib fix
- added App that filters BinnedContigs by Completeness / Contamination
- split Plot and Table HTML reports into separate pages
- indicate in Table HTML report which bins were filtered out by QC
- added TSV summary table for download
- set thread count explicitly to 4

### Version 1.3.1
__Changes__
- changed citation format to PLOS

### Version 1.2.2
__Changes__
- Added Genome and GenomeSet input types

### Version 1.2.1
__Changes__
- Added choice to use reduced or full Reference Tree to input widget
- Changed and save_all_plots input widgets from checkbox to dropdown
- Removed save_all_plots option and made that default behavior
- Added AssemblySet input type

### Version 1.2.0
__Changes__
- Updated CheckM to v1.0.8 which fixes failure with --reduced_tree for certain ribosomal proteins

### Version 1.1.2
__Changes__
- Fix infinite recursion in output folder compression
- Fix running on empty FASTA

### Version 1.0.0
- Initial release
