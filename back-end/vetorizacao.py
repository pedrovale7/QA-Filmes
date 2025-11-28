import pandas as pd
import numpy as np
import os
from fastembed import TextEmbedding

os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
dir = os.path.dirname(os.path.abspath(__file__))
path_csv = os.path.join(dir, 'pre_processed_movies.csv')
path_npy = os.path.join(dir, 'vetores_filmes.npy')

df = pd.read_csv(path_csv)

def vetorizar_texto():
    vetores = []
    model = TextEmbedding('BAAI/bge-small-en-v1.5')

    for i, linha in df.iterrows():
        titulo = linha['Nome_Filme']
        genero = linha['Generos']

        if 'tags' in linha:
            tags = linha['Tags']
        else:
            tags = ""

        texto = f"Título: {titulo}\n Gênero: {genero}\n Tags: {tags}"
        vetores = list(model.embed([texto]))
    
    np.save(path_npy, vetores)


def busca_vetorial(texto_busca, top_k=5):
    model = TextEmbedding('BAAI/bge-small-en-v1.5')
    vetor_busca = list(model.embed([texto_busca]))[0]

    vetores_filmes = np.load(path_npy)

    similaridades = np.dot(vetores_filmes, vetor_busca) / (np.linalg.norm(vetores_filmes, axis=1) * np.linalg.norm(vetor_busca))

    indices_top_k = np.argsort(similaridades)[-top_k:][::-1]

    resultados = df.iloc[indices_top_k].copy()
    resultados['similaridade'] = similaridades[indices_top_k]

    return resultados.to_dict(orient='records')

vetorizar_texto()