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


class LargestFilesTests(unittest.TestCase):
    def test_orders_by_size_then_name(self):
        from organizer import largest_files

        with tempfile.TemporaryDirectory() as directory:
            for name, size in (("b.txt", 3), ("a.txt", 3), ("c.txt", 5)):
                with open(os.path.join(directory, name), "w", encoding="utf-8") as handle:
                    handle.write("x" * size)
            self.assertEqual(
                largest_files(directory),
                [("c.txt", 5), ("a.txt", 3), ("b.txt", 3)],
            )

    def test_respects_limit(self):
        from organizer import largest_files

        with tempfile.TemporaryDirectory() as directory:
            for name, size in (("a.txt", 1), ("b.txt", 2), ("c.txt", 3)):
                with open(os.path.join(directory, name), "w", encoding="utf-8") as handle:
                    handle.write("x" * size)
            self.assertEqual(largest_files(directory, limit=2), [("c.txt", 3), ("b.txt", 2)])

    def test_ignores_directories(self):
        from organizer import largest_files

        with tempfile.TemporaryDirectory() as directory:
            os.makedirs(os.path.join(directory, "folder"))
            with open(os.path.join(directory, "file.txt"), "w", encoding="utf-8") as handle:
                handle.write("data")
            self.assertEqual(largest_files(directory), [("file.txt", 4)])

    def test_empty_directory_returns_empty_list(self):
        from organizer import largest_files

        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(largest_files(directory), [])

    def test_limit_below_one_raises(self):
        from organizer import largest_files

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                largest_files(directory, limit=0)


class TotalSizeTests(unittest.TestCase):
    def test_sums_top_level_file_sizes(self):
        from organizer import total_size

        with tempfile.TemporaryDirectory() as directory:
            for name, size in (("a.txt", 3), ("b.txt", 5)):
                with open(os.path.join(directory, name), "w", encoding="utf-8") as handle:
                    handle.write("x" * size)
            self.assertEqual(total_size(directory), 8)

    def test_ignores_subdirectories(self):
        from organizer import total_size

        with tempfile.TemporaryDirectory() as directory:
            os.makedirs(os.path.join(directory, "folder"))
            with open(
                os.path.join(directory, "folder", "nested.txt"), "w", encoding="utf-8"
            ) as handle:
                handle.write("x" * 10)
            with open(os.path.join(directory, "file.txt"), "w", encoding="utf-8") as handle:
                handle.write("data")
            self.assertEqual(total_size(directory), 4)

    def test_empty_directory_returns_zero(self):
        from organizer import total_size

        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(total_size(directory), 0)


class UndoTests(unittest.TestCase):
    def test_undo_restores_organized_files(self):
        from organizer import undo_moves

        with tempfile.TemporaryDirectory() as directory:
            for name in ("photo.jpg", "notes.md"):
                open(os.path.join(directory, name), "w").close()
            moves = organize(directory, dry_run=False)
            restored = undo_moves(moves, directory)
            self.assertEqual(sorted(restored), ["notes.md", "photo.jpg"])
            self.assertTrue(os.path.exists(os.path.join(directory, "photo.jpg")))
            self.assertTrue(os.path.exists(os.path.join(directory, "notes.md")))

    def test_undo_skips_missing_source(self):
        from organizer import undo_moves

        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(undo_moves([("gone.jpg", "Images")], directory), [])

    def test_undo_conflict_raises_without_overwrite(self):
        from organizer import undo_moves

        with tempfile.TemporaryDirectory() as directory:
            os.makedirs(os.path.join(directory, "Images"))
            with open(
                os.path.join(directory, "Images", "photo.jpg"), "w", encoding="utf-8"
            ) as handle:
                handle.write("organized")
            with open(
                os.path.join(directory, "photo.jpg"), "w", encoding="utf-8"
            ) as handle:
                handle.write("existing")
            with self.assertRaises(FileExistsError):
                undo_moves([("photo.jpg", "Images")], directory)
            with open(
                os.path.join(directory, "photo.jpg"), encoding="utf-8"
            ) as handle:
                self.assertEqual(handle.read(), "existing")
            with open(
                os.path.join(directory, "Images", "photo.jpg"), encoding="utf-8"
            ) as handle:
                self.assertEqual(handle.read(), "organized")


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


class CategorySummaryTests(unittest.TestCase):
    def test_counts_files_and_bytes_by_category(self):
        import os
        import tempfile

        from organizer import category_summary

        with tempfile.TemporaryDirectory() as directory:
            for name, size in (("a.png", 3), ("b.jpg", 2), ("c.txt", 5)):
                with open(os.path.join(directory, name), "wb") as handle:
                    handle.write(b"x" * size)
            summary = category_summary(directory)
        self.assertEqual(summary["Images"], {"files": 2, "bytes": 5})
        self.assertEqual(summary["Documents"], {"files": 1, "bytes": 5})


if __name__ == "__main__":
    unittest.main()
