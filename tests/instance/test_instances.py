"""Test class for the InstanceSet class."""

from pathlib import Path
from collections import defaultdict

import pytest

from sparkle.instance import (
    FileInstanceSet,
    IterableFileInstanceSet,
    MultiFileInstanceSet,
    Instance_Set,
    resolve_instance_pair,
)
from sparkle.CLI.help.nicknames import resolve_instance_name


def test_resolve_instance_set() -> None:
    """Test for resolving the correct instance set subclass."""
    file_instance_set_dir = Path("Examples/Resources/Instances/PTN")
    file_instance_set_single = Path("Examples/Resources/Instances/PTN/Ptn-7824-b01.cnf")
    multi_instance_set_dir = Path("Examples/Resources/CCAG/Instances/CCAG")
    multi_instance_set_single = Path("Examples/Resources/CCAG/Instances/CCAG/Banking1")
    iterable_instance_set = Path("tests/test_files/Instances/Iris")

    assert isinstance(Instance_Set(file_instance_set_dir), FileInstanceSet)
    assert isinstance(Instance_Set(file_instance_set_single), FileInstanceSet)
    assert isinstance(Instance_Set(multi_instance_set_dir), MultiFileInstanceSet)
    assert isinstance(Instance_Set(multi_instance_set_single), MultiFileInstanceSet)
    assert isinstance(Instance_Set(iterable_instance_set), IterableFileInstanceSet)


def test_iterable_file_instance_set() -> None:
    """Test for IterableFileInstanceSet properties."""
    instance_dir = Path("tests/test_files/Instances/Iris")
    dir_content = [
        Path("tests/test_files/Instances/Iris/Iris1.csv"),
        Path("tests/test_files/Instances/Iris/Iris2.npy"),
    ]
    iterable_file_instance_set = IterableFileInstanceSet(instance_dir)
    assert iterable_file_instance_set.directory == instance_dir
    assert iterable_file_instance_set.size == 75
    assert set(iterable_file_instance_set.all_paths) == set(dir_content)
    assert set(iterable_file_instance_set.instance_paths) == set(dir_content)
    assert set(iterable_file_instance_set.instance_names) == set(
        ["Iris1.csv", "Iris2.npy"]
    )
    assert iterable_file_instance_set.instances == [
        str(p.with_suffix("")) for p in iterable_file_instance_set.instance_paths
    ]
    assert iterable_file_instance_set.name == "Iris"
    assert str(iterable_file_instance_set) == "Iris"
    assert iterable_file_instance_set.get_path_by_name("Iris1.csv") == dir_content[0]
    assert iterable_file_instance_set.get_path_by_name("DoesNotExist") is None
    for instance in iterable_file_instance_set.all_paths:
        assert IterableFileInstanceSet.__determine_size__(instance) == 75


def test_multi_file_instance_set_single_instance() -> None:
    """Test for MultiFileInstanceSet properties."""
    instance_dir = Path("Examples/Resources/CCAG/Instances/CCAG")
    instance_csv = instance_dir / "instances.csv"
    paths = [
        Path("Examples/Resources/CCAG/Instances/CCAG/Banking1.model"),
        Path("Examples/Resources/CCAG/Instances/CCAG/Banking1.constraints"),
    ]
    target = Path("Examples/Resources/CCAG/Instances/CCAG/Banking1")
    multi_file_instance_set = MultiFileInstanceSet(target)
    assert multi_file_instance_set.directory == target.parent
    assert multi_file_instance_set.size == 1
    assert set(multi_file_instance_set.all_paths) == set(paths + [instance_csv])
    assert multi_file_instance_set.instance_paths == [paths]
    assert multi_file_instance_set.instance_names == ["Banking1"]
    assert multi_file_instance_set.instances == [
        Path("Examples/Resources/CCAG/Instances/CCAG/Banking1")
    ]
    assert multi_file_instance_set.name == "CCAG"
    assert str(multi_file_instance_set) == "CCAG"
    assert multi_file_instance_set.get_path_by_name("Banking1") == paths
    assert multi_file_instance_set.get_path_by_name("DoesNotExist") is None


def test_multi_file_instance_set_directory() -> None:
    """Test for MultiFileInstanceSet properties."""
    instance_dir = Path("Examples/Resources/CCAG/Instances/CCAG")
    dir_content = [f for f in instance_dir.iterdir() if f.is_file()]
    dir_dict = defaultdict(list)
    for path in dir_content:
        if path.name == "instances.csv":
            continue
        dir_dict[path.stem].append(path)
    multi_file_instance_set = MultiFileInstanceSet(instance_dir)

    assert multi_file_instance_set.directory == instance_dir
    # 2 files for each instance + csv file
    assert multi_file_instance_set.size == (len(dir_content) - 1) / 2
    assert set(multi_file_instance_set.all_paths) == set(dir_content)
    for path in multi_file_instance_set.instance_paths:
        assert set(path) == set(dir_dict[path[0].stem])
    assert set(multi_file_instance_set.instance_names) == set(dir_dict.keys())
    assert set(multi_file_instance_set.instances) == set(
        instance_dir / Path(key) for key in dir_dict.keys()
    )
    assert multi_file_instance_set.name == "CCAG"
    assert str(multi_file_instance_set) == "CCAG"
    # Compare as sets: get_path_by_name returns instances.csv order while dir_dict follows
    # Path.iterdir() order, which is filesystem-dependent.
    assert set(multi_file_instance_set.get_path_by_name("Banking1")) == set(
        dir_dict["Banking1"]
    )
    assert multi_file_instance_set.get_path_by_name("DoesNotExist") is None


