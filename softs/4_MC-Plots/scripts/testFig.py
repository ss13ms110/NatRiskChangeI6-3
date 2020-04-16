import matplotlib.pyplot as plt

tags = ['R', 'homo_MAS', 'GF_MAS', 'GF_OOP', 'GF_VM', 'GF_MS', 'GF_VMC']

fig = plt.figure(figsize=(16,8))

for i, tag in enumerate(tags):
    ax = fig.add_subplot(2, 4, i+1)


plt.show()