#!/usr/bin/env python3
"""Run a Jupyter notebook headlessly and write the executed notebook.

Usage:
    python scripts/run_notebook.py --input notebooks/benin_eda.ipynb

This will create an executed notebook next to the input file with suffix `_executed`.
Requires: nbformat, nbconvert
"""
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Execute a Jupyter notebook headlessly')
    parser.add_argument('--input', '-i', required=True, help='Path to the input notebook (.ipynb)')
    parser.add_argument('--output', '-o', help='Path to write executed notebook (default: add _executed before .ipynb)')
    parser.add_argument('--timeout', '-t', type=int, default=600, help='Execution timeout per cell in seconds (default: 600)')
    parser.add_argument('--kernel', '-k', default='python3', help='Kernel name to use (default: python3)')
    args = parser.parse_args()

    nb_path = args.input
    if not os.path.exists(nb_path):
        print(f'ERROR: input notebook not found: {nb_path}', file=sys.stderr)
        return 2

    out_path = args.output
    if not out_path:
        base, ext = os.path.splitext(nb_path)
        out_path = f"{base}_executed{ext}"

    try:
        import nbformat
        from nbconvert.preprocessors import ExecutePreprocessor
    except Exception as e:
        print('Missing required packages: nbformat and nbconvert. Install with:', file=sys.stderr)
        print('  python -m pip install nbformat nbconvert', file=sys.stderr)
        return 3

    print(f'Executing notebook: {nb_path}\nWriting executed notebook to: {out_path}\nTimeout per cell: {args.timeout}s, Kernel: {args.kernel}')

    try:
        with open(nb_path, 'r', encoding='utf-8') as fh:
            nb = nbformat.read(fh, as_version=4)

        ep = ExecutePreprocessor(timeout=args.timeout, kernel_name=args.kernel)
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(nb_path) or '.'}})

        with open(out_path, 'w', encoding='utf-8') as fh:
            nbformat.write(nb, fh)

        print('Notebook executed successfully.')
        return 0
    except Exception as exc:
        print('ERROR during notebook execution:', file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 4

if __name__ == '__main__':
    sys.exit(main())
