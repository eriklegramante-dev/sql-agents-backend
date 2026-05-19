from sqlalchemy.exc import SQLAlchemyError


class BeginContext:
    def __init__(self, raises=False):
        self.raises = raises

    async def __aenter__(self):
        if self.raises:
            raise SQLAlchemyError("boom")
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def run_sync(self, callback):
        self.callback = callback


class Engine:
    def __init__(self, raises=False):
        self.raises = raises

    def begin(self):
        return BeginContext(raises=self.raises)


class Session:
    def __init__(
        self,
        record=None,
        execute_result=None,
        raises=None,
    ):
        self.record = record
        self.execute_result = execute_result
        self.raises = raises
        self.committed = False
        self.rolled_back = False
        self.deleted = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def add(self, instance):
        self.instance = instance

    async def commit(self):
        if self.raises == "commit":
            raise SQLAlchemyError("boom")

        self.committed = True

    async def refresh(self, instance):
        if getattr(instance, "id", None) is None:
            instance.id = 10

    async def rollback(self):
        self.rolled_back = True

    async def get(self, model, record_id):
        if self.raises == "get":
            raise SQLAlchemyError("boom")

        return self.record

    async def execute(self, statement):
        if self.raises == "execute":
            raise SQLAlchemyError("boom")

        return self.execute_result

    async def delete(self, record):
        if self.raises == "delete":
            raise SQLAlchemyError("boom")
        self.deleted = record


class Result:
    def __init__(self, record):
        self.record = record

    def scalar_one_or_none(self):
        return self.record


class Connection:
    def __init__(self, session=None, engine=None):
        self.session = session
        self.engine = engine or Engine()

    def get_session(self):
        return lambda: self.session
