# Topological Graph Mapping and Discrete Informed Search: A Geophysical Perspective on ARC-AGI-3

**Author:** Muhammad Umar Bilal  
**Affiliation:** Eight Pillars Consultancy FZ-LLC

## 📖 Overview
This repository contains the official code submission for the **ARC Prize 2026 - Paper Track**. 

We present a deterministic, graph-based agent that treats the ARC-AGI-3 environment as an unknown terrain. Drawing on 15+ years of experience in geophysical survey planning, the agent applies discrete state-hashing and Breadth-First Search (BFS) for optimal environmental coverage.

## 🧠 Methodology (Version 5 Architecture)
Our agent operates without the computational overhead of continuous neural networks. It uses a four-phase loop:
1. **Topological Mapping:** Visual frames are hashed (MD5) and mapped into a directed graph.
2. **Centroid Sniper:** Uses NumPy to identify the rarest non-background object (min 5 pixels) and clicks its exact geometric center for complex `(x, y)` coordinate actions.
3. **Bounded BFS & Dead-End Elimination:** Actions that do not change the state are eliminated. A Bounded Breadth-First Search (max depth=3) calculates the shortest path to the nearest unexplored state, preventing RHAE penalties from long traversals.
4. **Verified Sprint Memory:** Once a level is cleared, the agent saves the exact winning path (state hash, action ID, coordinates) and perfectly replays it.

## 📂 Repository Structure
- `my_agent.py`: The core agent logic implementing the Grandmaster architecture.
- `pathfinder.py`: The BFS script for offline graph analysis.
- `play.py`: A basic script to run the environment locally.

## 🚀 Competition Details
- **Competition:** ARC Prize 2026 - ARC-AGI-3
- **Paper Track:** Topological Graph Mapping and Discrete Informed Search
- **Evaluation:** Kaggle Offline Inference Server (utilizing local `.whl` installation and `pydantic_core` patch).

## 👨‍💻 Author
**Muhammad Umar Bilal**
- Geophysicist | AI Geospatial Solutions 
- Founder of Eight Pillars Consultancy FZ-LLC
- M.Sc. Geophysics, Quaid-e-Azam University
- [LinkedIn Profile](https://www.linkedin.com/in/muhammad-umar-bilal-umarbillallucky)