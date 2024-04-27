# Benchmarkable

This is a command-line benchmarking tool for testing file uploads to an S3-compatible object storage service (e.g., Ceph RGW, Minio etc.) using Python. The tool supports benchmarking the upload speed for a specified number of file uploads to an S3 bucket.

## Requirements

- Python 3.x
- Boto3 library (`pip install boto3`)
- tqdm (`pip install boto3`)

## Installation

1. Clone the repository:

    <code>git clone https://github.com/TorbenThorsten/Benchmarkable </code>

# S3 Usage

## Command-line Arguments

The script supports the following command-line arguments:

    --s3: Enable benchmarking for S3 storage (required).
    --count <N>: Number of file uploads to perform (default: 1).
    --size <SIZE>: Size of the test file to upload (e.g., "1M", "100M", "1G").
    --randmin <SIZE>: minimum size of the test file to upload (e.g., "1M", "100M", "1G").
    --randmax <SIZE>: maximum size of the test file to upload (e.g., "1M", "100M", "1G").
    --access-key <ACCESS_KEY>: AWS Access Key ID (required for S3 access).
    --secret-key <SECRET_KEY>: AWS Secret Access Key (required for S3 access).
    --endpoint <ENDPOINT>: Custom S3 endpoint URL (e.g., "https://s3.amazonaws.com").

## Example Usage

### Benchmark S3 upload speed for 5 file uploads of size 100 MB:

<code>python Benchmarkable.py --s3 --count 5 --size 100M --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --endpoint YOUR_S3_ENDPOINT_URL</code>

### Benchmark S3 upload speed for 10 file uploads of random sizes between 1 and 50 MB:

<code>python Benchmarkable.py --s3 --randmin 1M --randmax 50M --size 100M --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --endpoint YOUR_S3_ENDPOINT_URL</code>

### Notes: 

Replace YOUR_ACCESS_KEY, YOUR_SECRET_KEY, and YOUR_S3_ENDPOINT_URL with your actual AWS credentials and S3 endpoint URL.
The benchmark tool creates a temporary S3 bucket named "benchmarkable-bucket" for testing purposes and deletes it after benchmarking.