from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

textos = ["adorei", "ótimo", "excelente", "péssimo", "horrível", "ruim", "muito bom", "não gostei"]
labels  = [1, 1, 1, 0, 0, 0, 1, 0]

modelo = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf",   LogisticRegression())
])
modelo.fit(textos, labels)

with open("modelo.pkl", "wb") as f:
    pickle.dump(modelo, f)