def test_file_instance_set_single_file() -> None:
    """Test for MultiFileInstanceSet properties."""
    single_instance = Path("Examples/Resources/Instances/PTN/Ptn-7824-b01.cnf")
    single_instance_set = FileInstanceSet(single_instance)
    assert single_instance_set.directory == Path("Examples/Resources/Instances/PTN")
    assert single_instance_set.size == 1
    assert single_instance_set.all_paths == [single_instance]
    assert single_instance_set.instance_paths == [single_instance]
    assert single_instance_set.instance_names == ["Ptn-7824-b01"]
    assert single_instance_set.instance_pairs == [("PTN", "Ptn-7824-b01")]
    assert single_instance_set.instances == [
        str(p.with_suffix("")) for p in single_instance_set.instance_paths
    ]
    assert single_instance_set.name == "Ptn-7824-b01"
    assert str(single_instance_set) == "Ptn-7824-b01"
    assert single_instance_set.get_path_by_name("Ptn-7824-b01") == single_instance
    assert single_instance_set.get_path_by_name("DoesNotExist") is None


def test_file_instance_set_directory() -> None:
    """Test for FileInstanceSet properties."""
    instance_dir = Path("Examples/Resources/Instances/PTN")
    dir_content = [f for f in instance_dir.iterdir() if f.is_file()]
    file_instance_set = FileInstanceSet(instance_dir)
    assert file_instance_set.directory == instance_dir
    assert file_instance_set.size == len(dir_content)
    assert set(file_instance_set.all_paths) == set(dir_content)
    assert set(file_instance_set.instance_paths) == set(dir_content)
    assert set(file_instance_set.instance_names) == set([f.stem for f in dir_content])
    assert file_instance_set.instances == [
        str(p.with_suffix("")) for p in file_instance_set.instance_paths
    ]
    assert file_instance_set.name == "PTN"
    assert str(file_instance_set) == "PTN"
    assert file_instance_set.get_path_by_name("Ptn-7824-b01") == next(
        (p for p in dir_content if p.stem == "Ptn-7824-b01"), None
    )
    assert file_instance_set.get_path_by_name("DoesNotExist") is None


def test_resolve_instance_pair() -> None:
    """Test resolving a single instance path to its stored (set_name, instance_name) pair."""
    # A single Path resolves to its pair directly (not wrapped in a list). Every subclass
    # names its instances differently, so the pair must match what the set itself stores
    # rather than being derived from the path.
    for instance_dir in (
        Path("Examples/Resources/Instances/PTN"),  # FileInstanceSet: stem
        Path("tests/test_files/Instances/Iris"),  # Iterable: name with suffix
    ):
        instance_set = Instance_Set(instance_dir)
        for pair, path in zip(instance_set.instance_pairs, instance_set.instance_paths):
            assert resolve_instance_pair(path) == pair

    # Regression: the instance name of an IterableFileInstanceSet keeps its suffix, so
    # deriving it with Path.stem silently produced a key no row was stored under.
    iris_path = Path("tests/test_files/Instances/Iris/Iris1.csv")
    assert resolve_instance_pair(iris_path) == ("Iris", "Iris1.csv")
    assert iris_path.stem == "Iris1"  # What the old derivation produced

    # Unknown paths fall back to (parent directory name, file stem)
    unknown = Path("Examples/Resources/Instances/PTN/DoesNotExist.cnf")
    assert resolve_instance_pair(unknown) == ("PTN", "DoesNotExist")


def test_resolve_instance_pair_multiple() -> None:
    """Test resolving a list of paths to a pair per path, in input order."""
    ptn = Path("Examples/Resources/Instances/PTN")
    iris = Path("tests/test_files/Instances/Iris")
    ccag = Path("Examples/Resources/CCAG/Instances/CCAG")
    # Each path is resolved independently, so pairs come back one per path, in order,
    # even when the paths span different sets and all three subclasses (FileInstanceSet,
    # IterableFileInstanceSet, MultiFileInstanceSet), each with its own naming convention.
    paths = [
        ptn / "Ptn-7824-b01.cnf",  # FileInstanceSet: stem
        iris / "Iris1.csv",  # IterableFileInstanceSet: name with suffix
        ptn / "Ptn-7824-b03.cnf",  # back to the first set
        ccag / "Banking1.model",  # MultiFileInstanceSet: name from CSV
    ]
    assert resolve_instance_pair(paths) == [
        ("PTN", "Ptn-7824-b01"),
        ("Iris", "Iris1.csv"),
        ("PTN", "Ptn-7824-b03"),
        ("CCAG", "Banking1"),
    ]

    # A multi-file instance's files each resolve to the same pair (one per file), since
    # every path is treated independently.
    assert resolve_instance_pair(
        [ccag / "Banking1.model", ccag / "Banking1.constraints"]
    ) == [("CCAG", "Banking1"), ("CCAG", "Banking1")]


