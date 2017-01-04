#!/projects/tumour_char/analysis_scripts/python/centos06/anaconda3_v2.3.0/bin/python

"""
output file format

+------------------------+-------------+-------------+--------------------------------------------------------------+
| column_name            | data_type   | example     | description                                                  |
+========================+=============+=============+==============================================================+
| classification         | SVTYPE      | deletion    | the type of structural variant being called                  |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| cluster_id             | int         | 1           | the id for the cluster that this was derived from            |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break1_chromosome      | string      | X           | the name of the chromosome                                   |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break1_position_start  | int         | 1           | the start of the breakpoint interval                         |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break1_position_end    | int         | 10          | the end of the breakpoint interval                           |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break1_orientation     | char        | R           | orientation of the first breakpoint                          |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break2_chromosome      | str         | 12          | the name of the chromosome                                   |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break2_position_start  | int         | 2           | the start of the breakpoint interval                         |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break2_position_end    | int         | 20          | the end of the breakpoint interval                           |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break2_orientation     | char        | R           | orientation of the second breakpoint                         |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| opposing_strands       | boolean     | False       | if the strands are not the same at both breakpoints          |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| stranded               | boolean     | True        | if strand matters (if False assume pos/pos ~ neg/neg)        |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| contigs_assembled      | int         | 0           | number of contigs built from split reads                     |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| contig_alignments      | int         | 1           | number of alignments created from blatting contigs           |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| contig_sequence        | string      | ATGC...     | the full sequence of the contig                              |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| contig_remap_score     | float       | 21          | reads which remap to the contig (multimaps are fractional)   |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| contig_alignment_score | float       | 20          | the score which indicates how unique the alignment was       |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| contig_co_mutations    | string      | 12:g.123A>T | a semi-colon delimited list of small mutations called        |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| call_method            | CALL_METHOD | CONTIG      | the method used to call the breakpoints (CONTIG, FLANK, etc) |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| flanking_reads         | int         | 23          | number of flanking reads which support the call              |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| median_insert_size     | int         | 8200        | the median insert size as called by flanking reads           |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| stdev_insert_size      | float       | 7.7         | the standard deviation (wrt the median) in the insert sizes  |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break1_split_reads     | int         | 0           | the number of split reads at the first breakpoint            |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| break2_split_reads     | int         | 45          | the number of split reads at the second breakpoint           |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| linking_split_reads    | int         | 3           | the number of split reads that support both breakpoints      |
+------------------------+-------------+-------------+--------------------------------------------------------------+
| untemplated_sequence   | string      | ATCGGT      | sequence between the two breakpoints                         |
+------------------------+-------------+-------------+--------------------------------------------------------------+


"""
import subprocess
import TSV
import argparse
import os
import re
from structural_variant import __version__
from structural_variant.constants import *
from structural_variant.error import *
from structural_variant.read_tools import CigarTools
from structural_variant.breakpoint import Breakpoint, BreakpointPair
from structural_variant.read_tools import BamCache
from structural_variant.validate import Evidence, EvidenceSettings
from structural_variant.blat import blat_contigs
from structural_variant.interval import Interval
from structural_variant.annotate import load_masking_regions, load_reference_genome, load_reference_genes
from tools import profile_bam
import math
import itertools
from datetime import datetime
import pysam

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

__prog__ = os.path.basename(os.path.realpath(__file__))

INPUT_BAM_CACHE = None
REFERENCE_ANNOTATIONS = None
HUMAN_REFERENCE_GENOME = None
MASKED_REGIONS = None
EVIDENCE_SETTINGS = EvidenceSettings(median_insert_size=385, stdev_isize=95)


def mkdirp(dirname):
    try:
        os.makedirs(dirname)
    except OSError as exc:  # Python >2.5: http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
        if exc.errno == errno.EEXIST and os.path.isdir(dirname):
            pass
        else:
            raise


