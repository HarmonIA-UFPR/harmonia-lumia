from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sliding_session():
    # 1. Tentar criar um mock de UserServiceDependency para não precisar de DB
    pass


if __name__ == '__main__':
    test_sliding_session()
