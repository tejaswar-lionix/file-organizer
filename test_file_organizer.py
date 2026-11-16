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


class DuplicateTests(unittest.TestCase):
    def test_identical_files_are_grouped(self):
        from organizer import find_duplicates

        with tempfile.TemporaryDirectory() as directory:
            for name in ("a.txt", "b.txt"):
                with open(os.path.join(directory, name), "w", encoding="utf-8") as handle:
                    handle.write("same content")
            groups = find_duplicates(directory)
            self.assertEqual(len(groups), 1)
            self.assertEqual(list(groups.values()), [["a.txt", "b.txt"]])

    def test_unique_file_is_excluded(self):
        from organizer import find_duplicates

        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "only.txt"), "w", encoding="utf-8") as handle:
                handle.write("unique")
            self.assertEqual(find_duplicates(directory), {})

    def test_files_are_left_in_place(self):
        from organizer import find_duplicates

        with tempfile.TemporaryDirectory() as directory:
            for name in ("a.txt", "b.txt"):
                with open(os.path.join(directory, name), "w", encoding="utf-8") as handle:
                    handle.write("same content")
            find_duplicates(directory)
            self.assertTrue(os.path.exists(os.path.join(directory, "a.txt")))
            self.assertTrue(os.path.exists(os.path.join(directory, "b.txt")))

    def test_empty_directory_returns_empty_dict(self):
        from organizer import find_duplicates

        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(find_duplicates(directory), {})


class MappingTests(unittest.TestCase):
    def test_load_mapping_normalises_extensions(self):
        import json

        from organizer import load_mapping, plan_organize

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "map.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"Design": [".PSD", ".Sketch"]}, handle)
            mapping = load_mapping(path)
            self.assertEqual(
                plan_organize(["hero.psd"], mapping=mapping),
                [("hero.psd", "Design")],
            )


if __name__ == "__main__":
    unittest.main()
