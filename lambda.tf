resource "aws_lambda_function" "central_monitor" {
  function_name = "central-website-monitor"
  runtime       = "python3.10"
  handler       = "index.lambda_handler"
  role          = aws_iam_role.lambda_role.arn
  filename      = "lambda/lambda.zip"
  timeout       = 15

  source_code_hash = filebase64sha256("lambda/lambda.zip")

  depends_on = [
    aws_iam_role_policy_attachment.basic
  ]

  environment {
    variables = {
      BOT_TOKEN = "8410052282:AAFIEF_fywv2kfP5agjYOvGWPETB93RCJm8"
      CHAT_ID  = "1294991106"
    }
  }
}
