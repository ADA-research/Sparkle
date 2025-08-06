"""Test class for the InstanceSet class."""

from pathlib import Path
from collections import defaultdict
from sparkle.instance import (
    FileInstanceSet,
    IterableFileInstanceSet,
    MultiFileInstanceSet,
    Instance_Set,
)


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
    assert multi_file_instance_set.get_path_by_name("Banking1") == dir_dict["Banking1"]
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
