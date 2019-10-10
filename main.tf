module "package" {
  source = "./modules/package"

  name          = var.name
  path          = var.package_path
  include_paths = [var.package_include_paths]
}

module "function" {
  source = "./modules/function"

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

