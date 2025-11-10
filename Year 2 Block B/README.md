# Plant Phenotyping: Computer Vision & Robotic Automation

End-to-end AI system combining computer vision, deep learning, and reinforcement learning to automate plant root analysis and robotic inoculation for the Netherlands Plant Eco-phenotyping Centre (NPEC).

## 🎯 Project Overview

This project addresses a critical challenge in agricultural research: efficiently analyzing plant root systems and automating precise microbe inoculation for high-throughput plant phenotyping studies.

**Client:** Netherlands Plant Eco-phenotyping Centre (NPEC)  
**System:** Hades - In-vitro root system phenotyping platform  
**Capacity:** Processing up to 10,000 seedlings on 2000+ Petri dishes

### The Challenge

Plant phenotyping research requires:
- **Accurate root segmentation** from complex, overlapping structures
- **Precise root measurements** for quantitative trait analysis
- **Automated inoculation** at specific root tip locations
- **High-throughput processing** for large-scale experiments

Traditional manual analysis is time-consuming, error-prone, and cannot scale to NPEC's throughput requirements.

## ✨ Solution: Integrated AI Pipeline

### 🔍 Computer Vision Pipeline

**1. Traditional CV Preprocessing**
- Petri dish detection and extraction (±30 pixel accuracy)
- Plant instance segmentation (5 plants per dish)
- Region of interest isolation

**2. Deep Learning Segmentation**
- U-Net architecture for pixel-level root detection
- Multi-class segmentation (root, shoot, seed)
- Data augmentation for robust performance
- Achieved **F1 score > 0.8** on validation set

**3. Root System Architecture (RSA) Extraction**
- Skeletonization and branch detection
- Primary root identification and length measurement
- Root tip localization for inoculation targets
- **Kaggle competition: sMAPE < 10%** target

### 🤖 Robotic Control Systems

**1. Simulation Environment**
- PyBullet-based Opentrons OT-2 digital twin
- Working envelope determination
- State observation and command execution

**2. Reinforcement Learning Controller**
- Custom Gymnasium wrapper for RL compatibility
- Stable Baselines 3 (PPO algorithm)
- Hyperparameter optimization across team
- Target accuracy: **±1mm positional control**

**3. PID Controller**
- Classical control system (3-axis PID)
- Gain tuning for optimal performance
- Comparative benchmarking vs. RL approach
- Target accuracy: **±1mm positional control**

**4. CV-Robotics Integration**
- Pixel-to-robot coordinate transformation
- Automated multi-plant inoculation workflow
- End-to-end pipeline from image to robotic action

## 📊 Key Results

### Computer Vision Performance
- **Root Segmentation F1 Score:** 0.856 (validation set)
- **Kaggle Public Leaderboard:** 5.12% sMAPE
- **Major Improvement:** Zone-based root assignment reduced sMAPE from 30.007% to 5.12%
- **Model Performance:** Effectively segments roots even in complex overlapping cases

### U-Net Model Specifications
- **Best Validation Loss:** 0.002723
- **Best Validation F1:** 0.8564
- **Learning Rate:** 1e-4
- **Batch Size:** 32
- **Epochs:** 100

### Robotic Control Performance

**Reinforcement Learning Controller:**
- **Accuracy:** ±1mm positional precision (5/5 zones successful)
- **Average Time:** 6.388 seconds per target
- **Average Steps:** 49.6 steps per movement

**Best Individual RL Model Hyperparameters:**
- Learning Rate: 0.0001
- Batch Size: 32
- Steps: 2048
- Epochs: 15
- Gamma: 0.98
- Policy: MlpPolicy
- Clip Range: 0.2
- Value Coefficient: 0.5

**Group RL Model Hyperparameters:**
- Learning Rate: 0.0001
- Batch Size: 64
- Steps: 2048
- Epochs: 50
- Gamma: 0.8
- Policy: MlpPolicy
- Clip Range: 0.1
- Value Coefficient: 0.75

**PID Controller:**
- **Accuracy:** ±1mm positional precision (5/5 zones successful)
- **Average Time:** 7.313 seconds per target
- **Average Steps:** 62.0 steps per movement
- **Best Performing Gains:**
  - KP: 20.0
  - KI: 0.1
  - KD: 0.005

