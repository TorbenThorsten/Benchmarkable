import argparse
import sys
import boto3
import os
import time
from tqdm import tqdm

class UploadStats:
    def __init__(self):
        self.upload_times = []
        self.upload_speeds = []

    def record_upload(self, upload_time, file_size_mb):
        self.upload_times.append(upload_time)
        upload_speed_mb_s = file_size_mb / upload_time
        self.upload_speeds.append(upload_speed_mb_s)

    def print_summary(self):
        if not self.upload_times:
            print("No uploads recorded.")
            return

        min_speed = min(self.upload_speeds)
        max_speed = max(self.upload_speeds)
        avg_speed = sum(self.upload_speeds) / len(self.upload_speeds)

        print(f"Minimum Upload Speed: {min_speed:.2f} MB/s")
        print(f"Maximum Upload Speed: {max_speed:.2f} MB/s")
        print(f"Average Upload Speed: {avg_speed:.2f} MB/s")
        print(f"Total Uploads Recorded: {len(self.upload_times)}")

def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark-Programm für Dateisysteme und S3-Speicher")
    parser.add_argument("--s3", action="store_true", help="Benchmark für S3-Speicher")
    parser.add_argument("--fs", action="store_true", help="Benchmark für Dateisystem")
    parser.add_argument("--read", action="store_true", help="Random Read-Modus")
    parser.add_argument("--write", action="store_true", help="Random Write-Modus")
    parser.add_argument("--count", type=int, default=1, help="Anzahl der Uploads")
    parser.add_argument("--size", type=str, default="1M", help="Dateigröße in KB")

    # S3 Specific
    parser.add_argument("--access-key", required=True, help="AWS Access Key ID")
    parser.add_argument("--secret-key", required=True, help="AWS Secret Access Key")
    parser.add_argument("--endpoint", required=True, help="Custom S3 endpoint URL")

    return parser.parse_args()

def parse_size(size_str):
    size_str = size_str.lower()
    if size_str.endswith("m"):
        return int(size_str[:-1]) * 1024 * 1024
    elif size_str.endswith("g"):
        return int(size_str[:-1]) * 1024 * 1024 * 1024
    else:
        print("Ungültiges Format für die Dateigröße. Verwenden Sie z. B. 20M oder 20G.")
        sys.exit(1)

def upload_file(s3_client, bucket_name, file_path, file_size_mb):
    start_time = time.time()
    s3_client.upload_file(file_path, bucket_name, "testfile.bin")
    end_time = time.time()
    upload_time = end_time - start_time
    upload_speed_mb_s = file_size_mb / upload_time
    return upload_time, upload_speed_mb_s

def create_file(file_path, size):
    with open(file_path, "wb") as f:
        f.write(os.urandom(size))

def delete_file(s3_client, bucket_name, file_key):
    s3_client.delete_object(Bucket=bucket_name, Key=file_key)

def main():
    args = parse_args()

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=args.access_key,
        aws_secret_access_key=args.secret_key,
        endpoint_url=args.endpoint
    )

    bucket_name = "benchmarkable-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    size_in_bytes = parse_size(args.size)
    test_file_path = "testfile.bin"
    create_file(test_file_path, size_in_bytes)

    upload_stats = UploadStats()

    with tqdm(total=args.count, desc="Benchmarking") as pbar:
        for _ in range(args.count):
            upload_time, upload_speed_mb_s = upload_file(s3_client, bucket_name, test_file_path, size_in_bytes / (1024 * 1024))
            upload_stats.record_upload(upload_time, size_in_bytes / (1024 * 1024))
            pbar.update(1)  # Increment progress bar by 1 for each upload

    delete_file(s3_client, bucket_name, "testfile.bin")
    os.remove(test_file_path)

    s3_client.delete_bucket(Bucket=bucket_name)

    print("\nBenchmark Summary:")
    upload_stats.print_summary()

if __name__ == "__main__":
    main()
