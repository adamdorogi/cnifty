import csv
import subprocess
import click
import pathlib

# create mint tx

@click.command()
@click.argument('final-dir', type=click.Path(file_okay=False, resolve_path=True, path_type=pathlib.Path))
def run_sale(final_dir):
    print("Running sale")