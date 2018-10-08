variable "name" {
  default     = ""
  description = "The name of the package .zip file when no path is specified. The path will result in ./.terraform/$(name).zip."
}

variable "path" {
  default     = ""
  description = "The file or directory which should be part of of the package .zip file within the local filesystem."
}

variable "include_paths" {
  default     = []
  description = "Additional files and directories which should be part of of the package .zip file within the local filesystem."
}

variable "output_path" {
  default     = ""
  description = "The path of the package .zip file within the local filesystem."
}
