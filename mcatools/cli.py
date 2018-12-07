import click

from mcatools.biome import extract_region_biomes
from mcatools.fileutils import save_biome_image_rgb, extract_region, readfile


@click.group()
def main():
    pass


@click.command()
@click.argument("fromregion")
@click.argument("toimage")
def export_biome(fromregion, toimage):
    click.echo(f"Loading region data from: {fromregion}")
    filedata = readfile(fromregion)
    region = extract_region(filedata)
    biome_data = extract_region_biomes(region)
    save_biome_image_rgb(biome_data, toimage)
    click.echo(f"Biome data saved to: {toimage}")


main.add_command(export_biome)
