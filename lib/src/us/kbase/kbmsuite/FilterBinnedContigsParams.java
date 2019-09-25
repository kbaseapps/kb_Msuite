
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
 * <p>Original spec-file type: filter_binned_contigs_Params</p>
 * <pre>
 * filter_binned_contigs - grouped parameters to make new binned contig object with qual above thresholds
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "completenes_perc",
    "contamination_perc",
    "output_filtered_binnedcontigs_obj_name"
})
public class FilterBinnedContigsParams {

    @JsonProperty("completenes_perc")
    private Double completenesPerc;
    @JsonProperty("contamination_perc")
    private Double contaminationPerc;
    @JsonProperty("output_filtered_binnedcontigs_obj_name")
    private String outputFilteredBinnedcontigsObjName;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("completenes_perc")
    public Double getCompletenesPerc() {
        return completenesPerc;
    }

    @JsonProperty("completenes_perc")
    public void setCompletenesPerc(Double completenesPerc) {
        this.completenesPerc = completenesPerc;
    }

    public FilterBinnedContigsParams withCompletenesPerc(Double completenesPerc) {
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

    public FilterBinnedContigsParams withContaminationPerc(Double contaminationPerc) {
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

    public FilterBinnedContigsParams withOutputFilteredBinnedcontigsObjName(String outputFilteredBinnedcontigsObjName) {
        this.outputFilteredBinnedcontigsObjName = outputFilteredBinnedcontigsObjName;
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
        return ((((((((("FilterBinnedContigsParams"+" [completenesPerc=")+ completenesPerc)+", contaminationPerc=")+ contaminationPerc)+", outputFilteredBinnedcontigsObjName=")+ outputFilteredBinnedcontigsObjName)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
