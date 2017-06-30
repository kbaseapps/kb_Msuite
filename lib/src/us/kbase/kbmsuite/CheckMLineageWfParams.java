
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
 * input_ref - reference to the input Assembly or BinnedContigs data
 *             (could be expanded to include Genome objects as well)
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "input_ref",
    "workspace_name",
    "save_output_dir",
    "save_plots_dir"
})
public class CheckMLineageWfParams {

    @JsonProperty("input_ref")
    private String inputRef;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("save_output_dir")
    private Long saveOutputDir;
    @JsonProperty("save_plots_dir")
    private Long savePlotsDir;
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
        return ((((((((((("CheckMLineageWfParams"+" [inputRef=")+ inputRef)+", workspaceName=")+ workspaceName)+", saveOutputDir=")+ saveOutputDir)+", savePlotsDir=")+ savePlotsDir)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
