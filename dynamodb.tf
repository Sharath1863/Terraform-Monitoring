resource "aws_dynamodb_table" "website_monitor_state" {
  name         = "website-monitor-state"
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "monitor_id"

  attribute {
    name = "monitor_id"
    type = "S"
  }

  tags = {
    Name    = "website-monitor-state"
    Purpose = "lambda-state-memory"
  }
}
