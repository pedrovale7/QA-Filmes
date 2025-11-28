import pandas as pd
import numpy as np
from fastembed import TextEmbedding

df = pd.read_csv('pre_processed_movies.csv')
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

        texto = f"Título: {titulo}\nGênero: {genero}\nTags: {tags}"
        vetores = list(model.embed([texto]))
    
    np.save('back-end/vetores_filmes.npy', vetores)


def busca_vetorial(texto_busca, top_k=5):
    model = TextEmbedding('BAAI/bge-small-en-v1.5')
    vetor_busca = list(model.embed([texto_busca]))[0]

    vetores_filmes = np.load('vetores_filmes.npy')

    similaridades = np.dot(vetores_filmes, vetor_busca) / (np.linalg.norm(vetores_filmes, axis=1) * np.linalg.norm(vetor_busca))

    indices_top_k = np.argsort(similaridades)[-top_k:][::-1]

    resultados = df.iloc[indices_top_k].copy()
    resultados['similaridade'] = similaridades[indices_top_k]

    return resultados.to_dict(orient='records')