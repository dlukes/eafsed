import os.path as osp
import click as cli
import logging as log

from lxml import etree
import regex as re

NAME = osp.splitext(osp.basename(__file__))[0]
LOG = log.getLogger(NAME)
LOGLEVELS = [s for f, s in sorted(
    (v, k) for k, v in vars(log).items() if k.isupper() and isinstance(v, int))]


def process(file, tier, search, replace):
    firstl = file.readline()
    secondl = file.readline()
    file.seek(0)
    eaf = etree.parse(file)
    file.close()
    xpath = f"//TIER[@LINGUISTIC_TYPE_REF='{tier}']//ANNOTATION_VALUE"
    for annot in eaf.xpath(xpath):
        annot.text = re.sub(search, replace, annot.text)
    xml_dump = etree.tounicode(eaf.getroot(), pretty_print=True)
    # the attribs of the root element get mixed up by lxml → use the original ones for the sake of
    # sane diffs; ditto the XML declaration line (see below)
    _, xml_dump = xml_dump.split("\n", maxsplit=1)
    with open(file.name, "w") as file:
        cli.echo(firstl, file=file, nl=False)
        cli.echo(secondl, file=file, nl=False)
        cli.echo(xml_dump, file=file, nl=False)


@cli.command()
@cli.option("--tier", "-t", help="Target tier linguistic type ref.", type=str)
@cli.option("--search", "-s", help="Regex pattern to search for.", type=str)
@cli.option("--replace", "-r", help="Regex pattern to use as replacement.", type=str)
@cli.option("lvl", "--log", help="Set logging level.", type=cli.Choice(LOGLEVELS), default="WARN")
@cli.option("--verbose", "-v", help="(Repeatedly) increase logging level.", count=True)
@cli.option("--quiet", "-q", help="(Repeatedly) decrease logging level.", count=True)
@cli.argument("input", type=cli.File("rt", encoding="utf-8"), nargs=-1)
def main(tier, search, replace, lvl, verbose, quiet, input):
    """sed for eaf files.

    INPUT are the files to process.

    """
    lvl = getattr(log, lvl) - 10*verbose + 10*quiet
    log.basicConfig(level=lvl, format="[%(asctime)s {}:%(levelname)s] %(message)s".format(NAME))
    LOG.debug(f"Replacing {search} with {replace}.")
    for file in input:
        LOG.info(f"Processing {file.name}.")
        process(file, tier, search, replace)
