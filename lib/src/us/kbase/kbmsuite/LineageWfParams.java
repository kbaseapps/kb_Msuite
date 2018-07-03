
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
 * <p>Original spec-file type: LineageWfParams</p>
 * <pre>
 * *
 * * Parameters for lineage_wf, which runs as a "local method".
 * *
 * * Required arguments:
 * *   bin_dir - required - Path to the directory where your bins are located
 * *   out_dir - required - Path to a directory where we will write output files
 * *   options - optional - A mapping of options to pass to lineage_wf. See the README.md
 * *     in the kb_Msuite repo for a list of all of these. For options that have no value, simply
 * *     pass an empty string.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "bin_dir",
    "out_dir",
    "options"
})
public class LineageWfParams {

    @JsonProperty("bin_dir")
    private java.lang.String binDir;
    @JsonProperty("out_dir")
    private java.lang.String outDir;
    @JsonProperty("options")
    private Map<String, String> options;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("bin_dir")
    public java.lang.String getBinDir() {
        return binDir;
    }

    @JsonProperty("bin_dir")
    public void setBinDir(java.lang.String binDir) {
        this.binDir = binDir;
    }

    public LineageWfParams withBinDir(java.lang.String binDir) {
        this.binDir = binDir;
        return this;
    }

    @JsonProperty("out_dir")
    public java.lang.String getOutDir() {
        return outDir;
    }

    @JsonProperty("out_dir")
    public void setOutDir(java.lang.String outDir) {
        this.outDir = outDir;
    }

    public LineageWfParams withOutDir(java.lang.String outDir) {
        this.outDir = outDir;
        return this;
    }

    @JsonProperty("options")
    public Map<String, String> getOptions() {
        return options;
    }

    @JsonProperty("options")
    public void setOptions(Map<String, String> options) {
        this.options = options;
    }

    public LineageWfParams withOptions(Map<String, String> options) {
        this.options = options;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((("LineageWfParams"+" [binDir=")+ binDir)+", outDir=")+ outDir)+", options=")+ options)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
