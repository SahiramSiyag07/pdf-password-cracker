# PDF Cracker

A Python script to crack password-protected PDF files using dictionary attacks or brute-force methods.

## Requirements

- Python 3.x
- pikepdf
- tqdm

Install dependencies:

```bash
pip install pikepdf tqdm
```

## Usage

### Dictionary Attack

Use a wordlist file to test passwords:

```bash
python pdf_cracker.py path/to/encrypted.pdf --wordlist path/to/wordlist.txt
```

### Brute-Force Attack

Generate and test passwords based on charset and length:

```bash
python pdf_cracker.py path/to/encrypted.pdf --brute --charset abcdefghijklmnopqrstuvwxyz0123456789 --min_len 1 --max_len 8 --threads 8
```

### Options

- `pdf_file`: Path to the PDF file (required)
- `--wordlist`: Path to wordlist file for dictionary attack
- `--brute`: Enable brute-force mode
- `--charset`: Charset for brute-force (default: letters + digits)
- `--min_len`: Minimum password length for brute-force (default: 1)
- `--max_len`: Maximum password length for brute-force (default: 8)
- `--threads`: Number of threads (default: 4)

## Features

- Command-line interface with argparse
- Dictionary attack using wordlist
- Brute-force attack with customizable charset and length
- Multi-threading for faster cracking
- Progress bar with tqdm
- Error handling for missing files and invalid inputs

## Example

```bash
python pdf_cracker.py encrypted.pdf --wordlist rockyou.txt --threads 8
```

If the password is found, it will display: `Password found: <password>`

If not found: `Password not found`

## Wordlist

A large wordlist file `large_wordlist.txt` is included, containing over 10 million generated passwords (all combinations of lowercase letters of length 5).
