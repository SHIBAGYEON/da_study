# CH02_06. 자료형_튜플

'''리스트는 대괄호, 튜플은 소괄호'''

a=(1, 2, 3)

print(type(a))
print(a[1]) #인덱스
print(a[:2]) #슬라이스

a[2]=0 #치환 불가
'''
리스트: 치환 가능
튜플: 치환 불가
'''

#튜플 더하기
a=(1, 2, 3)
b=(4, 5, 6)
c=a+b
print(c) 

#튜플 곱하기
a=(1, 2, 3)
b=a*2
print(b)