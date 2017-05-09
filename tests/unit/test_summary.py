import unittest

from mavis.summary.summary import alphanumeric_choice
from mavis.breakpoint import BreakpointPair, Breakpoint
from mavis.constants import SVTYPE, COLUMNS, CALL_METHOD, ORIENT, STRAND, PROTOCOL

class TestSummary(unittest.TestCase):
    def setUp(self):
        self.gev1 = BreakpointPair(
            Breakpoint('1', 1),
            Breakpoint('1', 10),
            opposing_strands=True,
            data={
                COLUMNS.event_type: SVTYPE.DEL,
                COLUMNS.break1_call_method: CALL_METHOD.CONTIG,
                COLUMNS.break2_call_method: CALL_METHOD.CONTIG,
                COLUMNS.fusion_sequence_fasta_id: None,
                COLUMNS.protocol: PROTOCOL.GENOME
            }
        )
        self.gev2 = BreakpointPair(
            Breakpoint('1', 1),
            Breakpoint('1', 10),
            opposing_strands=True,
            data={
                COLUMNS.event_type: SVTYPE.DEL,
                COLUMNS.break1_call_method: CALL_METHOD.CONTIG,
                COLUMNS.break2_call_method: CALL_METHOD.CONTIG,
                COLUMNS.fusion_sequence_fasta_id: None,
                COLUMNS.protocol: PROTOCOL.GENOME
            }
        )

    def test_alphanumeric_choice(self):
        self.gev1.data[COLUMNS.transcript1] = 'ABC'
        self.gev1.data[COLUMNS.transcript2] = 'AB1'
        self.gev2.data[COLUMNS.transcript1] = 'ZED'
        self.gev2.data[COLUMNS.transcript2] = 'AB1'
        bpp = alphanumeric_choice(self.gev1, self.gev2)
        self.assertEqual('ABC', bpp.data[COLUMNS.transcript1])

    def test_alphanumeric_choice_numbers(self):
        self.gev1.data[COLUMNS.transcript1] = '123'
        self.gev1.data[COLUMNS.transcript2] = '345'
        self.gev2.data[COLUMNS.transcript1] = '567'
        self.gev2.data[COLUMNS.transcript2] = '890'
        bpp = alphanumeric_choice(self.gev1, self.gev2)
        self.assertEqual('123', bpp.data[COLUMNS.transcript1])

    def test_alphanumeric_choice_gene_names(self):
        self.gev1.data[COLUMNS.transcript1] = 'ENST00000367580'
        self.gev1.data[COLUMNS.transcript2] = 'ENST00000367580'
        self.gev2.data[COLUMNS.transcript1] = 'ENST00000367579'
        self.gev2.data[COLUMNS.transcript2] = 'ENST00000367579'
        bpp = alphanumeric_choice(self.gev1, self.gev2)
        self.assertEqual('ENST00000367579', bpp.data[COLUMNS.transcript1])

    def test_compare_bbp_annotations_two_best_transcripts(self):
        
        raise unittest.SkipTest('TODO')

    def test_compare_bpp_annotations_two_transcripts(self):
        raise unittest.SkipTest('TODO')

    def test_compare_bbp_annotations_two_fusion_cdna(self):
        raise unittest.SkipTest('TODO')

    def test_compare_bbp_annotations_one_transcripts(self):
        raise unittest.SkipTest('TODO')

    def test_compare_bbp_annotations_one_best_transcripts(self):
        raise unittest.SkipTest('TODO')

    def test_compare_bbp_annotations_no_transcripts(self):
        raise unittest.SkipTest('TODO')

    def test_aggregate_events(self):
        raise unittest.SkipTest('TODO')


    def test_filtering_events_contigs(self):
        raise unittest.SkipTest('TODO')

    def test_filtering_events_none(self):
        raise unittest.SkipTest('TODO')

    def test_filtering_events_flanking(self):
        raise unittest.SkipTest('TODO')

    def test_filtering_events_spanning(self):
        raise unittest.SkipTest('TODO')

    def test_filtering_events_split(self):
        raise unittest.SkipTest('TODO')

