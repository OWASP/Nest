variable "common_tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "model_name" {
  description = "Approved Bedrock foundation model or inference profile ID."
  type        = string

  validation {
    condition     = trimspace(var.model_name) != ""
    error_message = "model_name must not be empty."
  }
}

variable "name_prefix" {
  description = "Name prefix for the Bedrock invocation policy."
  type        = string
}

variable "target_type" {
  description = "Type of the approved Bedrock target: foundation-model or inference-profile."
  type        = string
  default     = "foundation-model"

  validation {
    condition     = contains(["foundation-model", "inference-profile"], var.target_type)
    error_message = "target_type must be foundation-model or inference-profile."
  }
}
