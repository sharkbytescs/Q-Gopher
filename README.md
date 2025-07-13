# Q-Gopher Lambda

**Q-Gopher Lambda** is an AWS Lambda function that scrapes the latest quantum computing articles and writes them into a Gopher-compatible `gophermap` file. The file is then uploaded to an S3 bucket, where it can be served via a retro Gopher server.

## 🧠 Purpose

This Lambda automates the discovery and publication of quantum tech news from top academic and industry sources, enabling a modern-to-retro content pipeline.

## 📦 Features

- Scrapes articles from:
  - **MIT Quantum News**
  - **AWS Quantum Blog**
  - **ScienceDaily: Quantum Computing**
- Formats results as Gopher `i`-type menu items.
- Uploads the `gophermap` to a specified S3 bucket.

## ⚙️ How It Works

1. Lambda is triggered (e.g., on a schedule via **EventBridge**).
2. Scraping logic uses `requests` and `BeautifulSoup` to fetch article headlines.
3. Headlines are written into a `gophermap` file.
4. File is uploaded to a configured S3 bucket and key using `boto3`.

## 🚀 Deployment

### Prerequisites

- An S3 bucket (e.g., `q-gopher`)
- A Lambda IAM Role with the following permissions:
  - `s3:PutObject`
  - `logs:CreateLogGroup`
  - `logs:CreateLogStream`
  - `logs:PutLogEvents`

### Deploy with ZIP Upload

```bash
zip lambda.zip lambda_function.py
aws lambda update-function-code \
  --function-name q-gopher-fetcher \
  --zip-file fileb://lambda.zip
