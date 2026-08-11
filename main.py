import json
import os
import time

# ==========================================
# 1. 핵심 연산 및 도구 함수
# ==========================================
def mac_calculate(pattern, filter_matrix):
    """MAC 연산 (반복문 사용, 외부 라이브러리 금지)"""
    score = 0.0
    for i in range(len(pattern)):
        for j in range(len(pattern[0])):
            score += pattern[i][j] * filter_matrix[i][j]
    return score

def is_equal(a, b, epsilon=1e-9):
    """부동소수점 오차 허용 동점 비교"""
    return abs(a - b) < epsilon

def normalize_label(label):
    """라벨 정규화 (+ -> Cross, x -> X)"""
    label = label.lower()
    if label == '+' or label == 'cross':
        return 'Cross'
    elif label == 'x':
        return 'X'
    return label

def measure_time(pattern, filter_matrix, iterations=10):
    """MAC 연산 시간 측정 (10회 반복 후 평균, ms 단위)"""
    start_time = time.perf_counter()
    for _ in range(iterations):
        mac_calculate(pattern, filter_matrix)
    end_time = time.perf_counter()
    return ((end_time - start_time) / iterations) * 1000

# ==========================================
# 2. 모드 1: 사용자 입력 (3x3)
# ==========================================
def mode1():
    print("\n#-----------------------------------")
    print("# [1] 필터 입력")
    print("#-----------------------------------")
    
    try:
        print("필터 A (3줄 입력, 공백 구분)")
        filter_a = [list(map(float, input().split())) for _ in range(3)]
        print("\n필터 B (3줄 입력, 공백 구분)")
        filter_b = [list(map(float, input().split())) for _ in range(3)]
        
        print("\n#-----------------------------------")
        print("# [2] 패턴 입력")
        print("#-----------------------------------")
        print("패턴 (3줄 입력, 공백 구분)")
        pattern = [list(map(float, input().split())) for _ in range(3)]
        
        # MAC 연산 및 시간 측정
        score_a = mac_calculate(pattern, filter_a)
        score_b = mac_calculate(pattern, filter_b)
        avg_time = measure_time(pattern, filter_a) # 시간 측정용
        
        print("\n#-----------------------------------")
        print("# [3] MAC 결과")
        print("#-----------------------------------")
        print(f"A 점수: {score_a}")
        print(f"B 점수: {score_b}")
        print(f"연산 시간(평균/10회): {avg_time:.3f} ms")
        
        if is_equal(score_a, score_b):
            print("판정: 판정 불가 (UNDECIDED)")
        elif score_a > score_b:
            print("판정: A")
        else:
            print("판정: B")
            
    except ValueError:
        print("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")

# ==========================================
# 3. 모드 2: JSON 데이터 분석
# ==========================================
def mode2():
    # 파일 경로 자동 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        return

    print("\n#-----------------------------------")
    print("# [1] 필터 로드")
    print("#-----------------------------------")
    filters = data.get('filters', {})
    for size_key in filters.keys():
        print(f"✓ {size_key} 필터 로드 완료 (Cross, X)")

    print("\n#-----------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#-----------------------------------")
    
    patterns = data.get('patterns', {})
    
    # 결과 통계용 변수
    total_tests = 0
    pass_count = 0
    fail_count = 0
    fail_cases = []
    
    # 성능 분석용 변수 (크기별 시간 저장)
    time_stats = {}

    for key, val in patterns.items():
        total_tests += 1
        print(f"- -- {key} ---")
        
        # 크기 추출 (예: size_5_1 -> size_5)
        parts = key.split('_')
        size_key = f"{parts[0]}_{parts[1]}"
        n_size = int(parts[1])
        
        pattern_matrix = val['input']
        expected_raw = val['expected']
        expected = normalize_label(expected_raw)
        
        filter_cross = filters[size_key]['cross']
        filter_x = filters[size_key]['x']
        
        # MAC 연산
        score_cross = mac_calculate(pattern_matrix, filter_cross)
        score_x = mac_calculate(pattern_matrix, filter_x)
        
        # 시간 측정 (성능 분석용)
        exec_time = measure_time(pattern_matrix, filter_cross)
        if n_size not in time_stats:
            time_stats[n_size] = []
        time_stats[n_size].append(exec_time)
        
        print(f"Cross 점수: {score_cross}")
        print(f"X 점수: {score_x}")
        
        # 판정 로직
        if is_equal(score_cross, score_x):
            decision = "UNDECIDED"
        elif score_cross > score_x:
            decision = "Cross"
        else:
            decision = "X"
            
        # PASS / FAIL 확인
        if decision == expected:
            print(f"판정: {decision} | expected: {expected} | PASS")
            pass_count += 1
        else:
            reason = "동점(UNDECIDED) 규칙" if decision == "UNDECIDED" else "점수 오판정"
            print(f"판정: {decision} | expected: {expected} | FAIL ({reason})")
            fail_count += 1
            fail_cases.append(f"- {key}: {reason}에 따라 FAIL")

    # 성능 분석 표 출력
    print("\n#-----------------------------------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#-----------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수(N^2)'}")
    print("-" * 40)
    for size in sorted(time_stats.keys()):
        avg_t = sum(time_stats[size]) / len(time_stats[size])
        print(f"{size}x{size:<8} {avg_t:<15.3f} {size*size}")

    # 결과 요약 출력
    print("\n#-----------------------------------")
    print("# [4] 결과 요약")
    print("#-----------------------------------")
    print(f"총 테스트: {total_tests}개")
    print(f"통과: {pass_count}개")
    print(f"실패: {fail_count}개")
    
    if fail_count > 0:
        print("\n실패 케이스:")
        for fc in fail_cases:
            print(fc)

# ==========================================
# 메인 실행부 (메뉴)
# ==========================================
if __name__ == "__main__":
    while True:
        print("\n=== Mini NPU Simulator ===")
        print("[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("0. 종료")
        
        choice = input("선택: ")
        
        if choice == '1':
            mode1()
        elif choice == '2':
            mode2()
        elif choice == '0':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 1, 2, 0 중에서 선택해주세요.")