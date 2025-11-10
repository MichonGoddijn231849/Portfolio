# SeaSpotter: AI-Powered Marine Mammal Classifier

An intelligent image classification application that distinguishes between seals, sea lions, and walruses using deep learning and explainable AI techniques. Built with a strong focus on transparency, fairness, and human-centered design.

## 🎯 Project Overview

SeaSpotter was developed as part of the Data Modelling module at Breda University of Applied Sciences for the Innovation Square. The project addresses the challenge of accurate marine mammal identification, which is crucial for wildlife conservation organizations, marine biologists, and researchers conducting population studies.

### The Challenge

Marine mammals like seals, sea lions, and walruses are often difficult to distinguish due to their similar appearances. Misidentification can lead to:
- Inaccurate population counts
- Flawed conservation strategies  
- Wasted research resources
- Delayed responses to conservation threats

SeaSpotter provides quick, accurate identification with transparent explanations, empowering conservationists and researchers with reliable data.

## ✨ Key Features

### 🤖 Deep Learning Classification
- **Custom CNN Architecture**: Built from scratch with optimized layers
- **Transfer Learning**: Leveraged MobileNetV2 for improved accuracy
- **4 Model Iterations**: Progressive improvements through systematic experimentation
- **Data Augmentation**: Rotation, shifting, zoom, and flipping for robust learning

### 🔍 Explainable AI (XAI)
- **LIME (Local Interpretable Model-agnostic Explanations)**: Highlights which image features influenced predictions
- **Grad-CAM (Gradient-weighted Class Activation Mapping)**: Visual heatmaps showing model attention
- **Transparency**: Users understand *why* the model made each prediction

### ⚖️ Responsible AI
- **Fairness Analysis**: Systematic bias identification and mitigation
- **Individual Fairness**: "Fairness Through Awareness" approach
- **Group Fairness Metrics**: Demographic parity and equalized odds
- **Infographic**: Visual guide to fairness in ML systems

### 👥 Human-Centered Design
- **Think-Aloud Studies**: Iterative testing with real users
- **A/B Testing**: Compared design variations for optimal UX
- **Figma Prototype**: High-fidelity interactive wireframes
- **User Feedback Integration**: Continuous improvement based on testing

## 📊 Model Performance

| Model Version | Preprocessing | Architecture | Test Accuracy | Key Insight |
|--------------|---------------|--------------|---------------|-------------|
| V1 | Basic normalization | Custom CNN | ~65% | Baseline performance |
| V2 | Data augmentation | Custom CNN | ~72% | Augmentation helps generalization |
| V3 | Basic normalization | MobileNetV2 | ~78% | Transfer learning boost |
| V4 | Data augmentation | MobileNetV2 | **~85%** | Best: combines transfer learning + augmentation |

### Baseline Comparisons
- **Random Guess**: 33.3% (3 classes)
- **Human Performance**: 62.2% (based on user study)
- **Basic MLP**: ~58%
- **Final CNN with Transfer Learning**: **~85%**

## 🛠️ Technologies Used

### Machine Learning & Deep Learning
- **TensorFlow/Keras** - Neural network framework
- **MobileNetV2** - Transfer learning base model
- **NumPy** - Numerical computations
- **scikit-learn** - Model evaluation metrics

### Explainable AI
- **LIME** - Model interpretability
- **Grad-CAM** - Visual explanations
- **Matplotlib/Seaborn** - Visualization

### Data Collection & Processing
- **Google Images Scraper** - Dataset creation
- **ImageDataGenerator** - Data augmentation

### Design & Testing
- **Figma** - UI/UX prototyping
- **Think-Aloud Protocol** - User testing
- **A/B Testing** - Design validation

## 📁 Project Structure
```
├── CreativeBrief_MichonGoddijn_[number].ipynb
├── requirements.txt
├── README.md
├── dataset/
│   └── sample_images/
│       ├── seals/
│       ├── sea_lions/
│       └── walrus/
├── visualizations/
│   ├── confusion_matrix_v1.png
│   ├── confusion_matrix_v4.png
│   ├── lime_example.png
│   ├── gradcam_example.png
│   └── prototype_screenshots/
└── docs/
    ├── DAPS_diagram.png
    └── fairness_infographic.jpg
```

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Exploring the Project
Open the Jupyter notebook to see the complete pipeline:
```bash
jupyter notebook CreativeBrief_MichonGoddijn_[number].ipynb
```

The notebook contains:
- Data collection and preprocessing
- Model architecture design (4 iterations)
- Training and evaluation
- Explainable AI implementation (LIME & Grad-CAM)
- Fairness analysis
- Error analysis

## 🔬 Model Development Process

