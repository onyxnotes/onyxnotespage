---
title: "{{ replace .Name "-" " " | title }}"
description: ""
lead: ""
excerpt: ""
date: {{ .Date }}
lastmod: {{ .Date }}
draft: true
images: []
categories: []
tags: []
menu:
  notes:
    parent: ""
    identifier: "{{ .Name }}-{{ delimit (shuffle (split (md5 .Name) "" )) "" }}"
weight: 999
contributors: []
toc: true
---