### Controller Comparison
- **RL Advantage:** ~13% faster than PID (6.4s vs 7.3s average)
- **Both Achieve:** 100% success rate with ±1mm accuracy across all zones
- **PID Tuning Impact:** Increasing KP from 10 to 20 improved speed by 30-40%

## 🛠️ Technologies Used

### Computer Vision
- **Traditional CV:** OpenCV, scikit-image (morphological operations, edge detection)
- **Deep Learning:** TensorFlow/Keras, U-Net architecture
- **Image Processing:** PIL, NumPy, scikit-image
- **Annotation:** LabKit (ImageJ plugin)
- **Competition:** Kaggle platform

### Robotics & Control
- **Simulation:** PyBullet, URDF models
- **RL Framework:** Stable Baselines 3, Gymnasium
- **Experiment Tracking:** Weights & Biases (WandB)
- **Control Systems:** Custom PID implementation
- **Hardware Target:** Opentrons OT-2 liquid handling robot

### Development & Collaboration
- **Remote Training:** ClearML job queue
- **Version Control:** Git/GitHub
- **Documentation:** Jupyter Notebooks, Markdown
- **Team Coordination:** Hyperparameter search groups

## 🔄 Iterative Improvements

### 1. Root Segmentation Model Optimization
**Problem:** Initial model showed validation F1 of 0.77 with instability  
**Solution:** 
- Increased batch size from 16 to 32
- Extended training from 50 to 100 epochs  
- Set learning rate to 1e-4
**Result:** Improved validation F1 from 0.77 to 0.856 with stable convergence

### 2. Root-to-Plant Assignment Algorithm
**Problem:** Initial sMAPE of 30.007% due to incorrect root-plant matching  
**Solution:** Implemented zone-based segmentation dividing Petri dish into 5 vertical zones  
**Result:** Reduced sMAPE to 5.12% (83% improvement) on Kaggle public leaderboard

### 3. PID Controller Tuning
**Problem:** Slow response times with initial KP=10 gains  
**Solution:** Increased proportional gain (KP) from 10 to 20  
**Result:** 30-40% speed improvement while maintaining ±1mm accuracy

### 4. RL Hyperparameter Optimization
**Problem:** Finding optimal balance between stability and speed  
**Solution:** Team-based hyperparameter search testing multiple configurations  
**Result:** Individual model (batch 32, gamma 0.98) outperformed group model on speed

## 📐 Key Assumptions

1. **Geometric Assumptions:**
   - Petri dishes are square, ignoring corner curvatures
   - Petri dish edges parallel to image borders

2. **Spatial Assumptions:**
   - Roots can be segmented left-to-right within predefined vertical zones
   - Linear transformation adequately maps pixel coordinates to robot positions

3. **Image Quality Assumptions:**
   - Consistent lighting and background conditions across datasets
   - All input images contain valid, distinguishable roots

4. **Plant Layout Assumptions:**
   - Five plants per Petri dish (standard NPEC protocol)
   - Plants distributed relatively evenly across dish

## ⚠️ Known Limitations

1. **Computer Vision Limitations:**
   - Gaps in root predictions reduce segmentation quality and tip detection accuracy
   - Struggles with very small lateral roots (< 5 pixels width)
   - Complex root overlaps remain challenging to fully disambiguate
   - Performance degrades under heavy condensation on Petri dish

2. **Robotics Limitations:**
   - Robot arm doesn't fully descend to Petri dish surface during inoculation
   - PID controller 13% slower than RL in real-time scenarios
   - Coordinate transformation assumes flat Petri dish surface

3. **Integration Limitations:**
   - Segmentation errors propagate to robotic targeting
   - No real-time feedback from physical robot to CV system
   - Simulation-to-real-world transfer not yet validated

## 🚀 Future Improvements

### Computer Vision Enhancements
- **Data Augmentation:** Synthetic root overlaps and condensation simulation
- **Advanced Architectures:** Mask R-CNN or DeepLabV3+ for instance segmentation
- **Multi-Model Ensemble:** Combine predictions from multiple segmentation models
- **Root Tip Refinement:** Dedicated model for precise tip localization

### Robotics Enhancements
- **Hybrid Controller:** Combine RL speed with PID stability
- **Adaptive Control:** Real-time adjustment based on CV confidence scores
- **Depth Sensing:** Integrate Z-axis feedback for proper descent
- **Multi-Zone Parallelization:** Simultaneous inoculation planning

