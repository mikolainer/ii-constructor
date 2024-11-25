from iiconstructor_core.domain import InputDescription
from iiconstructor_core.domain.primitives import Name
from iiconstructor_inmemory.repo import SourceInMemory


def test_add_vector(get_source: SourceInMemory) -> None:
    name = Name("123")
    desc = InputDescription(name=name)

    get_source.add_vector(desc)
    assert get_source.check_vector_exists(name) is True
    vector = get_source.get_vector(name)
    assert vector == desc


def test_remove_vector(get_source: SourceInMemory) -> None:
    name = Name("123")
    desc = InputDescription(name=name)

    get_source.add_vector(desc)
    assert get_source.check_vector_exists(name) is True
    get_source.remove_vector(name)
    assert get_source.check_vector_exists(name) is False


def test_select_vectors(get_source: SourceInMemory) -> None:
    name = Name("123")
    desc = InputDescription(name=name)

    name2 = Name("1233")
    desc2 = InputDescription(name=name2)

    get_source.add_vector(desc)
    get_source.add_vector(desc2)

    list_vectors = get_source.select_vectors([name, name2])
    assert len(list_vectors) == 3
