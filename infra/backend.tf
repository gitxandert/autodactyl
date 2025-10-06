terraform {
  backend "s3" {
    bucket          = "autodactyl-terraform-state"
    key             = REDACTED
    region          = "us-east-2"
    use_lockfile    = true
    encrypt         = true
    profile         = REDACTED
  }
}
