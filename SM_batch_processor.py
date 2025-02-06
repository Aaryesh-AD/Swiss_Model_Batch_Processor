#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import gzip
import shutil
import argparse
import requests
import time
import re
import concurrent.futures
import threading
import json

# Determine the correct path for config.json
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # When running as an .exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # When running as a script

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")

with open(CONFIG_FILE) as f:
    config = json.load(f)

API_KEY = config.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is missing in config.json.")


with open("config.json") as f:
    config = json.load(f)

API_KEY = config.get("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY is missing. Set it in config.json.")

print(f"API Key loaded: {API_KEY}")


class SwissModelAPI:
    """Class for handling SwissModel API interactions with parallel execution support."""

    RAPID_RATE_LIMIT = 100  # Max 100 requests per minute
    REQUEST_INTERVAL = 60  # Wait 1 minute between requests

    def __init__(self, token, fasta_path, template_path, out_dir):
        self.token = token
        self.headers = {"Authorization": f"Token {self.token}"}
        self.fasta_path = fasta_path
        self.template_path = template_path
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        self.sequences = self._load_fasta_sequences()
        self.template_coordinates = self._load_template()
        self.lock = threading.Lock()  # Lock to prevent race conditions

    def _load_fasta_sequences(self):
        """Reads and cleans a FASTA file to extract valid sequences."""
        valid_chars = re.compile(r"[^A-Za-z?-]")
        sequences = {}

        with open(self.fasta_path, "r") as file:
            seq_id = None
            for line in file:
                line = line.strip()
                if line.startswith(">"):
                    seq_id = line[1:]
                    sequences[seq_id] = ""
                elif seq_id:
                    sequences[seq_id] += re.sub(valid_chars, "", line)

        return sequences  # Dictionary: {sequence_id: sequence}

    def _load_template(self):
        """Reads the template PDB file."""
        with open(self.template_path, "r") as file:
            return file.read()

    def submit_request(self, seq_id, sequence):
        """Submits a sequence to SwissModel API with retry handling."""
        attempt = 1
        while attempt <= 5:
            try:
                response = requests.post(
                    "https://swissmodel.expasy.org/user_template",
                    headers=self.headers,
                    json={"target_sequences": [sequence], "template_coordinates": self.template_coordinates, "project_title": f"Batch Submission - {seq_id}"},
                )
                
                if response.status_code == 429:  # Rate limit hit
                    wait_time = attempt * 10
                    print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    attempt += 1
                    continue

                response.raise_for_status()
                return seq_id, response.json().get("project_id")

            except requests.RequestException as e:
                print(f"Request error for {seq_id}: {e}")
                return seq_id, None

    def monitor_job_status(self, seq_id, project_id):
        """Monitors SwissModel job status until completion."""
        while True:
            time.sleep(10)  # Reduce server polling frequency
            try:
                status_response = requests.get(
                    f"https://swissmodel.expasy.org/project/{project_id}/models/summary/",
                    headers=self.headers,
                )
                status_response.raise_for_status()
                status_json = status_response.json()
                status = status_json.get("status", "UNKNOWN")
                print(f"Job {project_id} for {seq_id} status: {status}")
                if status in ["COMPLETED", "FAILED"]:
                    return status_json if status == "COMPLETED" else None
            except requests.RequestException:
                print(f"Error fetching job status for {project_id}. Retrying...")

    def fetch_model_results(self, seq_id, status_json):
        """Fetches and saves URLs of generated models."""
        model_data = []
        for i, model in enumerate(status_json.get("models", []), start=1):
            if "modelcif_url" in model:
                model_data.append((seq_id, model["modelcif_url"], i, "modelcif"))
            if "coordinates_url" in model:
                model_data.append((seq_id, model["coordinates_url"], i, "coordinates"))

        if not model_data:
            print(f"No models were generated for {seq_id}. Skipping download.")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self._download_and_extract, model_data)


    def sanitize_filename(self, filename):
        """Removes invalid characters for PyMOL compatibility."""
        return re.sub(r'[^A-Za-z0-9_.-]', '_', filename)

    def _download_and_extract(self, model_data):
        """Downloads and extracts gzipped model files with proper naming."""
        seq_id, url, model_number, file_type = model_data  # Include file_type for unique naming
        raw_filename = url.split("/")[-1]

        # Extract cluster number from the sequence ID (e.g., "cluster_3_medoid")
        cluster_match = re.search(r'cluster_(\d+)', seq_id)
        cluster_number = cluster_match.group(1) if cluster_match else "unknown"

        # Determine the subdirectory based on file type
        if file_type == "modelcif":
            sub_folder = "CIF"
            file_extension = ".cif"
        else:  # file_type == "coordinates"
            sub_folder = "PDB"
            file_extension = ".pdb"

        # Assign correct cluster subdirectory
        cluster_folder = os.path.join(self.out_dir, f"cluster_{cluster_number}_model", sub_folder)
        os.makedirs(cluster_folder, exist_ok=True)  # Ensure subdirectory exists

        # Generate unique filenames with type differentiation
        safe_filename = self.sanitize_filename(f"cluster_{cluster_number}_model_{model_number:03}{file_extension}")
        filename = os.path.join(cluster_folder, safe_filename)

        with self.lock:  # Prevent race conditions
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(filename, "wb") as file:
                    file.write(response.content)

                if filename.endswith(".gz"):
                    extracted_filename = filename.replace(".gz", "")
                    with gzip.open(filename, 'rb') as f_in, open(extracted_filename, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                    os.remove(filename)
                    print(f"Extracted {extracted_filename}")
                else:
                    print(f"Saved {filename}")

            except requests.RequestException as e:
                print(f"Failed to download {url}: {e}")




    def process_sequences(self):
        """Main function to process and submit sequences."""
        if not self.sequences:
            raise ValueError("No valid sequences found in the FASTA file.")
        print(f"Loaded {len(self.sequences)} valid sequences.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_seq = {executor.submit(self.submit_request, seq_id, seq): seq_id for seq_id, seq in self.sequences.items()}
            
            for future in concurrent.futures.as_completed(future_to_seq):
                seq_id, project_id = future.result()
                if project_id:
                    print(f"Project {project_id} for {seq_id} started successfully.")
                    status_json = self.monitor_job_status(seq_id, project_id)
                    if status_json:
                        self.fetch_model_results(seq_id, status_json)

        print("All sequences processed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Submit sequences to SwissModel API.")
    parser.add_argument("fasta_path", type=str, help="Path to input FASTA file.")
    parser.add_argument("template_path", type=str, help="Path to input template PDB file.")
    parser.add_argument("out_dir", type=str, help="Directory to save model outputs.")
    args = parser.parse_args()

    TOKEN = API_KEY  # Replace with your actual token

    swiss_model = SwissModelAPI(TOKEN, args.fasta_path, args.template_path, args.out_dir)
    swiss_model.process_sequences()


if __name__ == "__main__":
    main()