### Integration Improvements
- **Error Propagation Analysis:** Quantify CV errors impact on robotic accuracy
- **Closed-Loop Feedback:** Computer vision validation post-inoculation
- **Real Hardware Validation:** Test on physical Opentrons OT-2 system

## 📁 Repository Structure
```
├── README.md
├── requirements.txt
├── .gitignore
├── datalab_tasks/
│   ├── task2/
│   │   └── task_2.ipynb                    # Petri dish detection
│   ├── task3/
│   │   └── task_3.ipynb                    # Plant instance segmentation
│   ├── task5/
│   │   ├── task5_training.ipynb            # U-Net training
│   │   ├── task5_inference.ipynb           # U-Net inference
│   │   └── michongoddijn_231849_unet_model.h5
│   ├── task8/
│   │   └── task_8.ipynb                    # Kaggle competition pipeline
│   ├── task10/
│   │   └── ot2_gym_wrapper.py              # Gymnasium wrapper
│   ├── task11/
│   │   ├── base.py                         # RL training
│   │   └── test.py                         # RL testing
│   ├── task12/
│   │   └── pid_controller.py               # PID implementation
│   └── task13/
│       ├── pid_controller_pipeline.py      # PID + CV integration
│       └── rl_controller_pipeline.py       # RL + CV integration
└── visualizations/
    └── block b presentation.pdf
```

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Computer Vision Pipeline

**1. Preprocessing:**
```python
# Petri dish detection
jupyter notebook datalab_tasks/task2/task_2.ipynb

# Plant instance segmentation
jupyter notebook datalab_tasks/task3/task_3.ipynb
```

**2. Deep Learning Segmentation:**
```python
# Training
jupyter notebook datalab_tasks/task5/task5_training.ipynb

# Inference
jupyter notebook datalab_tasks/task5/task5_inference.ipynb
```

**3. Full Pipeline (Kaggle Competition):**
```python
jupyter notebook datalab_tasks/task8/task_8.ipynb
```

### Running the Robotic Controllers

**Simulation Environment:**
```python
python datalab_tasks/task9/task9.ipynb
```

**Reinforcement Learning:**
```python
# Training
python datalab_tasks/task11/base.py

# Testing
python datalab_tasks/task11/test.py
```

**PID Controller:**
```python
python datalab_tasks/task12/pid_controller.py
```

**Integrated System:**
```python
# RL + CV integration
python datalab_tasks/task13/rl_controller_pipeline.py

# PID + CV integration
python datalab_tasks/task13/pid_controller_pipeline.py
```

## 🔬 Technical Approach

### Computer Vision Pipeline

**Phase 1: Traditional CV (Tasks 1-3)**
- Manual annotation of 5 Petri dish images (shoot, seed, root classes)
- Peer review system for annotation quality
- Automated Petri dish detection using morphological operations
- Instance segmentation for individual plant isolation

**Phase 2: Deep Learning (Tasks 4-5)**
- Dataset preparation with image patching
- U-Net architecture for semantic segmentation
- Training on combined Y2B_23 and Y2B_24 datasets
- Validation F1 score target: **0.8+**

**Phase 3: Measurement Pipeline (Tasks 6-8)**
- Root instance segmentation from binary masks
- Skeletonization for RSA extraction
- Primary root identification and length measurement
- Kaggle competition optimization (sMAPE metric)

### Robotics & Control Systems

**Phase 1: Environment Setup (Task 9)**
- PyBullet simulation configuration
- Opentrons OT-2 digital twin
- Working envelope determination (8-corner cube)
- Command/observation interface

**Phase 2: RL Development (Tasks 10-11)**
- Custom Gymnasium wrapper implementation
- Action space, observation space, and reward function design
- Stable Baselines 3 PPO algorithm training
- Hyperparameter search (team collaboration)
- Multi-day training on remote GPU queue

**Phase 3: Classical Control (Task 12)**
- 3-axis PID controller implementation
- Gain tuning (Kp, Ki, Kd parameters)
- Performance comparison with RL approach

**Phase 4: Integration (Tasks 13-14)**
- Pixel-to-robot coordinate transformation
- CV pipeline output → controller input
- Multi-plant automated inoculation
- Speed and accuracy benchmarking

