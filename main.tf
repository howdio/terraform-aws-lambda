module "package" {
  # TF-UPGRADE-TODO: In Terraform v0.11 and earlier, it was possible to
  # reference a relative module source without a preceding ./, but it is no
  # longer supported in Terraform v0.12.
  #
  # If the below module source is indeed a relative local path, add ./ to the
  # start of the source string. If that is not the case, then leave it as-is
  # and remove this TODO comment.
  source = "modules/package"

  name          = var.name
  path          = var.package_path
  include_paths = [var.package_include_paths]
}

module "function" {
  # TF-UPGRADE-TODO: In Terraform v0.11 and earlier, it was possible to
  # reference a relative module source without a preceding ./, but it is no
  # longer supported in Terraform v0.12.
  #
  # If the below module source is indeed a relative local path, add ./ to the
  # start of the source string. If that is not the case, then leave it as-is
  # and remove this TODO comment.
  source = "modules/function"

  name        = var.name
  description = var.description
  handler     = var.handler
  runtime     = var.runtime

  role       = var.role
  role_name  = var.role_name
  policy     = var.policy
  policy_arn = var.policy_arn

  package_path = module.package.path
  package_hash = module.package.base64sha256

  tags = var.tags
}

