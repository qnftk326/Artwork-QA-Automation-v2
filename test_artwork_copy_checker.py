import unittest

from artwork_copy_checker import check_artwork, normalize


class ArtworkCopyCheckerTests(unittest.TestCase):
    def test_whitespace_and_linebreaks_are_ignored(self):
        self.assertEqual(normalize("KEEPING FRESH &\n SPACE-SAVING STORAGE"),
                         normalize("Keeping Fresh & Space-Saving Storage"))

    def test_exact_native_copy_passes(self):
        results = check_artwork({"sample.pdf": {
            "native": "HEAT-RESISTANT UP TO 420° C 최대 420°C 내열",
            "ocr": "",
        }})
        first = results[0]
        self.assertEqual(first["status"], "FAIL")  # other reference phrases are absent
        self.assertEqual(first["english_status"], "EXACT")
        self.assertEqual(first["korean_status"], "EXACT")

    def test_empty_korean_reference_is_not_marked_missing(self):
        results = check_artwork({"sample.pdf": {
            "native": "Tefal is a registered trademark of Tefal S.A.S. FRANCE -15 Avenue des Alpes - ZAE Rumilly Est - BP 89 - 74150 RUMILLY - France – R.C.S. Annecy B 301 520 920 www.tefal.com",
            "ocr": "",
        }})
        distributor = results[-1]
        self.assertEqual(distributor["english_status"], "REVIEW")
        self.assertEqual(distributor["korean_status"], "NOT_CONFIGURED")
        self.assertEqual(distributor["status"], "REVIEW")

    def test_ocr_only_match_requires_review(self):
        results = check_artwork({"sample.pdf": {
            "native": "",
            "ocr": "HEAT-RESISTANT UP TO 420° C 최대 420°C 내열",
        }})
        self.assertEqual(results[0]["english_status"], "OCR_REVIEW")
        self.assertEqual(results[0]["korean_status"], "OCR_REVIEW")

    def test_missing_copy_fails(self):
        results = check_artwork({"sample.pdf": {"native": "", "ocr": ""}})
        self.assertEqual(results[0]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
