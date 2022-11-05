import csv
import subprocess
import click
import pathlib

@click.command()
@click.argument('final-dir', type=click.Path(file_okay=False, resolve_path=True, path_type=pathlib.Path))
def add_to_ipfs(final_dir):
    # Load the metadata CSV file
    metadata_file_path = final_dir.joinpath('metadata.csv')
    with open(metadata_file_path) as csvfile:
        try:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            names = [name for name, _, _, _, _, _, _, _, _ in reader]
        except ValueError:
            raise click.ClickException(f'Invalid CSV file: {metadata_file_path}')
    
    result_file_path=final_dir.joinpath('ipfs.csv')
    with open(result_file_path, 'w') as fp:
        fp.write(f'Name,IPFS Hash\n')
        for name in names:
            image_path = final_dir.joinpath(f'{name}.png')

            print(f'Adding {image_path} to IPFS...')
            completed_process = subprocess.run(
                args=['/usr/local/bin/ipfs', 'add', image_path], capture_output=True, check=True)
            output = completed_process.stdout.decode()
            ipfs_hash = output.split()[1]
            fp.write(f'{name},{ipfs_hash}\n')