def read_config_file(filename):
    pass


def read_cluster_file(name, is_stranded):
    header, rows = TSV.read_file(
        name,
        require=[
            'cluster_id',
            'cluster_size',
            'break1_chromosome',
            'break1_position_start',
            'break1_position_end',
            'break1_orientation',
            'break1_strand',
            'break2_chromosome',
            'break2_position_start',
            'break2_position_end',
            'break2_orientation',
            'break2_strand',
            'opposing_strands'
        ],
        cast={
            'cluster_size': int,
            'break1_position_start': int,
            'break1_position_end': int,
            'break2_position_start': int,
            'break2_position_end': int,
            'opposing_strands': TSV.bool
        }
    )
    evidence = []
    for row in rows:
        strands = [(row['break1_strand'], row['break2_strand'])]
        if is_stranded:
            strands = itertools.product(STRAND.expand(row['break1_strand']), STRAND.expand(row['break2_strand']))
            strands = [(s1, s2) for s1, s2 in strands if row['opposing_strands'] == (s1 != s2)]
        if len(strands) == 0:
            raise UserWarning('error in reading input file. could not resolve strands', row)

        for s1, s2 in strands:
            bpp = BreakpointPair(
                Breakpoint(
                    row['break1_chromosome'],
                    row['break1_position_start'],
                    row['break1_position_end'],
                    strand=s1,
                    orient=row['break1_orientation']
                ),
                Breakpoint(
                    row['break2_chromosome'],
                    row['break2_position_start'],
                    row['break2_position_end'],
                    strand=s2,
                    orient=row['break2_orientation']
                ),
                opposing_strands=row['opposing_strands']
            )
            try:
                e = Evidence(
                    bpp,
                    INPUT_BAM_CACHE,
                    HUMAN_REFERENCE_GENOME,
                    annotations=REFERENCE_ANNOTATIONS,
                    protocol=row['protocol'],
                    data=row
                )
                evidence.append(e)
            except UserWarning as e:
                warnings.warn('failed to read cluster {}'.format(repr(e)))
    return evidence


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--version', action='version', version='%(prog)s version ' + __version__,
        help='Outputs the version number'
    )
    parser.add_argument(
        '-f', '--overwrite',
        action='store_true', default=False,
        help='set flag to overwrite existing reviewed files'
    )
    parser.add_argument(
        '-o', '--output',
        help='path to the output directory', required=True
    )
    parser.add_argument(
        '-n', '--input',
        help='path to the input file', required=True
    )
    parser.add_argument(
        '-b', '--bamfile',
        help='path to the input bam file', required=True
    )
    parser.add_argument(
        '--stranded', default=False,
        help='indicates that the input bam file is strand specific'
    )
    parser.add_argument(
        '-l', '--library',
        help='library id', required=True
    )
    parser.add_argument(
        '-m', '--masking_file',
        default='/home/creisle/svn/svmerge/trunk/hg19_masked_regions.tsv',
        help='path to the masking regions file'
    )
    parser.add_argument(
        '-a', '--annotations',
        default='/home/creisle/svn/ensembl_flatfiles/ensembl69_transcript_exons_and_domains_20160808.tsv',
        help='path to the reference annotations of genes, transcript, exons, domains, etc.'
    )
    parser.add_argument(
        '-r', '--reference_genome',
        default='/home/pubseq/genomes/Homo_sapiens/TCGA_Special/GRCh37-lite.fa',
        help='path to the human reference genome in fa format'
    )
    parser.add_argument(
        '-p', '--protocol',
        default=PROTOCOL.GENOME,
        choices=[PROTOCOL.GENOME, PROTOCOL.TRANS]
    )
    args = parser.parse_args()
    return args


