import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler

# 차원 축소 시각화 실습
np.random.seed(2021)

# 1. Data
# 1.1 Data Load

digit = load_digits()

data, target = digit["data"], digit["target"]
data[0], target[0]
data[0].shape

samples = data[:10].reshape(10, 8, 8)
fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(20, 10))
for idx, sample in enumerate(samples):
    axes[idx//5, idx%5].imshow(sample, cmap="gray")
plt.show()

# 1.2 정규화
scaler = StandardScaler()
scaled_data = scaler.fit_transform(data)

# 2. PCA
# 2.1 학습
from sklearn.decomposition import PCA
pca = PCA()
pca.fit(scaled_data)

# 2.2 설명된 분산
pca.explained_variance_

plt.plot(pca.explained_variance_)
plt.show()

# 2.3 설명된 분산의 비율
pca.explained_variance_ratio_

plt.plot(pca.explained_variance_ratio_)
plt.plot(pca.explained_variance_ratio_.cumsum(), linestyle="--")
plt.show()

# 3. 제한된 PCA
# 3.1 비율료 사용하는 방법
# `n_components` argument는 int와 float을 입력으로 받습니다.
# 0~1사이가 들어올 경우 설명된 분산이 해당 값에 도달할 때까지 주성분을 선택합니다.
ratio_pca = PCA(n_components=0.8)
ratio_pca.fit(scaled_data)
ratio_pca.explained_variance_ratio_
ratio_pca.explained_variance_ratio_.cumsum()
ratio_pca.n_components_

# 3.2 개수를 지정해서 사ㅛㅇ하는 방법
# `n_components` argument는 int와 float을 입력으로 받습니다.
# int 값으로 1보다 큰 값을 줄 경우에는 지정된 개수만큼의 주성분을 계산합니다.
plt.plot(pca.explained_variance_)
plt.show()

n_comp_pca = PCA(n_components=8)
n_comp_pca.fit(scaled_data)

n_comp_pca.explained_variance_ratio_

n_comp_pca.explained_variance_ratio_.cumsum()

# 3.3 시각화
# 이번에는 PCA를 이용해 데이터를 시각화 하는 방법에 대해서 알아보겠습니다.
# 사람이 인식할 수 있는 차원의 크기는 최대 3차원입니다.
# 그래서 보통 2차원 또는 3차원으로 데이터를 축소한 후 시각화를 진행합니다.
# 2차원으로 차원 축소는 주성분의 개수를 2개로, 3차원으로 차원 축소는 주성분의 개수를 3개로 하면 됩니다.

viz_pca = PCA(n_components=2)
viz_pca_latent = viz_pca.fit_transform(scaled_data)

def visualize_latent_space_with_label(latent):
    for label in np.unique(target):
        index = target == label
        component_1 = latent[index, 0]
        component_2 = latent[index, 1]
        plt.scatter(component_1, component_2, c=f"C{label}", label=label)
    plt.legend()
    plt.show()

visualize_latent_space_with_label(viz_pca_latent)

# 4. LDA
# 4.1 학습
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
lda = LinearDiscriminantAnalysis()
lda.fit(scaled_data, target)

# 4.2 설명된 분산
# 다만 LDA는 eigenvalue와 같이 분산의 크기를 나타내는 값은 없습니다.
# 설명된 분산의 크기만 확인할 수 있습니다.

lda.explained_variance_ratio_
plt.plot(lda.explained_variance_ratio_)
plt.plot(lda.explained_variance_ratio_.cumsum(), linestyle="--")
plt.show()

# 4.2 시각화
viz_lda = LinearDiscriminantAnalysis(n_components=2)
viz_lda_latent = viz_lda.fit_transform(scaled_data, target)
visualize_latent_space_with_label(viz_lda_latent)

# 4. T-SNE
from sklearn.manifold import TSNE
tsne = TSNE(n_components=2)
# 4.1 시각화
tsne_latent = tsne.fit_transform(scaled_data)
visualize_latent_space_with_label(tsne_latent)

# 5. 마무리
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))
latents = [
    ("pca", viz_pca_latent),
    ("lda", viz_lda_latent),
    ("tsne", tsne_latent)
]
for idx, (name, latent) in enumerate(latents):
    ax = axes[idx]
    ax.scatter(latent[:, 0], latent[:, 1], c=target)
    ax.set_title(name)

plt.show()
