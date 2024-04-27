import argparse
import sys
import random
import string
import boto3
import os
import time
from tqdm import tqdm
from colorama import Fore, Style

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

        print(f"{Fore.RED}Minimum Upload Speed: {min_speed:.2f} MB/s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Maximum Upload Speed: {max_speed:.2f} MB/s{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Average Upload Speed: {avg_speed:.2f} MB/s{Style.RESET_ALL}")
        print(f"Total Uploads Recorded: {len(self.upload_times)}")

def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark for Filesystems and S3 Storage Write Performances")
    parser.add_argument("--s3", action="store_true", help="benchmark for S3 Storage")
    parser.add_argument("--fs", action="store_true", help="benchmark for local Filesystem (in progress)")
    parser.add_argument("--count", type=str, default="1", help="Count of Files to Write (e.g., '5')")
    parser.add_argument("--size", type=str, default="1M", help="Explicit Filesize in MB or GB (e.g., '100M')")
    parser.add_argument("--randmin", type=str, help="Minimum size of random file (e.g., '100M')")
    parser.add_argument("--randmax", type=str, help="Maximum size of random file (e.g., '1G')")

    # S3 Specific
    parser.add_argument("--access-key", required=True, help="AWS Access Key ID")
    parser.add_argument("--secret-key", required=True, help="AWS Secret Access Key")
    parser.add_argument("--endpoint", required=True, help="S3 endpoint URL")

    return parser.parse_args()

def parse_size(size_str):
    size_str = size_str.lower()
    if size_str.endswith("m"):
        return int(size_str[:-1]) * 1024 * 1024
    elif size_str.endswith("g"):
        return int(size_str[:-1]) * 1024 * 1024 * 1024
    else:
        print("Unsupported format. Use something like '100M' or '1G'.")
        sys.exit(1)

def generate_random_size(randmin_str, randmax_str):
    randmin = parse_size(randmin_str)
    randmax = parse_size(randmax_str)
    return random.randint(randmin, randmax)

def generate_random_string(length=5):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def upload_file(s3_client, bucket_name, file_path, file_size_mb):
    start_time = time.time()
    s3_client.upload_file(file_path, bucket_name, "benchmarkable")
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

    unique_suffix = generate_random_string(5)
    bucket_name = f"benchmarkable-bucket-{unique_suffix}"
    s3_client.create_bucket(Bucket=bucket_name)

    upload_stats = UploadStats()

    # Custom ASCII art and Design
    ascii_art = r"""
  ____                  _                          _         _     _      
 |  _ \                | |                        | |       | |   | |     
 | |_) | ___ _ __   ___| |__  _ __ ___   __ _ _ __| | ____ _| |__ | | ___ 
 |  _ < / _ \ '_ \ / __| '_ \| '_ ` _ \ / _` | '__| |/ / _` | '_ \| |/ _ \
 | |_) |  __/ | | | (__| | | | | | | | | (_| | |  |   < (_| | |_) | |  __/
 |____/ \___|_| |_|\___|_| |_|_| |_| |_|\__,_|_|  |_|\_\__,_|_.__/|_|\___|
                                                                          
    """
    print(ascii_art)
    print(f"by TorbenThorsten")
    print(f"\n\nBenchmark running on bucket {Fore.CYAN}{bucket_name}{Style.RESET_ALL}")

    with tqdm(total=int(args.count), desc="Benchmarking") as pbar:
        for _ in range(int(args.count)):
            if args.randmin is not None and args.randmax is not None:
                size_in_bytes = generate_random_size(args.randmin, args.randmax)
            else:
                size_in_bytes = parse_size(args.size)

            test_file_path = "benchmarkable"
            create_file(test_file_path, size_in_bytes)

            upload_time, upload_speed_mb_s = upload_file(s3_client, bucket_name, test_file_path, size_in_bytes / (1024 * 1024))
            upload_stats.record_upload(upload_time, size_in_bytes / (1024 * 1024))

            delete_file(s3_client, bucket_name, "benchmarkable")
            os.remove(test_file_path)

            pbar.update(1)  # Increment progress bar by 1 for each upload

    s3_client.delete_bucket(Bucket=bucket_name)

    print("\nBenchmark Summary:")
    upload_stats.print_summary()

if __name__ == "__main__":
    main()
