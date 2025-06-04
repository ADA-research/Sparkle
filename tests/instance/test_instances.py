"""Test class for the InstanceSet class."""
from pathlib import Path
from sparkle.instance import \
    FileInstanceSet, IterableFileInstanceSet, MultiFileInstanceSet, Instance_Set


def test_resolve_instance_set() -> None:
    """Test for resolving the correct instance set subclass."""
    file_instance_set_dir = Path("tests/test_files/Instances/PTN")
    file_instance_set_single = Path("tests/test_files/Instances/PTN/Ptn-b01.cnf")
    multi_instance_set_dir = Path("tests/test_files/Instances/CCAG")
    multi_instance_set_single = Path("tests/test_files/Instances/CCAG/Banking1")
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
    assert iterable_file_instance_set.all_paths == dir_content
    assert iterable_file_instance_set.instance_paths == dir_content
    assert iterable_file_instance_set.instance_names == ["Iris1.csv", "Iris2.npy"]
    assert iterable_file_instance_set.instances == iterable_file_instance_set.instance_paths
    assert iterable_file_instance_set.name == "Iris"
    assert str(iterable_file_instance_set) == "Iris"
    assert iterable_file_instance_set.get_path_by_name("Iris1.csv") == dir_content[0]
    assert iterable_file_instance_set.get_path_by_name("DoesNotExist") is None
    for instance in iterable_file_instance_set.all_paths:
        assert IterableFileInstanceSet.__determine_size__(instance) == 75


def test_multi_file_instance_set_single_instance() -> None:
    """Test for MultiFileInstanceSet properties."""
    instance_dir = Path("tests/test_files/Instances/CCAG")
    instance_csv = instance_dir / "instances.csv"
    paths = [Path("tests/test_files/Instances/CCAG/Banking1.model"),
             Path("tests/test_files/Instances/CCAG/Banking1.constraints")]
    target = Path("tests/test_files/Instances/CCAG/Banking1")
    multi_file_instance_set = MultiFileInstanceSet(target)
    assert multi_file_instance_set.directory == target.parent
    assert multi_file_instance_set.size == 1
    assert multi_file_instance_set.all_paths == paths + [instance_csv]
    assert multi_file_instance_set.instance_paths == [paths]
    assert multi_file_instance_set.instance_names == ["Banking1"]
    assert multi_file_instance_set.instances == [
        Path("tests/test_files/Instances/CCAG/Banking1")]
    assert multi_file_instance_set.name == "CCAG"
    assert str(multi_file_instance_set) == "CCAG"
    assert multi_file_instance_set.get_path_by_name("Banking1") == paths
    assert multi_file_instance_set.get_path_by_name("DoesNotExist") is None


def test_multi_file_instance_set_directory() -> None:
    """Test for MultiFileInstanceSet properties."""
    instance_dir = Path("tests/test_files/Instances/CCAG")
    instance_csv = instance_dir / "instances.csv"
    dir_content = [
        Path("tests/test_files/Instances/CCAG/Banking1.model"),
        Path("tests/test_files/Instances/CCAG/Banking1.constraints"),
        Path("tests/test_files/Instances/CCAG/Healthcare1.model"),
        Path("tests/test_files/Instances/CCAG/Healthcare1.constraints")
    ]
    multi_file_instance_set = MultiFileInstanceSet(instance_dir)
    assert multi_file_instance_set.directory == instance_dir
    assert multi_file_instance_set.size == 2
    assert multi_file_instance_set.all_paths == dir_content + [instance_csv]
    assert multi_file_instance_set.instance_paths == [dir_content[:2], dir_content[2:]]
    assert multi_file_instance_set.instance_names == ["Banking1", "Healthcare1"]
    assert multi_file_instance_set.instances == [Path(
        "tests/test_files/Instances/CCAG/Banking1"), Path("tests/test_files/Instances/CCAG/Healthcare1")]
    assert multi_file_instance_set.name == "CCAG"
    assert str(multi_file_instance_set) == "CCAG"
    assert multi_file_instance_set.get_path_by_name("Banking1") == dir_content[:2]
    assert multi_file_instance_set.get_path_by_name("DoesNotExist") is None


def test_file_instance_set_single_file() -> None:
    """Test for MultiFileInstanceSet properties."""
    single_instance = Path("tests/test_files/Instances/PTN/Ptn-b01.cnf")
    single_instance_set = FileInstanceSet(single_instance)
    assert single_instance_set.directory == Path("tests/test_files/Instances/PTN")
    assert single_instance_set.size == 1
    assert single_instance_set.all_paths == [single_instance]
    assert single_instance_set.instance_paths == [single_instance]
    assert single_instance_set.instance_names == ["Ptn-b01"]
    assert single_instance_set.instances == single_instance_set.instance_paths
    assert single_instance_set.name == "Ptn-b01"
    assert str(single_instance_set) == "Ptn-b01"
    assert single_instance_set.get_path_by_name("Ptn-b01") == single_instance
    assert single_instance_set.get_path_by_name("DoesNotExist") is None


def test_file_instance_set_directory() -> None:
    """Test for FileInstanceSet properties."""
    instance_dir = Path("tests/test_files/Instances/PTN")
    dir_content = [
        Path("tests/test_files/Instances/PTN/Ptn-b01.cnf"),
        Path("tests/test_files/Instances/PTN/Ptn-b03.cnf"),
        Path("tests/test_files/Instances/PTN/Ptn-b05.cnf")
    ]
    file_instance_set = FileInstanceSet(instance_dir)
    assert file_instance_set.directory == instance_dir
    assert file_instance_set.size == 3
    assert file_instance_set.all_paths == dir_content
    assert file_instance_set.instance_paths == dir_content
    assert file_instance_set.instance_names == [
        "Ptn-b01", "Ptn-b03", "Ptn-b05"]
    assert file_instance_set.instances == file_instance_set.instance_paths
    assert file_instance_set.name == "PTN"
    assert str(file_instance_set) == "PTN"
    assert file_instance_set.get_path_by_name("Ptn-b01") == dir_content[0]
    assert file_instance_set.get_path_by_name("DoesNotExist") is None
