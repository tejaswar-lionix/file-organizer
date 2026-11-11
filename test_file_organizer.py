import os
import tempfile
import unittest

from organizer import category_for, organize, plan_organize


class OrganizerTests(unittest.TestCase):
    def test_category_lookup_is_case_insensitive(self):
        self.assertEqual(category_for("photo.JPG"), "Images")
        self.assertEqual(category_for("notes.md"), "Documents")
        self.assertEqual(category_for("archive.bin"), "Other")

    def test_plan_organize_pairs_names_with_categories(self):
        self.assertEqual(
            plan_organize(["a.jpg", "b.pdf"]),
            [("a.jpg", "Images"), ("b.pdf", "Documents")],
        )

    def test_dry_run_leaves_files_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            open(os.path.join(directory, "photo.jpg"), "w").close()
            organize(directory, dry_run=True)
            self.assertTrue(os.path.exists(os.path.join(directory, "photo.jpg")))

    def test_organize_moves_files_into_category_folders(self):
        with tempfile.TemporaryDirectory() as directory:
            open(os.path.join(directory, "photo.jpg"), "w").close()
            moved = organize(directory, dry_run=False)
            self.assertEqual(moved, [("photo.jpg", "Images")])
            self.assertTrue(
                os.path.exists(os.path.join(directory, "Images", "photo.jpg"))
            )


if __name__ == "__main__":
    unittest.main()
