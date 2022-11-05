import click

from .content import generate_content
from .ipfs import add_to_ipfs


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None, '-v', '--version')
def cli():
    pass


cli.add_command(generate_content.generate_content)
cli.add_command(add_to_ipfs.add_to_ipfs)