def gather_evidence_from_bam(clusters):
    evidence = []

    for i, e in enumerate(clusters):
        if e.protocol == PROTOCOL.GENOME:
            tab = '[' + str(datetime.now()) + ']'
            print()
            print(
                tab,
                '({} of {})'.format(i + 1, len(clusters)),
                'gathering evidence for:',
                e.breakpoint_pair
            )
            tab = ' ' * len(tab)
            print(tab, 'possible event type(s):', BreakpointPair.classify(e.breakpoint_pair))
            try:
                e.load_evidence()
            except NotImplementedError as err:
                print(tab, repr(err))
                continue
            print(
                tab,
                'flanking reads:', [len(a) for a in e.flanking_reads],
                'split reads:', [len(a) for a in e.split_reads]
            )
            e.assemble_split_reads()
            print(tab, 'assembled {} contigs'.format(len(e.contigs)))
            evidence.append(e)
            ihist = {}
            for read in itertools.chain.from_iterable(e.flanking_reads):
                isize = abs(read.template_length)
                ihist[isize] = ihist.get(isize, 0) + 1
            try:
                median = profile_bam.histogram_median(ihist)
                stdev = math.sqrt(profile_bam.histogram_stderr(ihist, median))
                print(tab, 'insert size: {:.0f} +/- {:.2f}'.format(median, stdev))
            except:
                pass
        else:
            raise NotImplementedError('currently only genome protocols are supported')
    return evidence


