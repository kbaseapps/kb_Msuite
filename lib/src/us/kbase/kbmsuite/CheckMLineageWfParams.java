
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
 * <p>Original spec-file type: CheckMLineageWfParams</p>
 * <pre>
 * input_ref - reference to the input Assembly, AssemblySet, Genome, GenomeSet, or BinnedContigs data
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "input_ref",
    "workspace_name",
    "reduced_tree",
    "save_output_dir",
    "save_plots_dir",
    "filter_params",
    "threads"
})
public class CheckMLineageWfParams {

    @JsonProperty("input_ref")
    private String inputRef;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("reduced_tree")
    private Long reducedTree;
    @JsonProperty("save_output_dir")
    private Long saveOutputDir;
    @JsonProperty("save_plots_dir")
    private Long savePlotsDir;
    /**
     * <p>Original spec-file type: filter_binned_contigs_Params</p>
     * <pre>
     * filter_binned_contigs - grouped parameters to make new binned contig object with qual above thresholds
     * </pre>
     * 
     */
    @JsonProperty("filter_params")
    private FilterBinnedContigsParams filterParams;
    @JsonProperty("threads")
    private Long threads;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("input_ref")
    public String getInputRef() {
        return inputRef;
    }

    @JsonProperty("input_ref")
    public void setInputRef(String inputRef) {
        this.inputRef = inputRef;
    }

    public CheckMLineageWfParams withInputRef(String inputRef) {
        this.inputRef = inputRef;
        return this;
    }

    @JsonProperty("workspace_name")
    public String getWorkspaceName() {
        return workspaceName;
    }

    @JsonProperty("workspace_name")
    public void setWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
    }

    public CheckMLineageWfParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
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

    public CheckMLineageWfParams withReducedTree(Long reducedTree) {
        this.reducedTree = reducedTree;
        return this;
    }

    @JsonProperty("save_output_dir")
    public Long getSaveOutputDir() {
        return saveOutputDir;
    }

    @JsonProperty("save_output_dir")
    public void setSaveOutputDir(Long saveOutputDir) {
        this.saveOutputDir = saveOutputDir;
    }

    public CheckMLineageWfParams withSaveOutputDir(Long saveOutputDir) {
        this.saveOutputDir = saveOutputDir;
        return this;
    }

    @JsonProperty("save_plots_dir")
    public Long getSavePlotsDir() {
        return savePlotsDir;
    }

    @JsonProperty("save_plots_dir")
    public void setSavePlotsDir(Long savePlotsDir) {
        this.savePlotsDir = savePlotsDir;
    }

    public CheckMLineageWfParams withSavePlotsDir(Long savePlotsDir) {
        this.savePlotsDir = savePlotsDir;
        return this;
    }

    /**
     * <p>Original spec-file type: filter_binned_contigs_Params</p>
     * <pre>
     * filter_binned_contigs - grouped parameters to make new binned contig object with qual above thresholds
     * </pre>
     * 
     */
    @JsonProperty("filter_params")
    public FilterBinnedContigsParams getFilterParams() {
        return filterParams;
    }

    /**
     * <p>Original spec-file type: filter_binned_contigs_Params</p>
     * <pre>
     * filter_binned_contigs - grouped parameters to make new binned contig object with qual above thresholds
     * </pre>
     * 
     */
    @JsonProperty("filter_params")
    public void setFilterParams(FilterBinnedContigsParams filterParams) {
        this.filterParams = filterParams;
    }

    public CheckMLineageWfParams withFilterParams(FilterBinnedContigsParams filterParams) {
        this.filterParams = filterParams;
        return this;
    }

    @JsonProperty("threads")
    public Long getThreads() {
        return threads;
    }

    @JsonProperty("threads")
    public void setThreads(Long threads) {
        this.threads = threads;
    }

    public CheckMLineageWfParams withThreads(Long threads) {
        this.threads = threads;
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
        return ((((((((((((((((("CheckMLineageWfParams"+" [inputRef=")+ inputRef)+", workspaceName=")+ workspaceName)+", reducedTree=")+ reducedTree)+", saveOutputDir=")+ saveOutputDir)+", savePlotsDir=")+ savePlotsDir)+", filterParams=")+ filterParams)+", threads=")+ threads)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
