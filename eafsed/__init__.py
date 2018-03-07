import click as cli
import logging as log

from lxml import etree
import regex as re

LOG = log.getLogger(__name__)
LOGLEVELS = [s for f, s in sorted(
    (v, k) for k, v in vars(log).items() if k.isupper() and isinstance(v, int))]


def matches(value, requirement):
    return requirement is None or value == requirement


def process(file, tier_type, tier_id, search, replace):
    firstl = file.readline()
    secondl = file.readline()
    file.seek(0)
    eaf = etree.parse(file)
    file.close()
    for tier in eaf.xpath("//TIER"):
        if matches(tier.attrib["LINGUISTIC_TYPE_REF"], tier_type)\
           and matches(tier.attrib["TIER_ID"], tier_id):
            log.info(f"Matched tier {tier.attrib!r}")
            for annot in tier.xpath(".//ANNOTATION_VALUE"):
                if annot.text is not None:
                    annot.text = re.sub(search, replace, annot.text)
    # don't let lxml turn empty annotations into self-closing tags to avoid spurious differences
    for annot in eaf.xpath("//ANNOTATION_VALUE"):
        if annot.text is None:
            annot.text = ""
    xml_dump = etree.tounicode(eaf.getroot(), pretty_print=True)
    # the attribs of the root element get mixed up by lxml → use the original ones for the sake of
    # sane diffs; ditto the XML declaration line (see below)
    _, xml_dump = xml_dump.split("\n", maxsplit=1)
    with open(file.name, "w") as file:
        cli.echo(firstl, file=file, nl=False)
        cli.echo(secondl, file=file, nl=False)
        cli.echo(xml_dump, file=file, nl=False)


@cli.command()
@cli.option("tier_type", "--type", "-t", help="Target tier linguistic type ref.", type=str)
@cli.option("tier_id", "--id", "-i", help="Target tier ID.", type=str)
@cli.option("--search", "-s", help="Regex pattern to search for.", type=str)
@cli.option("--replace", "-r", help="Regex pattern to use as replacement.", type=str)
@cli.option("lvl", "--log", help="Set logging level.", type=cli.Choice(LOGLEVELS), default="WARN")
@cli.option("--verbose", "-v", help="(Repeatedly) increase logging level.", count=True)
@cli.option("--quiet", "-q", help="(Repeatedly) decrease logging level.", count=True)
@cli.argument("input", type=cli.File("rt", encoding="utf-8"), nargs=-1)
def main(tier_type, tier_id, search, replace, lvl, verbose, quiet, input):
    """sed for eaf files.

    INPUT are the files to process.

    """
    lvl = getattr(log, lvl) - 10*verbose + 10*quiet
    log.basicConfig(level=lvl, format="[%(asctime)s {}:%(levelname)s] %(message)s".format(__name__))
    LOG.debug(f"Replacing {search} with {replace}.")
    for file in input:
        LOG.info(f"Processing {file.name}.")
        process(file, tier_type, tier_id, search, replace)
