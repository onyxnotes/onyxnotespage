---
title: "Test"
description: "Es un archivo para probar el markdown"
lead: "Archivo para probar markdown"
date: 2022-08-06T01:58:33+02:00
lastmod: 2022-08-06T01:58:33+02:00
draft: false
images: []
menu:
  docs:
    parent: ""
    identifier: "test-1e26c4fc43f4809d27b67a6bedd23863"
weight: 999
toc: true
---
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

Esto es un párrafo

---

> Esto es un quote

Ahí va un poco de python

```python
def hello():
	print("hello world")
```

Ahí va una integral de $f(x)$

$$\int_a^b f(x)dx$$

<br>
<br>
Esto es texto con <span style="color:red">color</span>
<br>
<br>

Ahí va una tabla

|Hola|Adiós|
|:-:|:-:|
|1|2|
|3|4|

Ahí va una imagen global (a la que le podemos cambiar el tamaño)

{{< globalimgsinalt imgpath="images/default-image.png" res="200x">}}


<br>
<br>
<br>

Ahi va una **imagen global** con alt

{{< globalimg imgpath="images/default-image.png" res="300x" alt="Imagen en blanco">}}


<br>
<br>
<br>

Ahí va una imagen global centrada

{{< globalimgsinaltct imgpath="images/default-image.png" res="300x">}}

Ahi va una imagen de markdown vanilla
<span style="width:400">![](images/default-image.png)<span>


