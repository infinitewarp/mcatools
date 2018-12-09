import shutil
import time

import click

from mcatools.imageutils import save_biome_image_rgb, load_biome_image_rgb
from mcatools.region import Region


@click.group()
def main():
    pass


@click.command()
@click.argument("region_filename")
@click.argument("image_filename")
def export_biome(region_filename, image_filename):
    click.echo(f"Loading region data from: {region_filename}")
    region = Region.load(region_filename)
    biome_data = region.get_biomes()
    save_biome_image_rgb(biome_data, image_filename)
    click.echo(f"Biome data saved to: {image_filename}")


@click.command()
@click.argument("region_filename")
@click.argument("image_filename")
def import_biome(region_filename, image_filename):
    click.echo(f"Loading region data from: {region_filename}")
    region = Region.load(region_filename)
    biome_data = load_biome_image_rgb(image_filename)
    region.set_biomes(biome_data)
    region_filename_backup = f"{region_filename}-{time.time()}"
    click.echo(f"Backing up {region_filename} to {region_filename_backup}")
    shutil.copy2(region_filename, region_filename_backup)
    region.save(region_filename)
    click.echo(f"Biome data saved to region: {region_filename}")


main.add_command(export_biome)
main.add_command(import_biome)
