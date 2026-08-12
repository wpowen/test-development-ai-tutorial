import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).parent
OUTPUT_ROOT = ROOT.parents[1]
PUBLIC = OUTPUT_ROOT / "site/public/materials/profession-reality"
ARCHIVE = OUTPUT_ROOT / "site/public/materials/profession-reality.zip"


def distributable_files(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and not path.name.endswith(".pyc")
    }


class MaterialClosureTests(unittest.TestCase):
    def test_canonical_public_and_zip_are_byte_identical(self):
        canonical = distributable_files(ROOT)
        public = distributable_files(PUBLIC)
        self.assertEqual(set(canonical), set(public))
        for name, content in canonical.items():
            self.assertEqual(content, public[name], name)

        with zipfile.ZipFile(ARCHIVE) as archive:
            zipped = {
                name.removeprefix("profession-reality/"): archive.read(name)
                for name in archive.namelist()
                if not name.endswith("/") and name.startswith("profession-reality/") and "__pycache__" not in name
            }
        self.assertEqual(set(canonical), set(zipped))
        for name, content in canonical.items():
            self.assertEqual(content, zipped[name], name)


if __name__ == "__main__":
    unittest.main()
