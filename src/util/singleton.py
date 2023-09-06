class Singleton:
    _instance = None  # 클래스 변수로 유일한 인스턴스를 저장할 변수

    def __new__(cls):
        # 인스턴스가 없으면 새로 생성하고, 이미 있으면 기존 인스턴스를 반환
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
            
        return cls._instance