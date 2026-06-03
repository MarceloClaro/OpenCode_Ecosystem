import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestConservationImports:
    def test_import_get_conservation(self):
        import get_conservation
        assert get_conservation is not None

    def test_ucsc_api_url_defined(self):
        import get_conservation
        assert get_conservation.UCSC_API_URL.startswith("https://")

    def test_client_instantiated(self):
        import get_conservation
        assert get_conservation.CLIENT is not None

    def test_parse_coordinate_valid(self):
        import get_conservation
        chrom, start, end = get_conservation.parse_coordinate("chr1:100-200")
        assert chrom == "chr1"
        assert start == 99
        assert end == 200

    def test_parse_coordinate_single_pos(self):
        import get_conservation
        chrom, start, end = get_conservation.parse_coordinate("chr1:100")
        assert chrom == "chr1"
        assert start == 99
        assert end == 100

    def test_parse_coordinate_invalid_raises(self):
        import get_conservation
        with pytest.raises(SystemExit):
            get_conservation.parse_coordinate("invalid")

    def test_get_conservation_data_returns_dict(self):
        import get_conservation
        result = get_conservation.get_conservation_data(
            "chr1", 0, 100, "phyloP100way", genome="hg38"
        )
        assert isinstance(result, dict)

    def test_get_conservation_data_has_track_keys(self):
        import get_conservation
        result = get_conservation.get_conservation_data(
            "chr1", 0, 100, "phyloP100way", genome="hg38"
        )
        assert "chr1" in result or "phyloP100way" in result


class TestTFBSImports:
    def test_import_get_tfbs(self):
        import get_tfbs
        assert get_tfbs is not None

    def test_client_instantiated(self):
        import get_tfbs
        assert get_tfbs.api_client is not None

    def test_parse_coordinate_valid(self):
        import get_tfbs
        chrom, start, end = get_tfbs.parse_coordinate("chr1:100-200")
        assert chrom == "chr1"
        assert start == 100
        assert end == 200

    def test_parse_coordinate_single_pos(self):
        import get_tfbs
        chrom, start, end = get_tfbs.parse_coordinate("chr1:100")
        assert chrom == "chr1"
        assert start == 100
        assert end == 101

    def test_parse_coordinate_invalid_raises(self):
        import get_tfbs
        with pytest.raises(SystemExit):
            get_tfbs.parse_coordinate("bad")

    def test_get_tfbs_data_returns_dict(self):
        import get_tfbs
        result = get_tfbs.get_tfbs_data(
            "chr1", 0, 100, "encRegTfbsClustered", genome="hg38"
        )
        assert isinstance(result, dict)


class TestListTracksImports:
    def test_import_list_tracks(self):
        import list_tracks
        assert list_tracks is not None

    def test_client_instantiated(self):
        import list_tracks
        assert list_tracks.api_client is not None

    def test_flatten_tracks_returns_list(self):
        import list_tracks
        sample = {
            "track1": {"shortLabel": "Label One", "type": "bigWig"},
            "subgroup": {
                "track2": {"shortLabel": "Label Two", "type": "bigBed"},
            },
        }
        result = list_tracks.flatten_tracks(sample)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_flatten_tracks_has_track_keys(self):
        import list_tracks
        sample = {
            "track1": {"shortLabel": "Label One", "type": "bigWig"},
        }
        result = list_tracks.flatten_tracks(sample)
        assert result[0]["track"] == "track1"
        assert result[0]["shortLabel"] == "Label One"
        assert result[0]["type"] == "bigWig"

    def test_filter_tracks_by_search(self):
        import list_tracks
        tracks = [
            {"track": "tfbsTrack", "shortLabel": "TFBS", "longLabel": "TFBS Data", "group": "reg", "type": "bigBed"},
            {"track": "geneTrack", "shortLabel": "Genes", "longLabel": "Gene Data", "group": "genes", "type": "bigBed"},
        ]
        result = list_tracks.filter_tracks(tracks, search="tfbs")
        assert len(result) == 1
        assert result[0]["track"] == "tfbsTrack"

    def test_filter_tracks_by_group(self):
        import list_tracks
        tracks = [
            {"track": "tfbsTrack", "shortLabel": "TFBS", "longLabel": "TFBS Data", "group": "regulation", "type": "bigBed"},
            {"track": "geneTrack", "shortLabel": "Genes", "longLabel": "Gene Data", "group": "genes", "type": "bigBed"},
        ]
        result = list_tracks.filter_tracks(tracks, group="genes")
        assert len(result) == 1
        assert result[0]["track"] == "geneTrack"

    def test_filter_tracks_no_match(self):
        import list_tracks
        tracks = [
            {"track": "track1", "shortLabel": "T1", "longLabel": "T1", "group": "g", "type": "bigBed"},
        ]
        result = list_tracks.filter_tracks(tracks, search="zzz_nonexistent")
        assert len(result) == 0
