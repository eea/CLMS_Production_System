## Airflow DAGs

---

## Contributors
* Samuel Carraro
* Johannes Schmid

## General Description
This directory provides the source codes of the Airflow DAGs.

A DAG (Directed Acyclic Graph) is the core concept of Airflow, collecting Tasks together, organized with dependencies and relationships to say how they should run.

Here’s a basic example DAG:

![image](https://user-images.githubusercontent.com/113164413/190569772-39f0ffcb-022b-4ca8-bcfc-7d490d867c9c.png)

It defines four Tasks - A, B, C, and D - and dictates the order in which they have to run, and which tasks depend on what others. It will also say how often to run the DAG - maybe “every 5 minutes starting tomorrow”, or “every day since January 1st, 2020”.

The DAG itself doesn’t care about what is happening inside the tasks; it is merely concerned with how to execute them - the order to run them in, how many times to retry them, if they have timeouts, and so on.

