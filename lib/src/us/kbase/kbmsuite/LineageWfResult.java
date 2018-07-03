
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
 * <p>Original spec-file type: LineageWfResult</p>
 * <pre>
 * *
 * * Output results of running the lineage_wf local method.
 * * We simply give the raw standard out from checkm, which may be an error message (checkm does
 * * not use stderr)
 * *
 * * Fields:
 * *   stdout - The standard out given by checkm after running.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "stdout"
})
public class LineageWfResult {

    @JsonProperty("stdout")
    private String stdout;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("stdout")
    public String getStdout() {
        return stdout;
    }

    @JsonProperty("stdout")
    public void setStdout(String stdout) {
        this.stdout = stdout;
    }

    public LineageWfResult withStdout(String stdout) {
        this.stdout = stdout;
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
        return ((((("LineageWfResult"+" [stdout=")+ stdout)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
