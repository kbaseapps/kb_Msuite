
package us.kbase.kbmsuite;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: CheckMInputParams</p>
 * <pre>
 * Runs CheckM as a command line local function.
 * subcommand - specify the subcommand to run; supported options are lineage_wf, tetra, bin_qa_plot, dist_plot
 * bin_folder - folder with fasta files representing each contig (must end in .fna)
 * out_folder - folder to store output
 * plots_folder - folder to save plots to
 * seq_file - the full concatenated FASTA file (must end in .fna) of all contigs in your bins, used
 *            just for running the tetra command
 * tetra_File - specify the output/input tetra nucleotide frequency file (generated with the tetra command)
 * dist_value - when running dist_plot, set this to a value between 0 and 100
 * thread -  number of threads
 * reduced_tree - if set to 1, run checkM with the reduced_tree flag, which will keep memory limited to less than 16gb
 * quiet - pass the --quite parameter to checkM, but doesn't seem to work for all subcommands
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "subcommand",
    "bin_folder",
    "out_folder",
    "plots_folder",
    "seq_file",
    "tetra_file",
    "dist_value",
    "thread",
    "reduced_tree",
    "quiet"
})
public class CheckMInputParams {

    @JsonProperty("subcommand")
    private String subcommand;
    @JsonProperty("bin_folder")
    private String binFolder;
    @JsonProperty("out_folder")
    private String outFolder;
    @JsonProperty("plots_folder")
    private String plotsFolder;
    @JsonProperty("seq_file")
    private String seqFile;
    @JsonProperty("tetra_file")
    private String tetraFile;
    @JsonProperty("dist_value")
    private Long distValue;
    @JsonProperty("thread")
    private Long thread;
    @JsonProperty("reduced_tree")
    private Long reducedTree;
    @JsonProperty("quiet")
    private Long quiet;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("subcommand")
    public String getSubcommand() {
        return subcommand;
    }

    @JsonProperty("subcommand")
    public void setSubcommand(String subcommand) {
        this.subcommand = subcommand;
    }

    public CheckMInputParams withSubcommand(String subcommand) {
        this.subcommand = subcommand;
        return this;
    }

    @JsonProperty("bin_folder")
    public String getBinFolder() {
        return binFolder;
    }

    @JsonProperty("bin_folder")
    public void setBinFolder(String binFolder) {
        this.binFolder = binFolder;
    }

    public CheckMInputParams withBinFolder(String binFolder) {
        this.binFolder = binFolder;
        return this;
    }

    @JsonProperty("out_folder")
    public String getOutFolder() {
        return outFolder;
    }

    @JsonProperty("out_folder")
    public void setOutFolder(String outFolder) {
        this.outFolder = outFolder;
    }

    public CheckMInputParams withOutFolder(String outFolder) {
        this.outFolder = outFolder;
        return this;
    }

    @JsonProperty("plots_folder")
    public String getPlotsFolder() {
        return plotsFolder;
    }

    @JsonProperty("plots_folder")
    public void setPlotsFolder(String plotsFolder) {
        this.plotsFolder = plotsFolder;
    }

    public CheckMInputParams withPlotsFolder(String plotsFolder) {
        this.plotsFolder = plotsFolder;
        return this;
    }

    @JsonProperty("seq_file")
    public String getSeqFile() {
        return seqFile;
    }

    @JsonProperty("seq_file")
    public void setSeqFile(String seqFile) {
        this.seqFile = seqFile;
    }

    public CheckMInputParams withSeqFile(String seqFile) {
        this.seqFile = seqFile;
        return this;
    }

    @JsonProperty("tetra_file")
    public String getTetraFile() {
        return tetraFile;
    }

    @JsonProperty("tetra_file")
    public void setTetraFile(String tetraFile) {
        this.tetraFile = tetraFile;
    }

    public CheckMInputParams withTetraFile(String tetraFile) {
        this.tetraFile = tetraFile;
        return this;
    }

    @JsonProperty("dist_value")
    public Long getDistValue() {
        return distValue;
    }

    @JsonProperty("dist_value")
    public void setDistValue(Long distValue) {
        this.distValue = distValue;
    }

    public CheckMInputParams withDistValue(Long distValue) {
        this.distValue = distValue;
        return this;
    }

    @JsonProperty("thread")
    public Long getThread() {
        return thread;
    }

    @JsonProperty("thread")
    public void setThread(Long thread) {
        this.thread = thread;
    }

    public CheckMInputParams withThread(Long thread) {
        this.thread = thread;
        return this;
    }

    @JsonProperty("reduced_tree")
    public Long getReducedTree() {
        return reducedTree;
    }

    @JsonProperty("reduced_tree")
    public void setReducedTree(Long reducedTree) {
        this.reducedTree = reducedTree;
    }

    public CheckMInputParams withReducedTree(Long reducedTree) {
        this.reducedTree = reducedTree;
        return this;
    }

    @JsonProperty("quiet")
    public Long getQuiet() {
        return quiet;
    }

    @JsonProperty("quiet")
    public void setQuiet(Long quiet) {
        this.quiet = quiet;
    }

    public CheckMInputParams withQuiet(Long quiet) {
        this.quiet = quiet;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((((((((((((((("CheckMInputParams"+" [subcommand=")+ subcommand)+", binFolder=")+ binFolder)+", outFolder=")+ outFolder)+", plotsFolder=")+ plotsFolder)+", seqFile=")+ seqFile)+", tetraFile=")+ tetraFile)+", distValue=")+ distValue)+", thread=")+ thread)+", reducedTree=")+ reducedTree)+", quiet=")+ quiet)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
