variable "name" {
  description = "Name to be used on all the resources as identifier."
}

variable "description" {
  default     = ""
  description = "Description of what your Lambda Function does."
}

variable "handler" {
  description = "The function entrypoint in your code. "
}

variable "runtime" {
  description = "The function runtime to use. (nodejs, nodejs4.3, nodejs6.10, nodejs8.10, java8, python2.7, python3.6, dotnetcore1.0, dotnetcore2.0, dotnetcore2.1, nodejs4.3-edge, go1.x)"
}

variable "role" {
  default     = ""
  description = "This governs both who / what can invoke your Lambda Function, as well as what resources our Lambda Function has access to. See Lambda Permission Model for more details."
}

variable "role_name" {
  default     = ""
  description = "The name of the IAM role which will be created for the Lambda Function."
}

variable "policy" {
  default     = ""
  description = "IAM policy attached to the Lambda Function role."
}

variable "policy_arn" {
  default     = ""
  description = "The Amazon Resource Name (ARN) identifying your IAM policy attached to the Lambda Function role."
}

variable "tags" {
  default     = {}
  description = "A mapping of tags to assign to the object."
}

variable "package_path" {
  description = "The path to the function's deployment package within the local filesystem."
}

variable "package_include_paths" {
  default     = []
  description = "Additional files and directories which should be part of of the package .zip file within the local filesystem."
}

