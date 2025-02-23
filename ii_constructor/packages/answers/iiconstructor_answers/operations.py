from .data import OutputRepository, OutputFactory, IsOutputSpec, OneIdOutputSpec, OutputDescription, Output

class OutputLibService:
    @staticmethod
    def create(value: OutputDescription, factory: OutputFactory) -> Output:
        new_item = factory.create(value)
        factory._repo().save(OneIdOutputSpec(new_item.id()), new_item.value())
        return new_item

    @staticmethod
    def read(spec: IsOutputSpec, repo: OutputRepository) -> set[Output]:
        if not repo.is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(repo)
        
        return repo.get(spec)

    @staticmethod
    def update(id_spec: IsOutputSpec, new_value:OutputDescription, repo: OutputRepository):
        if not repo.is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(repo)
        
        result = repo.get(id_spec)
        
        if len(result) == 0:
            print(f"ERROR: попытка обновить несуществующий(е) объект(ы)")
            raise ValueError(id_spec)
        
        old_output = result.pop()
        repo.save(OneIdOutputSpec(old_output.id()), new_value)

    @staticmethod
    def delete(spec: IsOutputSpec, repo: OutputRepository):
        if not repo.is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(repo)
        
        repo.remove(spec)