def test_resolve_instance_pair_missing_set() -> None:
    """Test that a path whose set directory does not exist raises rather than guessing.

    A missing file inside an existing set falls back to (dir name, stem), but a missing
    set directory raises: Instance_Set(path.parent) reaches iterdir() on a directory that
    is not there. Fabricating a pair here would write a phantom key to the data frame.
    """
    missing_set = Path("Examples/Resources/Instances/GhostSet/foo.cnf")
    assert not missing_set.parent.exists()
    with pytest.raises(FileNotFoundError):
        resolve_instance_pair(missing_set)


def test_resolve_instance_name() -> None:
    """Test resolving a (set_name, instance_name) pair to its instance path(s)."""
    instance_sets = [
        Instance_Set(Path(instance_dir))
        for instance_dir in (
            "Examples/Resources/Instances/PTN",
            "Examples/Resources/Instances/PTN2",
            "tests/test_files/Instances/Iris",
            "Examples/Resources/CCAG/Instances/CCAG",
        )
    ]

    # Names are looked up through the owning set, so each subclass' naming convention
    # resolves: the stem for FileInstanceSet, the name with suffix for the iterable one.
    assert resolve_instance_name("PTN", "Ptn-7824-b01", instance_sets) == Path(
        "Examples/Resources/Instances/PTN/Ptn-7824-b01.cnf"
    )
    assert resolve_instance_name("Iris", "Iris1.csv", instance_sets) == Path(
        "tests/test_files/Instances/Iris/Iris1.csv"
    )

    # An unresolvable name yields None rather than raising
    assert resolve_instance_name("PTN", "DoesNotExist", instance_sets) is None

    # search_location may also be a directory containing instance set directories
    assert resolve_instance_name(
        "Iris", "Iris2.npy", Path("tests/test_files/Instances")
    ) == Path("tests/test_files/Instances/Iris/Iris2.npy")


def test_resolve_instance_name_multi_file() -> None:
    """Test that a multi-file instance resolves to all of its paths."""
    ccag_dir = Path("Examples/Resources/CCAG/Instances/CCAG")
    expected = {str(ccag_dir / "Banking1.model"), str(ccag_dir / "Banking1.constraints")}

    # A multi file instance is passed to a command line as a single argument, so its
    # paths are returned space joined rather than as a list.
    resolved = resolve_instance_name("CCAG", "Banking1", [Instance_Set(ccag_dir)])
    assert set(resolved.split(" ")) == expected

    # The same holds when the name is a suffix-less path, which is resolved by globbing
    # the parent directory instead of going through the set.
    resolved = resolve_instance_name("CCAG", str(ccag_dir / "Banking1"), [])
    assert set(resolved.split(" ")) == expected


def test_resolve_instance_name_existing_path() -> None:
    """Test that an instance name that already is a file path is returned as a Path."""
    instance_path = Path("Examples/Resources/Instances/PTN/Ptn-7824-b01.cnf")
    resolved = resolve_instance_name("PTN", str(instance_path), [])
    # Returned as a Path, like the other single file branch, so callers do not have to
    # handle both a str and a Path depending on which branch resolved the name.
    assert isinstance(resolved, Path)
    assert resolved == instance_path


def test_resolve_instance_name_shared_name(tmp_path: Path) -> None:
    """Test that instances sharing a name across sets resolve to their own set."""
    for set_name in ("SetA", "SetB"):
        (tmp_path / set_name).mkdir()
        (tmp_path / set_name / "shared.cnf").write_text(f"p cnf {set_name}\n")
    instance_sets = [Instance_Set(tmp_path / name) for name in ("SetA", "SetB")]

    for set_name in ("SetA", "SetB"):
        resolved = resolve_instance_name(set_name, "shared", instance_sets)
        assert resolved == tmp_path / set_name / "shared.cnf"


def test_resolve_instance_name_pair_roundtrip() -> None:
    """Test that resolve_instance_name and resolve_instance_pair are inverses."""
    for instance_dir in (
        Path("Examples/Resources/Instances/PTN"),
        Path("tests/test_files/Instances/Iris"),
    ):
        instance_set = Instance_Set(instance_dir)
        for pair in instance_set.instance_pairs:
            instance_path = resolve_instance_name(*pair, [instance_set])
            assert resolve_instance_pair(instance_path) == pair