def main():
    global INPUT_BAM_CACHE, REFERENCE_ANNOTATIONS, MASKED_REGIONS, HUMAN_REFERENCE_GENOME
    """
    - read the evidence
    - assemble contigs from the split reads
    - blat the contigs
    - pair the blatted contigs (where appropriate)
    - TODO: call the breakpoints and summarize the evidence
    """
    args = parse_arguments()

    FILENAME_PREFIX = re.sub('\.(txt|tsv)$', '', os.path.basename(args.input))
    EVIDENCE_BAM = os.path.join(args.output, FILENAME_PREFIX + '.evidence.bam')
    CONTIG_BAM = os.path.join(args.output, FILENAME_PREFIX + '.contigs.bam')
    EVIDENCE_BED = os.path.join(args.output, FILENAME_PREFIX + '.evidence.bed')
    OUTPUT_FILE = os.path.join(args.output, FILENAME_PREFIX + '.validated')
    MIN_EXTEND_OVERLAP = 6  # on each end
    MIN_CONTIG_READ_REMAP = 3
    MIN_BREAKPOINT_RESOLUTION = 3
    INPUT_BAM_CACHE = BamCache(args.bamfile)
    print('[{}] loading the masking regions: {}'.format(datetime.now(), args.masking_file))
    MASKED_REGIONS = load_masking_regions(args.masking_file)
    for chr in MASKED_REGIONS:
        for m in MASKED_REGIONS[chr]:
            if m.name == 'nspan':
                m.position.start -= EVIDENCE_SETTINGS.read_length
                m.position.end += EVIDENCE_SETTINGS.read_length

    # load the reference genome
    print('[{}] loading the reference genome: {}'.format(datetime.now(), args.reference_genome))
    HUMAN_REFERENCE_GENOME = load_reference_genome(args.reference_genome)
    if args.protocol == PROTOCOL.TRANS:
        print('[{}] loading the reference annotations: {}'.format(datetime.now(), args.annotations))
        REFERENCE_ANNOTATIONS = load_reference_genes(args.annotations)
    print('[{}] loading complete'.format(datetime.now()))

    evidence_reads = set()

    split_read_contigs = set()
    chr_to_index = {}

    clusters = read_cluster_file(args.input, args.stranded)
    filtered_clusters = []
    for cluster in clusters:
        overlaps_mask = None
        for mask in MASKED_REGIONS.get(cluster.break1.chr, []):
            if Interval.overlaps(cluster.window1, mask):
                overlaps_mask = mask
                break
        for mask in MASKED_REGIONS.get(cluster.break2.chr, []):
            if Interval.overlaps(cluster.window2, mask):
                overlaps_mask = mask
                break
        if overlaps_mask is None:
            filtered_clusters.append(cluster)
        else:
            print('[{}] dropping cluster {} overlapping mask {}:{}-{}'.format(
                datetime.now(), cluster.breakpoint_pair, mask.reference_object, mask.start, mask.end))

    evidence = gather_evidence_from_bam(filtered_clusters)

    blat_sequences = set()
    for e in evidence:
        for c in e.contigs:
            blat_sequences.add(c.seq)
    print('\n[{}] blatting {} contig sequences'.format(datetime.now(), len(blat_sequences)))
    blat_contig_alignments = blat_contigs(
        evidence,
        INPUT_BAM_CACHE,
        reference_genome=HUMAN_REFERENCE_GENOME
    )
    print('[{}] blat complete'.format(datetime.now()))
    event_calls = []
    for e in evidence:
        print('\n[{}] calling events for {}'.format(datetime.now(), e.breakpoint_pair))
        calls = []
        try:
            calls = e.call_events()
            event_calls.extend(calls)
        except UserWarning as e:
            print('warning: error in calling events', repr(e))
        print('[{}] call {} events'.format(datetime.now(), len(calls)))

    # write the output validated clusters (split by type and contig)
    header = [
        'cluster_id',
        'validation_id',
        'break1_chromosome',
        'break1_position_start',
        'break1_position_end',
        'break1_orientation',
        'break1_strand',
        'break2_chromosome',
        'break2_position_start',
        'break2_position_end',
        'break2_orientation',
        'break2_strand',
        'event_type',
        'opposing_strands',
        'stranded',
        'protocol',
        'tools',
        'contigs_assembled',
        'contigs_aligned',
        'contig_sequence',
        'contig_remap_score',
        'contig_alignment_score',
        'break1_call_method',
        'break2_call_method',
        'flanking_reads',
        'median_insert_size',
        'stdev_insert_size',
        'break1_split_reads',
        'break1_split_reads_forced',
        'break2_split_reads',
        'break2_split_reads_forced',
        'linking_split_reads',
        'untemplated_sequence',
        'break1_homologous_sequence',
        'break2_homologous_sequence',
        'break1_ewindow',
        'break1_ewindow_count',
        'break2_ewindow',
        'break2_ewindow_count'
    ]

    id_prefix = re.sub(' ', '_', str(datetime.now()))
    id = 1
    with open(OUTPUT_FILE, 'w') as fh:
        fh.write('#' + '\t'.join(header) + '\n')
        for ec in event_calls:
            flank_count, flank_median, flank_stdev = ec.count_flanking_support()
            b1_count, b1_custom, b2_count, b2_custom, link_count = ec.count_split_read_support()
            b1_homseq = None
            b2_homseq = None
            try:
                b1_homseq, b2_homseq = ec.breakpoint_sequence_homology(HUMAN_REFERENCE_GENOME)
            except AttributeError:
                pass
            row = {
                'cluster_id': ec.data['cluster_id'],
                'validation_id': 'validation_{}-{}'.format(id_prefix, id),
                'break1_chromosome': ec.break1.chr,
                'break1_position_start': ec.break1.start,
                'break1_position_end': ec.break1.end,
                'break1_strand': STRAND.NS,
                'break1_orientation': ec.break1.orient,
                'break2_chromosome': ec.break2.chr,
                'break2_position_start': ec.break2.start,
                'break2_position_end': ec.break2.end,
                'break2_strand': STRAND.NS,
                'break2_orientation': ec.break2.orient,
                'event_type': ec.classification,
                'opposing_strands': ec.opposing_strands,
                'stranded': ec.stranded,
                'protocol': ec.evidence.protocol,
                'tools': ec.data['tools'],
                'contigs_assembled': len(ec.evidence.contigs),
                'contigs_aligned': sum([len(c.alignments) for c in ec.evidence.contigs]),
                'contig_sequence': None,
                'contig_remap_score': None,
                'contig_alignment_score': None,
                'break1_call_method': ec.call_method,
                'break2_call_method': ec.call_method,
                'flanking_reads': flank_count,
                'median_insert_size': flank_median,
                'stdev_insert_size': flank_stdev,
                'break1_split_reads': b1_count,
                'break1_split_reads_forced': b1_custom,
                'break2_split_reads': b2_count,
                'break2_split_reads_forced': b2_custom,
                'linking_split_reads': link_count,
                'untemplated_sequence': None,
                'break1_homologous_sequence': b1_homseq,
                'break2_homologous_sequence': b2_homseq,
                'break1_ewindow': '{}-{}'.format(*ec.evidence.window1),
                'break2_ewindow': '{}-{}'.format(*ec.evidence.window2),
                'break1_ewindow_count': ec.evidence.counts[0],
                'break2_ewindow_count': ec.evidence.counts[1]
            }
            if ec.contig:
                row['contig_sequence'] = ec.contig.seq
                row['contig_remap_score'] = ec.contig.remap_score()
            if ec.alignment:
                r1, r2 = ec.alignment
                if r2 is None:
                    row['contig_alignment_score'] = r1.get_tag('br')
                else:
                    row['contig_alignment_score'] = int(round((r1.get_tag('br') + r2.get_tag('br')) / 2, 0))
            if ec.untemplated_sequence is not None:
                row['untemplated_sequence'] = ec.untemplated_sequence
            if ec.stranded:
                row['break1_strand'] = ec.break1.strand
                row['break2_strand'] = ec.break2.strand
            fh.write('\t'.join([str(row[col]) for col in header]) + '\n')
            id += 1

    with pysam.AlignmentFile(CONTIG_BAM, 'wb', template=INPUT_BAM_CACHE.fh) as fh:
        print('[{}] writing: {}'.format(datetime.now(), CONTIG_BAM))
        for ev in evidence:
            for c in ev.contigs:
                for read1, read2 in c.alignments:
                    read1.cigar = CigarTools.convert_for_igv(read1.cigar)
                    fh.write(read1)
                    if read2:
                        read2.cigar = CigarTools.convert_for_igv(read2.cigar)
                        fh.write(read2)

    # write the evidence
    with pysam.AlignmentFile(EVIDENCE_BAM, 'wb', template=INPUT_BAM_CACHE.fh) as fh:
        print('[{}] writing: {}'.format(datetime.now(), EVIDENCE_BAM))
        reads = set()
        for ev in evidence:
            print(ev)
            temp = ev.supporting_reads()
            reads.update(temp)
        for read in reads:
            read.cigar = CigarTools.convert_for_igv(read.cigar)
            fh.write(read)
    # now sort the contig bam
    sort = re.sub('.bam$', '.sorted', CONTIG_BAM)
    print('[{}] sorting the bam file: {}'.format(datetime.now(), CONTIG_BAM))
    subprocess.call(['samtools', 'sort', CONTIG_BAM, sort])
    CONTIG_BAM = sort + '.bam'
    print('[{}] indexing the sorted bam: {}'.format(datetime.now(), CONTIG_BAM))
    subprocess.call(['samtools', 'index', CONTIG_BAM])

    # then sort the evidence bam file
    sort = re.sub('.bam$', '.sorted', EVIDENCE_BAM)
    print('[{}] sorting the bam file: {}'.format(datetime.now(), EVIDENCE_BAM))
    subprocess.call(['samtools', 'sort', EVIDENCE_BAM, sort])
    EVIDENCE_BAM = sort + '.bam'
    print('[{}] indexing the sorted bam: {}'.format(datetime.now(), EVIDENCE_BAM))
    subprocess.call(['samtools', 'index', EVIDENCE_BAM])

    INPUT_BAM_CACHE.close()

if __name__ == '__main__':
    main()


