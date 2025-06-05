# test_new_api.py
def test_load_dotenv():
    from simpleenvs import load_dotenv

    # .env 파일 생성
    with open(".env", "w") as f:
        f.write("TEST_VAR=hello_world\nDEBUG=true\nPORT=8080")

    # python-dotenv처럼 간단하게!
    load_dotenv()

    # 테스트
    import os

    assert os.getenv("TEST_VAR") == "hello_world"
    assert os.getenv("DEBUG") == "True"  # str로 저장됨
    print(os.getenv("DEBUG"))
    print("✅ load_dotenv() 성공!")


if __name__ == "__main__":
    test_load_dotenv()
