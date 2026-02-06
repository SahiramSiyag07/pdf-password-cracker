import argparse
import os
import queue
import string
import threading
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

import pikepdf
from tqdm import tqdm

def read_wordlist(file_path):
    """Read passwords from a wordlist file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Wordlist file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading wordlist: {e}")

def generate_passwords(charset, min_len, max_len):
    """Generate passwords for brute-force attacks."""
    for length in range(min_len, max_len + 1):
        for pwd_tuple in itertools.product(charset, repeat=length):
            yield ''.join(pwd_tuple)

def try_password(pdf_path, password):
    """Attempt to open the PDF with the given password."""
    try:
        with pikepdf.open(pdf_path, password=password):
            return password
    except pikepdf.PasswordError:
        return None
    except Exception as e:
        return None

def main():
    parser = argparse.ArgumentParser(description='PDF Password Cracker')
    parser.add_argument('pdf_file', help='Path to the PDF file')
    parser.add_argument('--wordlist', help='Path to wordlist file for dictionary attack')
    parser.add_argument('--brute', action='store_true', help='Use brute-force mode')
    parser.add_argument('--charset', default=string.ascii_letters + string.digits, help='Charset for brute-force (default: letters + digits)')
    parser.add_argument('--min_len', type=int, default=1, help='Minimum password length for brute-force (default: 1)')
    parser.add_argument('--max_len', type=int, default=8, help='Maximum password length for brute-force (default: 8)')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads (default: 4)')

    args = parser.parse_args()

    # Error handling for missing files
    if not os.path.exists(args.pdf_file):
        print(f"Error: PDF file not found: {args.pdf_file}")
        return

    if args.wordlist and not os.path.exists(args.wordlist):
        print(f"Error: Wordlist file not found: {args.wordlist}")
        return

    if not args.wordlist and not args.brute:
        print("Error: Specify --wordlist for dictionary attack or --brute for brute-force attack")
        return

    # Check if PDF is encrypted
    try:
        with pikepdf.open(args.pdf_file):
            print("PDF is not encrypted. No password needed.")
            return
    except pikepdf.PasswordError:
        pass  # PDF is encrypted, proceed
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return

    # Determine mode
    mode = 'wordlist' if args.wordlist else 'brute'

    found_password = None

    if mode == 'wordlist':
        try:
            passwords = read_wordlist(args.wordlist)
        except Exception as e:
            print(f"Error: {e}")
            return

        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {executor.submit(try_password, args.pdf_file, pwd): pwd for pwd in passwords}
            for future in tqdm(as_completed(futures), total=len(passwords), desc="Testing passwords"):
                result = future.result()
                if result:
                    found_password = result
                    executor.shutdown(wait=False)
                    break

    elif mode == 'brute':
        print("Starting brute-force attack...")
        attempt_count = 0
        with tqdm(desc="Brute-forcing", unit="attempts") as pbar:
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = {}
                for pwd in generate_passwords(args.charset, args.min_len, args.max_len):
                    if found_password:
                        break
                    future = executor.submit(try_password, args.pdf_file, pwd)
                    futures[future] = pwd
                    attempt_count += 1
                    pbar.update(1)
                    # To avoid memory issues, process in batches
                    if len(futures) >= 10000:
                        for f in as_completed(futures):
                            result = f.result()
                            if result:
                                found_password = result
                                pbar.close()
                                executor.shutdown(wait=False)
                                break
                        futures = {}
                        if found_password:
                            break
                # Process remaining futures
                for f in as_completed(futures):
                    result = f.result()
                    if result:
                        found_password = result
                        pbar.close()
                        executor.shutdown(wait=False)
                        break

    if found_password:
        print(f"Password found: {found_password}")
    else:
        print("Password not found")

if __name__ == '__main__':
    main()
