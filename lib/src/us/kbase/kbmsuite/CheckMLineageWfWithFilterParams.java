
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
 * <p>Original spec-file type: CheckMLineageWf_withFilter_Params</p>
 * <pre>
 * input_ref - reference to the input BinnedContigs data
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
    "completenes_perc",
    "contamination_perc",
    "output_filtered_binnedcontigs_obj_name",
    "threads"
})
public class CheckMLineageWfWithFilterParams {

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
    @JsonProperty("completenes_perc")
    private Double completenesPerc;
    @JsonProperty("contamination_perc")
    private Double contaminationPerc;
    @JsonProperty("output_filtered_binnedcontigs_obj_name")
    private String outputFilteredBinnedcontigsObjName;
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

    public CheckMLineageWfWithFilterParams withInputRef(String inputRef) {
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

    public CheckMLineageWfWithFilterParams withWorkspaceName(String workspaceName) {
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

    public CheckMLineageWfWithFilterParams withReducedTree(Long reducedTree) {
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

    public CheckMLineageWfWithFilterParams withSaveOutputDir(Long saveOutputDir) {
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

    public CheckMLineageWfWithFilterParams withSavePlotsDir(Long savePlotsDir) {
        this.savePlotsDir = savePlotsDir;
        return this;
    }

    @JsonProperty("completenes_perc")
    public Double getCompletenesPerc() {
        return completenesPerc;
    }

    @JsonProperty("completenes_perc")
    public void setCompletenesPerc(Double completenesPerc) {
        this.completenesPerc = completenesPerc;
    }

    public CheckMLineageWfWithFilterParams withCompletenesPerc(Double completenesPerc) {
        this.completenesPerc = completenesPerc;
        return this;
    }

    @JsonProperty("contamination_perc")
    public Double getContaminationPerc() {
        return contaminationPerc;
    }

    @JsonProperty("contamination_perc")
    public void setContaminationPerc(Double contaminationPerc) {
        this.contaminationPerc = contaminationPerc;
    }

    public CheckMLineageWfWithFilterParams withContaminationPerc(Double contaminationPerc) {
        this.contaminationPerc = contaminationPerc;
        return this;
    }

    @JsonProperty("output_filtered_binnedcontigs_obj_name")
    public String getOutputFilteredBinnedcontigsObjName() {
        return outputFilteredBinnedcontigsObjName;
    }

    @JsonProperty("output_filtered_binnedcontigs_obj_name")
    public void setOutputFilteredBinnedcontigsObjName(String outputFilteredBinnedcontigsObjName) {
        this.outputFilteredBinnedcontigsObjName = outputFilteredBinnedcontigsObjName;
    }

    public CheckMLineageWfWithFilterParams withOutputFilteredBinnedcontigsObjName(String outputFilteredBinnedcontigsObjName) {
        this.outputFilteredBinnedcontigsObjName = outputFilteredBinnedcontigsObjName;
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

    public CheckMLineageWfWithFilterParams withThreads(Long threads) {
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
        return ((((((((((((((((((((("CheckMLineageWfWithFilterParams"+" [inputRef=")+ inputRef)+", workspaceName=")+ workspaceName)+", reducedTree=")+ reducedTree)+", saveOutputDir=")+ saveOutputDir)+", savePlotsDir=")+ savePlotsDir)+", completenesPerc=")+ completenesPerc)+", contaminationPerc=")+ contaminationPerc)+", outputFilteredBinnedcontigsObjName=")+ outputFilteredBinnedcontigsObjName)+", threads=")+ threads)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
