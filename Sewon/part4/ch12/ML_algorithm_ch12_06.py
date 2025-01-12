#CH12_06. Collaborative Filtering (1)
"""
1. 협업 필터링 (Collaborative Filtering)
-여러 유저의 과거 아이템 상호작용 정보를 이용해 추천

-상호작용
 ex) 영화 평점, 제품 사용 리뷰, 동영상 시청 시간, 클릭 횟수 등
 
2. 메모리 기반(Memory Based) 협업 필터링
-여러 유저의 과거 아이템 상호작용 정보를 메모리에 저장하고, 추천이 필요할 때마다 전체 데이터를 이용해 추천
-메모리 기반 종류
 1) 유저 기반 (User Based)
    : 아이템 선호도가 비슷한 유저를 탐색하고 비슷한 유저가 좋아한 것 중 새로운 아이템 추천
 2) 아이템 기반 (Item Based)
    : 유저들의 선호도가 비슷한 아이템을 탐색하고, 유저가 기존에 선호한 아이템과 유사한 아이템 추천

3. KNN
-가장 유사한 K개의 이웃을 통해 아이템을 추천하는 방법
-유저별 아이템 선호도 예측

-KNN 협업 필터링 종류
 1) KNN Basic
 -KNN Basic 유저 기반: 아이템 i에 대한 유저 u의 선호도 예측
 -KNN Basic 유저 기반 방법
 Step1) 유저 간의 유사도 계산
 Step2) 아이템i를 평가한 유저들 중에서 유저u와 비슷한 유저 k명을 찾는다.
 Step3) K명의 유사한 유저들이 아이템i에 평가한 선호도를 유사도 기준으로 가중 평균
 Step4) 예측 선호도가 높은 아이템을 유저에게 추천

 2) KNN with Means
 -선호도의 평균에 선호도 편차를 유사도 기준으로 가중 평균을 더하는 방법
 -유저나 아이템의 평균 선호도를 반영
 -KNN with Means 유저 기반 방법
 Step1) 유저간의 유사도를 계산
 Step2) 아이템i를 평가한 유저들 중에서 유저u와 비슷한 유저k명을 찾는다.
 Stpe3) 아이템i의 평균 선호도를 계산
 Step4) K명의 유사한 유저들이 아이템i에 평가한 선호도의 편차를 유사도 기준으로 가중 평균
 Step5) 예측 선호도가 높은 아이템을 유저에게 추천
"""