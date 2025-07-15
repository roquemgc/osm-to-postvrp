# Extractor de Ruas de Arquivo OSM

Este projeto em Python tem como objetivo extrair, normalizar e converter dados de ruas a partir de arquivos no formato `.osm` (OpenStreetMap). As coordenadas das ruas são processadas e salvas em um arquivo `model.txt`, seguindo uma estrutura específica usada no projeto **LimeiraPilot**.

## Requisitos

- Python 3.8+
- Bibliotecas:

```bash
pip install pillow
```

## Arquivos base

- `city.osm` – Arquivo de mapa OSM, salvo no diretório raiz
- `base_model.txt` – Arquivo base com a tag `#ROADMAP`
- `background.png` – Imagem usada para obter o limite geográfico. Deve estar em `../LimeiraPilot/config/background.png`

## Como Executar

Execute o script principal:

```bash
python -m extractor.main
```

## Exemplo de Linha Gerada

```
Rua das Laranjeiras 1 [RESIDENTIAL][124,543]-[130,546]-[135,547]
```

## Observações

- Coordenadas fora dos limites da imagem (`background.png`) são descartadas.
- Ruas com menos de 2 coordenadas ou muito longas são filtradas.
- As coordenadas são convertidas para um sistema proporcional.
