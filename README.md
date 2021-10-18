# export-ssna-data
A set of scripts to export and pseudonymize SSNA data for long-term storage, starting from a Discourse forum. 

## Why do we need this?

We are committed to open knowledge, and specifically open research data. More and more agencies funding research make the publication of research data in open format, but in our experience most researchers see this as overhead and tend to do it badly. 

## Documentation

A detailed explanation of what these scripts do, and why, is [here](https://edgeryders.eu/t/12786).

## Principles

1. **Close to the source**. Though we use software – including our own – to analyze, interpret and navigate the data, when publishing datasets we prefer to harvest data directly at the source, which in our case is the DB of our Discourse installation, https://edgeryders.eu. 
2. **Standard file format: CSV**. We choose CSV as a near-universal standard for data, for maximum reusability. This is in accordance with the emphasis on tabular data proposed by Open Knowledge's [Frictionless Data](https://frictionlessdata.io/specs/) project. 
3. **Standard metadata format: Data Package**. We choose [Data Package](https://datahub.io/docs/data-packages) as a metadata standard flexible enough to accommodate our data.
4. **Pseudonymized**. We publish the text of the posts as is, but pseudonymize their authors. While most posts on Edgeryders and their authors are visible on the web, we wish to uphold the author's rights to have their posts deleted. This is easy to do on the live Edgeryders platform, but it is impossible to track all downloaded copies of a dataset once it has been published on Zenodo or similar repository. Imagine someone publishes a post on Edgeryders, and that post is published, with others, on a public repository. But then, that someone changes his or her mind, and decides to delete all her/his posts. That post will live on in older versions of the dataset on the repository, but it will no longer be possible search the Edgeryders platform to attribute the post to its author.  We publish on permanent repositories posts in pseudonymized form so that, once the author of a post has deleted it from Edgeryders, it will be harder to attribute it to that person. 

## About the data

Semantic Social Networks are induced from human conversations. In our case, these conversations happen on the online forum https://edgeryders.eu. Since this is a [Discourse](https://www.discourse.org/) installation, the database architecure is organized as follows:

* **Categories**. Categories are the top level entities used by Discourse. They are intended to help the forum's user get their bearings.
* **Subcategories**. Discourse supports exactly two levels of categories. A top-level category can have several subcategories, but those subcategories cannot have sub-subcategories. 
* **Topics**. A Discourse topic is a thread of posts which share the same title. All posts except the first one are a reply to another posts in the topic, or to the topic itself (normally identified with the first post in the topic). Each topic belongs to exactly one category, which can be either a top-level category or a subcategory.
* **Posts**. A Discourse post is a piece of text authored by a single user. Each post belongs to exactly one topic.
* **Tags**. Discourse tags are keywords that can be associated to topics (not posts). Each topic can be associated to any number of tags. In SSNA studies, we use tags to identify projects, since the same topic can be used in several studies. For example, a topic on green technology could, in principle, be included in both a study on technological trends and another one on sustainability. We use the format `ethno-TAGNAME` for tags that refer to SSNA studies.

On top of these entities, we use two additional ones that are generated by the Open Ethnographer component (not part of a standard Discourse installation): 

* **Annotations**. Annotations are created by ethnographers. They refer to specific posts, and associate a snippet of text in the post to a keyword in an ontology that describes the object of the SSNA study. Ethnographers call these keywords *codes*, and the process of annotating the text is known as *coding*. Annotations contain the ID of the post they annotate, and those of the codes .
* **Codes**. Ethnographic codes are created by ethnographers. 

For a more detailed description, see [the edgeryders.eu APIs documentation](https://edgeryders.eu/t/using-the-edgeryders-eu-apis/7904).

## About the scripts

The repo has two scripts. 

* `download_and_pseudonymize.py` accesses your Discourse site via API and saves four CSV files, starting from a tag. These contain all you need to run a social semantic network analysis of the conversation around that tag. The files are pseudonymized for data protection and research ethics purposes (see the documentation on edgeryders.eu for a more detailed explanation).
* `trim_datapackage.py` is useful if you use data.world to automatically generate your dapackage.json metadata file. It gets rid of some quirks concerning the generation of a metadata file from a set of CSV files in data.world.


## What you need to use this script

This script relies on a small module called `z_discourse_API_functions`. You can find it [here](https://github.com/edgeryders/network-viz-for-ssna/blob/f68ac966547f4c388b8e5a5999b150cfae29148e/code/python%20scripts/z_discourse_API_functions.py). 

Some of the functions in the module access data that are only visible to users of the Discourse site you are using. For them to work, you will need to request an API key to the site admins. 

The functions to access ethnographic codes and annotations obviously only work if the Discourse installation supports ethnography. This is true for the different communities spawned around Edgeryders. You can create your own ethnography-ready Discourse forum using [this repository](https://github.com/edgeryders/discourse).

## Documenting your data

We recommend using the Data Package standard ([see](https://edgeryders.eu/t/using-the-edgeryders-eu-apis/7904)). We provide a template `datapackage.json`. 