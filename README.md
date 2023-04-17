# SimpleML

Projet simple de generation de séquences.

## Entraînement

- Préparer un fichier texte avec le contenu sur lequel entraîner le modèle (eg [sherlock](ML/sherlock.txt), [shakespeake](ML/shakespeare.txt)). Le contenu n'a qu'une seule contrainte: contenir des séquences de caractères ou de mots. Ce que ces mots ou caractères représentent n'est pas forcément du texte
- Modifier et faire tourner [train.py](train.py) (ou mieux, le google collag avec GPU) dessus
- Récuperer les fichiers `char_idx...pickle`, `...tfl.meta`, `...tfl.index` et `...tfl.data-XXXX` et les mettre quelque part

## Utilisation

- initialiser *le même modèle qu'à l'entraînement* (en termes de réseau neuronal)
- appeler la méthode `load` du modèle avec le chemin du tfl
- appeler la méthode `generate` du modèle pour générer une nouvelle séquence

ou bien

- utiliser la classe `ModelLoader` qui le fait pour vous, si vous respectez la structure des dossiers (`ML/xxx/xxx.tfl`)

## FAQ

### Combien de temps a prend d'entraîner un nouveau modèle?

Avec Google Collab ou une **grosse** config, compter une heure pour un petit texte comme `sherlock`, deux heures pour un fichier plus gros comme `shakespeare`

### Est-ce que je suis obligé(e) d'utiliser du texte comme les exemples?

Oui et non. Le modèle s'entraiine sur des séquences de caractères. Mais ce que veulent dire ces caractères est libre. Par exemple, si vous décidez d'entraîner le modèle à jouer à Tetris, vous pouvez utiliser UDLR pour up down right left, et utiliser l'output comme appuis sur des boutons. Le modèle essayera juste de produire un output qui *ressemble* à son input.

### Quelle taille de texte dois-je utiliser?

Plus vous avez d'exemples *différents*, plus le modèle aura de variabilité, mais plus il sera long à entraîner. Un modèle très court fera essentiellement du copier coller de vos exemples, alors qu'un modèle plus gros aura plus de chances de générer quelque chose de nouveau.

### Temperature?!?

La variabilité "autorisée". À 0, le générateur ignore le modèle, à 1, il ne prend que le caractère le plus fréquent après la suite donnée. C'est une mesure de random, en quelque sorte.

### Comment je lance les exemples fournis?

#### Installation des dépendances

- préparez l'environnement: `python -m venv venv`
- activez l'environnement: `. venv/bin/activate`
- mettez pip à jour: `pip install -U pip`
- installez les requirements: `pip install -U -r required.txt`

#### Lancement simple

Si vous ne voulez pas traiter plus d'une requête à la fois, utilisez dans `app.py` les lignes

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8280)
```

et commentez les deux dernières lignes. Lancez le serveur avec `python app.py`. L'API est disponible sur http://localhost:8280

#### Lancement multiple

Si vous voulez être capable de gérer plusieurs requêtes en même temps, utilisez gunicorn. Commentez les deux lignes de lancement simple, décommentez les deux dernières lignes:

```python
server = pywsgi.WSGIServer(('0.0.0.0', 8280), app)
server.serve_forever()
```

puis lancez le programme avec `gunicorn -t 300 app.py`. L'API est disponible sur http://localhost:8280

#### Attention!

Le premier chargement est *lent*. Il prend aussi pas mal de RAM.

#### l'API

Très simple:

- `GET /<model>/g/<seed>/<size>[/<temp>]` utilise `model` pour générer la suite de `seed`, de taille `size`, avec une température optionnelle de `temp`. 
ex: `GET /contes/g/le%20sultan/100` -> `le sultan de rendre à ses cris d'admiration de gros enfants qui n'étaient pas nouvelles de notre endroit de la forêt, et de l`
- `POST /shakespeare` accepte un json contenant `seed`, `size`, et optionnellement `temp` pour faire la même chose

### J'ai décidé d'entraîner mon propre modèle, dans quoi je m'embarque?

Si vous avez juste décidé d'utiliser une source de texte (ou de pseudo texte comme dans l'exemple de Tetris) différente, rien de compliqué à part attendre.

Si vous voulez "améliorer" le modèle, vous pouvez:

- Jouer sur la structure du réseau de neurones. Actuellement, c'est un triple layer de 512 neurones. Si vous avez relativement peu de caracteres, vous pouvez utiliser moins de layers, ou moins de neurones. Le modèle sera alors beaucoup plus simple à entraîner. En gros, plus vous avez de neurones par layer, plus le modèle est capable de variété, et plus vous avez de layers, et plus il est capable de "comprendre" la séquence absorbée. 3x512 est un bon compromis pour du texte en francais ou en anglais avec un "style" particulier (shakespearien, conte pour enfant, etc). Pour des styles moins "stricts", il vous faudra probablement plus d'exemples, plus de layers, et plus de neurones par layer. 

- Forcer le modèle à coller un peu plus aux exemples. Si vous trouvez que le modèle manque de jugeote, vous pouvez augmenter le nombre d'époques d'entraînement (50 dans l'exemple). Plus vous forcez le modèle a "coller" aux exemples et moins il sera original. Attention, dans ce contexte, original peut vouloir dire "dit du charabia" si le modèle n'est pas assez entraîné.

- Jouer sur la taille de la séquence à mémoriser (avec `seq_maxlen` et `redun_step`). Si vous le forcez à regarder 3 caracteres sur les séquences de taille maximale de 25, vous obtenez le 4e caractère le plus probable, basé sur ces séquences/exemples. Si vous augmentez à 4 caractères par exemple, vous aurez des résultats différents (la question devenant "quel est le 5e caractère le plus probable après ces 4 là" au lieu de "quel est le 4e caractère, après ces 3 là?")# workshop_avril_2023
