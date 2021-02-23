üöäéžěář

Erstmals ist mein Ziel die Untersuchung der Daten. Ich will Minimum, Maximum, Durchschnitt, Zentralwert und Differenz erkennen. Die tiefere Analyse kommt später, wenn ich meine Fähigkeiten verbessern werde.

Python muss als erst `pandas` importieren. Andererseits R ist fast bereit. In beiden Sprachen ist der Datenimport ähnlich:

Python:
```python
import pandas as pd

fish = pd.read_csv('Fish.csv')
```

R:
```R
data <- read.csv("Fish.csv", sep=',', fileEncoding="UTF-8-BOM")
&#35; file encoding ist notwendig sonst die erste Spalte wird mit 'i..' beginnen
```
## Python

Danach beide Sprachen sind ein bisschen anders. Python geht vor. Hier als der erste Schritt brauchen wir die einzigartige Namen der Fisch:

```python
fish["Species"].unique()
```

In dem zweiten Schritt gruppieren wir die Fische und gehen die Liste durch.

```python
for specie in fish["Species"].unique():
    group = fish[fish["Species"] == specie]
```
Auf diesen Datenset können wir die Funktionen des Datenrahmens anwenden. Python und R sind auf Englisch basiert, so die Namen der Funktionen sind auch auf Englisch basiert.

```python
&#35; Durchschnitt
group.mean(axis=0)
&#35; Zentralwert
group.median(axis=0)
&#35; Minimum
group.min(axis=0)
&#35; Maximum
group.max(axis=0)
```

Die Differenzfunktion existiert in Python nicht. So ich musste das selbst machen. Ein Problem erscheint mit der ersten Spalte, die hat keine Nummern. Da müssen wir einen Parameter `numeric_only` benutzen.

```python
&#35; Differenz
group.max(axis=0, numeric_only=True) - group.min(axis=0, numeric_only=True)
```

## R

Die R-Sprache ist ein bisschen schwierig weil ich seit sechs Jahre nichts auf R geschrieben habe. Vor sechs Jahre nahmte ich eine Statistiksklasse und wir sollen es nutzen.

Beide Sprachen, Python und R, sind ein bisschen anders und man kann nicht Python ins R 1:1 übersetzen.

Die `aggregate` Funktion des `R`s hat ganz viel gemacht. Wieder mal war hier der Problem mit den Namen, so, sollte ich die hilfreiche Funktionen geschrieben. In der Zukunft will ich eine bessere Lösung finden aber zur Zeit es reicht.

```R
# Vorlage der hilfreichen Funktion
myFunction <- function (i) {
  if (!is.numeric(i)) {
    return(NA)
  }
  return(realFunction(i))
}
```
Die `aggregate` Funktion hat drei wichtige Argumente 
- `data` - Daten über die Fische
- `by` - hier soll der Name der Indexspalt sein, z. B. `list(data$Species)`
    - `data$Species` und `data['Species']` sind gleich
- `FUN` - hier kommt der Name der hilfreichen Funktion

## In nächstem Artikel

In nächstem Artikel werde ich dieser Dataset wieder explorieren aber diesmal mit D3.js.

## Komplett Code

```python
import pandas as pd

fish = pd.read_csv('Fish.csv')

for specie in fish["Species"].unique():
    group = fish[fish["Species"] == specie]
    print("Mean")
    print(group.mean(axis=0))
    print("Median")
    print(group.median(axis=0))
    print("Min")
    print(group.min(axis=0))
    print("Max")
    print(group.max(axis=0))
    print("diff")
    print(group.max(axis=0, numeric_only=True) - group.min(axis=0, numeric_only=True))
```

```R
data <- read.csv("Fish.csv", sep=',', fileEncoding="UTF-8-BOM")
# file encoding is necessary otherwise first column will start with 'i..'
print("min")
myMin <- function (i) {
  if (!is.numeric(i)) {
    return(NA)
  }
  return(min(i))
}
aggregate(data, by = list(data$Species), FUN = myMin)
print("max")
myMax <- function (i) {
  if (!is.numeric(i)) {
    return(NA)
  }
  return(max(i))
}
aggregate(data, by = list(data$Species), FUN = myMax)
print("mean")
myMean <- function (i) {
  if (!is.numeric(i)) {
    return(NA)
  }
  return(mean(i))
}
aggregate(data, by = list(data$Species), FUN = myMean)
print("median")
myMedian <- function (i) {
  if (!is.numeric(i)) {
    return(NA)
  }
  return(median(i))
}
aggregate(data, by = list(data$Species), FUN = myMedian)
print("difference")
myDifference <- function(i) {
  if (!is.numeric(i)) {
    return(NA)
  }
  return(max(i) - min(i))
}
aggregate(data, by = list(data$Species), FUN = myDifference)
```