import click

from mcatools.fileutils import save_biome_image_rgb, extract_region, readfile


@click.group()
def main():
    pass


@click.command()
@click.argument("region_filename")
@click.argument("image_filename")
def export_biome(region_filename, image_filename):
    click.echo(f"Loading region data from: {region_filename}")
    filedata = readfile(region_filename)
    region = extract_region(filedata)
    biome_data = region.get_biomes()
    save_biome_image_rgb(biome_data, image_filename)
    click.echo(f"Biome data saved to: {image_filename}")


main.add_command(export_biome)