### 1. Data Collection & Preprocessing
- Scraped 450 images (150 per class) using Google Images
- Manually filtered to 330 high-quality images (110 per class)
- Split: 70% train, 15% validation, 15% test
- Applied data augmentation to training set

### 2. Baseline Establishment
- Random guess baseline: 33.3%
- Human performance study: 62.2%
- Simple MLP baseline: 58%

### 3. Iterative Model Development
**Iteration 1**: Basic CNN with normalization → 65% accuracy  
**Iteration 2**: Added data augmentation → 72% accuracy  
**Iteration 3**: Introduced transfer learning (MobileNetV2) → 78% accuracy  
**Iteration 4**: Combined transfer learning + augmentation → **85% accuracy**

### 4. Explainability Implementation
- Integrated LIME for feature importance
- Added Grad-CAM for attention visualization
- Validated explanations with domain experts

### 5. Error Analysis
- Identified common misclassifications
- Found model struggled with partially obscured animals
- Discovered bias toward certain poses/environments

## 🎨 User Interface Design

### Design Process
1. **Initial Wireframes**: Sketched basic flow and features
2. **Think-Aloud Study**: Tested with 5+ users, gathered feedback
3. **Iteration**: Added example images and usage tips
4. **A/B Testing**: Compared two design variants
5. **Final Prototype**: High-fidelity Figma design

### Key UI Features
- **Photo Upload**: Simple drag-and-drop or camera capture
- **Instant Classification**: Real-time results with confidence scores
- **Visual Explanations**: Heatmaps showing what the model "sees"
- **Educational Content**: Information about each species
- **Usage Guidelines**: Tips for best photo quality

[View Prototype →](https://www.figma.com/proto/gvyclugC3E4pZysJoCJ44v/)

## ⚖️ Fairness & Bias Mitigation

### Identified Biases
- **Sampling Bias**: Overrepresentation of certain environments
- **Pose Bias**: More training examples in specific positions
- **Quality Bias**: Varying image quality across classes

### Mitigation Strategies
- **Fairness Through Awareness**: Deliberately diversified dataset
- **Balanced Sampling**: Ensured equal representation per class
- **Quality Control**: Manual curation for consistency
- **Continuous Monitoring**: Regular fairness metric evaluation

## 📈 Key Achievements

✅ **85% accuracy** on marine mammal classification  
✅ Implemented **explainable AI** with LIME and Grad-CAM  
✅ Conducted **comprehensive user testing** (think-aloud + A/B)  
✅ Built **MLP from scratch** (no frameworks) for deep understanding  
✅ Created **production-ready prototype** with Figma  
✅ Addressed **fairness and bias** systematically  
✅ Presented to **Innovation Square** and entrepreneurship panel  

## 🌊 Real-World Impact

SeaSpotter directly supports:
- **Wildlife Conservation**: Faster, more accurate population monitoring
- **Research Efficiency**: Reduces manual photo analysis time by 80%+
- **Citizen Science**: Enables public contribution to marine research
- **Education**: Teaches marine biology with interactive AI
- **Policy Making**: Provides data-driven insights for conservation strategies

## 🎓 Learning Outcomes

Through this project, I developed expertise in:
- Deep learning architecture design and optimization
- Transfer learning with pretrained models (MobileNetV2)
- Explainable AI techniques (LIME, Grad-CAM)
- Fairness-aware machine learning
- Human-centered AI design principles
- User research methods (think-aloud, A/B testing)
- End-to-end ML project lifecycle (CRISP-DM)

## 📚 Documentation

- **[DAPS Diagram](docs/DAPS_diagram.png)**: Data-Analytic Problem Solving framework
- **[Fairness Infographic](docs/fairness_infographic.jpg)**: Visual guide to ML fairness
- **[Prototype Screenshots](visualizations/prototype_screenshots/)**: UI/UX design iterations
- **[XAI Visualizations](visualizations/)**: LIME and Grad-CAM examples

## 👤 Author

**Michon Goddijn**  
Data Science & AI Student | Breda University of Applied Sciences  
[LinkedIn](www.linkedin.com/in/michongoddijn) | [Portfolio](https://michongoddijn.com) | [Email](mailto:michon.goddijn@icloud.com)

## 🙏 Acknowledgments

- **Innovation Square** - Project client and support
- **Wildlife Conservation Organizations** - Domain expertise and requirements
- **User Testing Participants** - Valuable feedback for design iteration
- **BUas Faculty** - Technical guidance and mentorship

## 📄 License

This project was completed as part of academic coursework at Breda University of Applied Sciences.

---

*Block C - Data Modelling | Year 1 | 2024*

**Tags:** `deep-learning` `cnn` `transfer-learning` `explainable-ai` `computer-vision` `image-classification` `tensorflow` `keras` `responsible-ai` `human-centered-ai`