## 📈 Project Development Process

### Week 1-2: Computer Vision Fundamentals
- Image annotation with LabKit (5 images per student)
- Peer review of segmentation masks
- Traditional CV techniques (thresholding, morphological operations)
- Petri dish and plant detection

### Week 3: Deep Learning Segmentation
- Dataset preparation and augmentation
- U-Net model training
- **Kaggle competition launch** (Week 3 Wednesday)
- Root measurement pipeline development

### Week 4-5: Robotics Introduction
- Simulation environment setup
- Reinforcement learning fundamentals
- Gymnasium wrapper creation
- RL training initialization (multi-day jobs)

### Week 6-7: Controller Development
- PID controller implementation
- Hyperparameter optimization
- CV-robotics integration
- Performance benchmarking

### Week 8: Final Integration & Presentation
- **Kaggle competition deadline** (Monday 13:00)
- Final pipeline testing
- **Client presentation** (Wednesday)

## 🏆 Achievements

✅ Developed **complete CV pipeline** from raw images to root measurements  
✅ Achieved **F1 > 0.80** on root segmentation validation set  
✅ Competed on **Kaggle leaderboard** with sMAPE-optimized predictions  
✅ Trained **reinforcement learning agent** for robotic control (±1mm accuracy)  
✅ Implemented **PID controller** with tuned gains (±1mm accuracy)  
✅ Created **end-to-end automation** combining CV and robotics  
✅ Conducted **peer review** ensuring annotation quality  
✅ Presented **integrated solution** to NPEC client  

## 🌱 Real-World Impact

This system enables NPEC to:
- **Automate phenotyping** of 10,000+ seedlings with minimal human intervention
- **Accelerate research** on plant-microbe interactions and disease resistance
- **Improve precision** in root trait measurement and inoculation
- **Scale experiments** previously limited by manual analysis bottlenecks
- **Advance agriculture** through data-driven plant breeding and crop improvement

## 🎓 Learning Outcomes

Through this project, I developed expertise in:

**Computer Vision:**
- Traditional CV techniques (edge detection, morphological operations, contour analysis)
- Deep learning for image segmentation (U-Net architecture)
- Dataset preparation, augmentation, and validation strategies
- Root system architecture extraction algorithms
- Evaluation metrics (F1 score, sMAPE)

**Robotics & Control:**
- Robotic simulation with PyBullet
- Reinforcement learning (PPO algorithm, Stable Baselines 3)
- Custom Gymnasium environment creation
- PID control theory and implementation
- Working envelope analysis and coordinate systems

**Integration & Optimization:**
- Pixel-to-robot coordinate transformation
- Pipeline integration (CV → control system)
- Performance benchmarking methodologies
- Hyperparameter optimization strategies
- Remote training with job queues (ClearML)

**Project Management:**
- Team-based hyperparameter search coordination
- Kaggle competition strategy and submission
- Client presentation and requirement gathering
- Peer review and quality assurance processes

## 👤 Author

**Michon Goddijn**  
Data Science & AI Student | Breda University of Applied Sciences  
[LinkedIn](www.linkedin.com/in/michongoddijn) | [Portfolio](https://michongoddijn.com) | [Email](mailto:michon.goddijn@icloud.com)

**Supervised by:** Dr. Alican Noyan (Computer Vision), MSc. Dean van Aswegen (Robotics & RL)

## 🙏 Acknowledgments

- **Netherlands Plant Eco-phenotyping Centre (NPEC)** - Project client and domain expertise
- **Faculty Advisors** - Dr. Alican Noyan, MSc. Dean van Aswegen, BSc. Jason Harty
- **Hyperparameter Search Team** - Collaborative RL optimization
- **Peer Reviewers** - Quality assurance for image annotations
- **BUas IT Services** - Remote training infrastructure (ClearML)

## 📄 License

This project was completed as part of academic coursework at Breda University of Applied Sciences in collaboration with NPEC.

---

*Year 2, Block B - AI Scientist: Computer Vision & Robotics | 2024-2025*

**Tags:** `computer-vision` `deep-learning` `u-net` `reinforcement-learning` `robotics` `pid-control` `plant-phenotyping` `image-segmentation` `opentrons` `stable-baselines3` `pytorch` `kaggle`
